"""LLM Provider Protocol definition.

This module defines the Protocol (interface) that all LLM providers must implement.
Using Python's Protocol (structural subtyping), providers don't need to explicitly
inherit from LLMProvider - they just need to implement the required methods.

The Protocol ensures:
- Type safety: Static type checkers verify providers implement the interface
- Flexibility: Providers can use different SDKs/implementations
- Testability: Easy to create mock providers for testing
- Documentation: Single source of truth for provider contract
"""

from asyncio import Semaphore
from typing import Protocol, runtime_checkable


@runtime_checkable
class LLMProvider(Protocol):
    """Protocol for LLM provider abstraction.

    Any class implementing this Protocol must have:
    - semaphore: Semaphore attribute for concurrency control
    - generate() method with the exact signature below

    The Protocol uses structural subtyping (duck typing with type checking).
    Classes implementing this Protocol don't need to inherit from it -
    they just need to have the required attributes and methods.

    Example:
        ```python
        class OpenAIProvider:
            def __init__(self, api_key: str, semaphore: Semaphore):
                self.client = AsyncOpenAI(api_key=api_key)
                self.semaphore = semaphore

            async def generate(
                self,
                prompt: str,
                model: str,
                temperature: float,
                response_model: type | None = None
            ) -> dict:
                async with self.semaphore:
                    # OpenAI-specific implementation
                    pass
        ```

    This class is runtime_checkable, meaning isinstance() checks work:
        ```python
        provider = OpenAIProvider(api_key, semaphore)
        assert isinstance(provider, LLMProvider)  # True!
        ```
    """

    semaphore: Semaphore
    """Semaphore for controlling concurrent API calls.

    All providers must accept a semaphore in their constructor and use it
    to limit concurrent API calls. This prevents rate limit abuse.

    Usage:
        ```python
        async with self.semaphore:
            response = await self.client.generate(...)
        ```
    """

    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float,
        response_model: type | None = None,
    ) -> dict:
        """Generate completion from LLM.

        This is the core method that all providers must implement.
        It handles making the API call, parsing the response, tracking
        tokens/cost, and managing errors.

        Args:
            prompt: The text prompt to send to the LLM.
                For multi-turn conversations, format as needed by the provider.
            model: Model ID to use for generation.
                Examples: "gpt-4o", "gpt-4o-mini", "claude-sonnet-4-5"
            temperature: Sampling temperature from 0.0 to 1.0.
                - 0.0: Deterministic, focused output
                - 0.7: Balanced creativity and coherence (recommended)
                - 1.0: Maximum creativity and randomness
            response_model: Optional Pydantic model for structured output.
                If provided, the response should be parsed to this model.
                If None, return raw text response.

        Returns:
            dict with the following keys:
                - content (str | BaseModel): Generated text OR parsed Pydantic object
                    - If response_model provided: Returns instance of that model
                    - If response_model is None: Returns raw text string
                - tokens_used (int): Total tokens consumed (input + output)
                - cost (float): USD cost for this call (6 decimal precision)
                - latency (float): Seconds elapsed for this call

        Raises:
            LLMProviderError: General API errors (auth, malformed request, etc.)
            LLMRateLimitError: Rate limit hit (will be retried with backoff)
            LLMTimeoutError: Request timeout exceeded
            OutputParsingError: JSON/Pydantic parsing failed

        Example:
            ```python
            # Simple text generation
            result = await provider.generate(
                prompt="Write a haiku about Python",
                model="gpt-4o",
                temperature=0.7
            )
            print(result["content"])  # String
            print(f"Cost: ${result['cost']:.6f}")
            print(f"Tokens: {result['tokens_used']}")

            # Structured output with Pydantic
            from construtor.models import CriadorOutput

            result = await provider.generate(
                prompt="Generate a multiple choice question about Python",
                model="gpt-4o",
                temperature=0.7,
                response_model=CriadorOutput
            )
            question = result["content"]  # CriadorOutput instance
            print(question.enunciado)
            print(question.alternativa_a)
            ```

        Implementation Requirements:
            1. MUST use `async with self.semaphore:` around all API calls
            2. MUST implement exponential backoff + jitter for rate limits
            3. MUST implement timeout handling (raise LLMTimeoutError)
            4. MUST calculate accurate token counts and costs
            5. MUST handle parsing errors (raise OutputParsingError)
            6. SHOULD measure latency from start to finish of API call
        """
        ...
