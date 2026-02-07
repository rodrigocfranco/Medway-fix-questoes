"""Anthropic LLM provider implementation.

This module implements the LLMProvider Protocol for Anthropic's Claude API
using the official Anthropic Python SDK v0.79.0+.

Key features:
- Async API calls with AsyncAnthropic client
- Structured outputs via extra_headers with beta flag
- Manual JSON parsing to Pydantic models
- Accurate token counting and cost calculation
- Exponential backoff with jitter for rate limits
- Timeout handling with configurable limits
- Semaphore-controlled concurrency
- Custom exception hierarchy for error handling
"""

import asyncio
import json
import time
from asyncio import Semaphore
from typing import Any, ClassVar

from anthropic import AsyncAnthropic
from pydantic import BaseModel, ValidationError
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from construtor.config.exceptions import (
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    OutputParsingError,
)


class AnthropicProvider:
    """Anthropic LLM provider with async, retry, and cost tracking.

    This class implements the LLMProvider Protocol for Anthropic's Claude models.
    It provides a unified interface for text generation with automatic handling
    of rate limits, timeouts, and cost tracking.

    Features:
        - Structured outputs: Use response_model for Pydantic validation
        - Cost tracking: Accurate per-call cost calculation
        - Rate limit handling: Exponential backoff with jitter
        - Timeout handling: Configurable request timeouts
        - Concurrency control: Semaphore-limited API calls

    Example:
        ```python
        from asyncio import Semaphore
        from construtor.providers.anthropic_provider import AnthropicProvider
        from construtor.models import CriadorOutput

        semaphore = Semaphore(5)  # Max 5 concurrent calls
        provider = AnthropicProvider(
            api_key="sk-ant-...",
            semaphore=semaphore,
            timeout=30.0
        )

        # Simple text generation
        result = await provider.generate(
            prompt="Write a haiku about Python",
            model="claude-sonnet-4-5",
            temperature=0.7
        )
        print(result["content"])  # String
        print(f"Cost: ${result['cost']:.6f}")

        # Structured output with Pydantic
        result = await provider.generate(
            prompt="Generate a multiple choice question",
            model="claude-sonnet-4-5",
            temperature=0.7,
            response_model=CriadorOutput
        )
        question = result["content"]  # CriadorOutput instance
        print(question.enunciado)
        ```

    Attributes:
        client: AsyncAnthropic client for API calls
        semaphore: Semaphore for concurrency control
        timeout: Request timeout in seconds
    """

    # Anthropic pricing per 1 million tokens (as of February 2026)
    PRICING: ClassVar[dict[str, tuple[float, float]]] = {
        "claude-opus-4-6": (5.00, 25.00),  # input, output per 1M tokens
        "claude-sonnet-4-5": (3.00, 15.00),
        "claude-haiku-4-5": (1.00, 5.00),
        "claude-3-opus": (15.00, 75.00),  # Legacy Claude 3
        "claude-3-sonnet": (3.00, 15.00),  # Legacy Claude 3
        "claude-3-haiku": (0.25, 1.25),  # Legacy Claude 3
    }

    def __init__(
        self,
        api_key: str,
        semaphore: Semaphore,
        timeout: float = 30.0,
    ) -> None:
        """Initialize Anthropic provider.

        Args:
            api_key: Anthropic API key from environment or config
            semaphore: Shared semaphore for concurrency control
            timeout: Request timeout in seconds (default 30)
        """
        self.client = AsyncAnthropic(api_key=api_key)
        self.semaphore = semaphore
        self.timeout = timeout

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float,
        response_model: type[BaseModel] | None = None,
    ) -> dict[str, Any]:
        """Generate completion with retry, timeout, and cost tracking.

        Implements LLMProvider Protocol.

        Args:
            prompt: Text prompt to send to Anthropic
            model: Model ID (e.g., "claude-sonnet-4-5", "claude-haiku-4-5")
            temperature: Sampling temperature 0.0-1.0
            response_model: Optional Pydantic model for structured output

        Returns:
            dict with keys:
                - content: Generated text or parsed Pydantic object
                - tokens_used: Total tokens (input + output)
                - cost: USD cost for this call
                - latency: Seconds elapsed

        Raises:
            LLMProviderError: General API errors
            LLMRateLimitError: Rate limit exceeded (retried automatically)
            LLMTimeoutError: Request timeout
            OutputParsingError: Pydantic parsing failed
        """
        # Use semaphore to control concurrency
        async with self.semaphore:
            return await self._generate_with_retry(
                prompt,
                model,
                temperature,
                response_model,
            )

    @retry(
        stop=stop_after_attempt(3),  # Max 3 attempts
        wait=wait_exponential(
            multiplier=1,
            min=2,
            max=10,
        ),  # 2s, 4s, 8s with jitter
        retry=retry_if_exception_type(LLMRateLimitError),  # Only retry rate limits
        reraise=True,  # Re-raise exception after max attempts
    )
    async def _generate_with_retry(
        self,
        prompt: str,
        model: str,
        temperature: float,
        response_model: type[BaseModel] | None,
    ) -> dict[str, Any]:
        """Internal generate with automatic retry on rate limits.

        This method is decorated with @retry for exponential backoff.
        Only LLMRateLimitError triggers retry - other errors fail immediately.
        """
        start_time = time.time()

        try:
            # Wrap API call in timeout
            result = await asyncio.wait_for(
                self._call_api(prompt, model, temperature, response_model),
                timeout=self.timeout,
            )

            # Calculate latency
            latency = time.time() - start_time
            result["latency"] = round(latency, 3)

            return result

        except TimeoutError as e:
            msg = f"Request timeout: {model} exceeded {self.timeout}s limit"
            raise LLMTimeoutError(
                msg,
                context={"model": model, "timeout": self.timeout},
            ) from e

    async def _call_api(
        self,
        prompt: str,
        model: str,
        temperature: float,
        response_model: type[BaseModel] | None,
    ) -> dict[str, Any]:
        """Make the actual API call to Anthropic.

        Handles both regular text generation and structured output.
        """
        try:
            messages = [{"role": "user", "content": prompt}]

            # Add structured outputs header if response_model provided
            extra_headers = {}
            if response_model:
                extra_headers = {
                    "anthropic-beta": "structured-outputs-2025-11-13",
                }

            response = await self.client.messages.create(
                model=model,
                max_tokens=2048,  # Anthropic requires explicit max_tokens
                messages=messages,
                temperature=temperature,
                extra_headers=extra_headers if extra_headers else None,
            )

            # Extract content from response
            content_text = response.content[0].text

            # Parse to Pydantic if response_model provided
            if response_model:
                try:
                    data = json.loads(content_text)
                    content = response_model(**data)
                except (json.JSONDecodeError, ValidationError) as e:
                    msg = f"Failed to parse response to {response_model.__name__}: {e}"
                    raise OutputParsingError(
                        msg,
                        context={
                            "model": model,
                            "response_text": content_text[:200],
                            "expected_schema": response_model.__name__,
                        },
                    ) from e
            else:
                content = content_text

            # Extract token counts
            usage = response.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            total_tokens = input_tokens + output_tokens

            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens, model)

            return {
                "content": content,
                "tokens_used": total_tokens,
                "cost": cost,
                "latency": 0.0,  # Will be set by caller
            }

        except Exception as e:
            # Check if error message contains rate limit indicators
            error_str = str(e).lower()
            if "rate_limit" in error_str or "429" in error_str:
                msg = f"Anthropic rate limit exceeded: {e}"
                raise LLMRateLimitError(
                    msg,
                    context={"model": model, "provider": "anthropic"},
                ) from e

            # Check if it's already one of our custom exceptions
            if isinstance(e, (LLMRateLimitError, LLMTimeoutError, OutputParsingError)):
                raise

            # General API error
            msg = f"Anthropic API error: {e}"
            raise LLMProviderError(
                msg,
                context={"model": model, "provider": "anthropic", "error": str(e)},
            ) from e

    def _calculate_cost(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str,
    ) -> float:
        """Calculate USD cost for an API call.

        Uses pricing table from February 2026.

        Args:
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            model: Model ID

        Returns:
            float: Cost in USD with 6 decimal precision
        """
        # Get pricing for model (default to 0 if model not found)
        input_price_per_m, output_price_per_m = self.PRICING.get(
            model,
            (0.0, 0.0),
        )

        # Calculate cost per token type
        input_cost = (input_tokens / 1_000_000) * input_price_per_m
        output_cost = (output_tokens / 1_000_000) * output_price_per_m

        # Return total cost with 6 decimal precision
        return round(input_cost + output_cost, 6)
