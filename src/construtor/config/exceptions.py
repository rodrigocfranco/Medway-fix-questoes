"""Custom exception hierarchy for the question builder pipeline.

This module defines a structured exception hierarchy that enables:
- Granular error handling at different pipeline stages
- Actionable error context for debugging and monitoring
- Distinction between retryable and non-retryable errors
- Clean separation of LLM provider errors vs parsing errors

Exception Hierarchy:
    Exception
    └── PipelineError (base for all pipeline errors)
        ├── LLMProviderError (general LLM API errors)
        │   ├── LLMRateLimitError (rate limit exceeded - retryable)
        │   └── LLMTimeoutError (request timeout - retryable)
        └── OutputParsingError (JSON/Pydantic parsing failed - retryable)
"""


class PipelineError(Exception):
    """Base exception for all pipeline errors.

    All custom exceptions in the question builder pipeline inherit from this class.
    Provides a context dict for storing additional debugging information.

    Attributes:
        context: Dict containing error context (model, question_id, etc.)
    """

    def __init__(self, message: str, context: dict | None = None):
        """Initialize PipelineError with message and optional context.

        Args:
            message: Human-readable error message
            context: Optional dict with error context (e.g., model, question_id)
        """
        super().__init__(message)
        self.context = context or {}


class LLMProviderError(PipelineError):
    """General LLM provider API errors.

    Raised for unexpected API errors that are not rate limits or timeouts.
    These errors are typically non-retryable and indicate a configuration
    issue or API problem.

    Examples:
        - Invalid API key
        - Malformed request
        - Unexpected API response format
    """


class LLMRateLimitError(LLMProviderError):
    """Rate limit exceeded error - retryable.

    Raised when the LLM provider returns a rate limit error (HTTP 429).
    These errors should be retried with exponential backoff + jitter.

    Context should include:
        - provider: Provider name (openai/anthropic)
        - model: Model ID that hit rate limit
        - retry_after: Seconds to wait (if provided by API)
    """


class LLMTimeoutError(LLMProviderError):
    """Request timeout error - retryable.

    Raised when an LLM API call exceeds the configured timeout.
    These errors should be retried, but may indicate a model issue
    if they persist.

    Context should include:
        - timeout: Configured timeout value
        - model: Model ID that timed out
        - elapsed: Actual elapsed time (if available)
    """


class OutputParsingError(PipelineError):
    """JSON or Pydantic parsing failed - retryable.

    Raised when the LLM output cannot be parsed to the expected format.
    These errors are retryable - the agent can regenerate with a better prompt.

    Context should include:
        - model: Model that generated invalid output
        - response_text: Raw response (truncated to 200 chars)
        - expected_schema: Expected Pydantic model name
    """
