"""OpenAI LLM provider implementation.

This module implements the LLMProvider Protocol for OpenAI's API using the
official OpenAI Python SDK v2.17.0+.

Key features:
- Async API calls with AsyncOpenAI client
- Structured outputs via beta.chat.completions.parse()
- Accurate token counting and cost calculation
- Exponential backoff with jitter for rate limits
- Timeout handling with configurable limits
- Semaphore-controlled concurrency
- Custom exception hierarchy for error handling
"""

import asyncio
import time
from asyncio import Semaphore
from typing import Any, ClassVar

from openai import AsyncOpenAI, RateLimitError
from pydantic import BaseModel
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
)


class OpenAIProvider:
    """OpenAI LLM provider with async, retry, and cost tracking.

    This class implements the LLMProvider Protocol for OpenAI's GPT models.
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
        from construtor.providers.openai_provider import OpenAIProvider
        from construtor.models import CriadorOutput

        semaphore = Semaphore(5)  # Max 5 concurrent calls
        provider = OpenAIProvider(
            api_key="sk-...",
            semaphore=semaphore,
            timeout=30.0
        )

        # Simple text generation
        result = await provider.generate(
            prompt="Write a haiku about Python",
            model="gpt-4o",
            temperature=0.7
        )
        print(result["content"])  # String
        print(f"Cost: ${result['cost']:.6f}")

        # Structured output with Pydantic
        result = await provider.generate(
            prompt="Generate a multiple choice question",
            model="gpt-4o",
            temperature=0.7,
            response_model=CriadorOutput
        )
        question = result["content"]  # CriadorOutput instance
        print(question.enunciado)
        ```

    Attributes:
        client: AsyncOpenAI client for API calls
        semaphore: Semaphore for concurrency control
        timeout: Request timeout in seconds
    """

    # OpenAI pricing per 1 million tokens (as of February 2026)
    PRICING: ClassVar[dict[str, tuple[float, float]]] = {
        "gpt-4o": (2.50, 10.00),  # input, output per 1M tokens
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4.5": (3.00, 12.00),
        "gpt-4": (3.00, 6.00),  # Legacy pricing
        "gpt-3.5-turbo": (0.50, 1.50),  # Legacy model
    }

    def __init__(
        self,
        api_key: str,
        semaphore: Semaphore,
        timeout: float = 30.0,
    ) -> None:
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key from environment or config
            semaphore: Shared semaphore for concurrency control
            timeout: Request timeout in seconds (default 30)
        """
        self.client = AsyncOpenAI(api_key=api_key)
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
            prompt: Text prompt to send to OpenAI
            model: Model ID (e.g., "gpt-4o", "gpt-4o-mini")
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
        except TimeoutError as e:
            msg = f"Request timeout: {model} exceeded {self.timeout}s limit"
            raise LLMTimeoutError(
                msg,
                modelo=model,
            ) from e
        else:
            # Calculate latency
            latency = time.time() - start_time
            result["latency"] = round(latency, 3)
            return result

    async def _call_api(
        self,
        prompt: str,
        model: str,
        temperature: float,
        response_model: type[BaseModel] | None,
    ) -> dict[str, Any]:
        """Make the actual API call to OpenAI.

        Handles both regular text generation and structured output.
        """
        try:
            messages = [{"role": "user", "content": prompt}]

            # Use structured output if response_model provided
            if response_model:
                response = await self.client.beta.chat.completions.parse(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    response_format=response_model,
                )
                content = response.choices[0].message.parsed
            else:
                response = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                content = response.choices[0].message.content

            # Extract token counts
            usage = response.usage
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            total_tokens = usage.total_tokens

            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens, model)

            return {
                "content": content,
                "tokens_used": total_tokens,
                "cost": cost,
                "latency": 0.0,  # Will be set by caller
            }

        except RateLimitError as e:
            # Rate limit - will be retried
            msg = f"OpenAI rate limit exceeded: {e}"
            raise LLMRateLimitError(
                f"{msg} (provider: openai)",
                modelo=model,
            ) from e

        except Exception as e:
            # Re-raise custom exceptions first to prevent misclassification
            if isinstance(e, (LLMRateLimitError, LLMTimeoutError)):
                raise

            # Check if error message contains rate limit indicators
            error_str = str(e).lower()
            if "rate limit" in error_str or "429" in error_str:
                msg = f"OpenAI rate limit exceeded: {e}"
                raise LLMRateLimitError(
                    f"{msg} (provider: openai)",
                    modelo=model,
                ) from e

            # General API error
            msg = f"OpenAI API error: {e}"
            raise LLMProviderError(
                f"{msg} (provider: openai, error: {e})",
                modelo=model,
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
