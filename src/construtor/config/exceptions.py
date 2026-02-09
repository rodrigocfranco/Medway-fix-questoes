"""Custom exception hierarchy for Construtor de Questões pipeline.

This module defines a structured exception hierarchy that enables:
- Granular error handling at different pipeline stages
- Actionable error context for debugging and monitoring (NFR13)
- Fault isolation: individual question failures don't stop the batch (NFR14)
- Distinction between retryable and non-retryable errors

Exception Hierarchy:
    Exception
    └── PipelineError (base for all pipeline errors)
        ├── LLMProviderError (general LLM API errors)
        │   ├── LLMRateLimitError (rate limit exceeded - retryable with backoff)
        │   └── LLMTimeoutError (request timeout - retryable with fallback)
        ├── OutputParsingError (JSON/Pydantic parsing failed - retryable)
        ├── InputValidationError (input validation failed - non-retryable)
        ├── PineconeError (RAG query failed - fallback to no-RAG)
        └── ConfigurationError (configuration error - non-retryable)

Usage Patterns:

✅ CORRECT - Specific exception with context:
    try:
        response = await llm_client.generate(prompt)
    except httpx.TimeoutError as e:
        raise LLMTimeoutError(
            "LLM request timed out",
            modelo="gpt-4o",
            question_id=123
        ) from e  # CRITICAL: 'from e' preserves stacktrace

✅ CORRECT - Catch at different hierarchy levels:
    try:
        process_question()
    except LLMRateLimitError:
        await asyncio.sleep(exponential_backoff())
        retry()
    except LLMProviderError:
        fallback_to_anthropic()
    except PipelineError as e:
        logger.error(f"Pipeline error: {e}")
        continue  # Fault isolation: continue to next question

❌ WRONG - Bare except (captures KeyboardInterrupt, SystemExit):
    try:
        process_question()
    except:  # NEVER DO THIS
        pass

❌ WRONG - Missing 'from' (loses stacktrace):
    except httpx.TimeoutError as e:
        raise LLMTimeoutError("Timeout")  # Missing 'from e'
"""


class PipelineError(Exception):
    """Base exception for all pipeline errors.

    All custom exceptions in the question builder pipeline inherit from this class.
    Provides optional context attributes for debugging and monitoring.

    Args:
        message: Human-readable error message
        question_id: Optional question ID where error occurred
        foco: Optional foco (topic) being processed
        modelo: Optional LLM model name
        rodada: Optional retry round number

    Attributes:
        question_id: Question ID where error occurred (if applicable)
        foco: Foco being processed (if applicable)
        modelo: LLM model name (if applicable)
        rodada: Retry round number (if applicable)

    Example:
        >>> raise PipelineError(
        ...     "Processing failed",
        ...     question_id=123,
        ...     foco="Anatomia"
        ... )
    """

    def __init__(
        self,
        message: str,
        *,
        question_id: int | None = None,
        foco: str | None = None,
        modelo: str | None = None,
        rodada: int | None = None,
    ) -> None:
        """Initialize PipelineError with message and optional context."""
        super().__init__(message)
        self.question_id = question_id
        self.foco = foco
        self.modelo = modelo
        self.rodada = rodada

    def __str__(self) -> str:
        """Include context in error message for clear logging.

        Returns:
            Error message with context appended (e.g., "Error | question_id=123 | foco=Anatomia")
        """
        parts = [super().__str__()]
        if self.question_id is not None:
            parts.append(f"question_id={self.question_id}")
        if self.foco:
            parts.append(f"foco={self.foco}")
        if self.modelo:
            parts.append(f"modelo={self.modelo}")
        if self.rodada is not None:
            parts.append(f"rodada={self.rodada}")
        return " | ".join(parts)

    def __repr__(self) -> str:
        """Full representation for debugging.

        Returns:
            Complete representation showing all attributes
        """
        return (
            f"{self.__class__.__name__}("
            f"message={super().__str__()!r}, "
            f"question_id={self.question_id!r}, "
            f"foco={self.foco!r}, "
            f"modelo={self.modelo!r}, "
            f"rodada={self.rodada!r})"
        )


class LLMProviderError(PipelineError):
    """General LLM provider API errors.

    Raised for unexpected API errors that are not rate limits or timeouts.
    These errors are typically non-retryable and indicate a configuration
    issue or API problem.

    Examples:
        - Invalid API key (401 Unauthorized)
        - Malformed request (400 Bad Request)
        - Unexpected API response format
        - Model not found (404)

    Context should include:
        - modelo: Model ID that caused the error
        - question_id: Question being processed (if applicable)
    """


class LLMRateLimitError(LLMProviderError):
    """Rate limit exceeded error - retryable with exponential backoff.

    Raised when the LLM provider returns a rate limit error (HTTP 429).
    These errors should be retried with exponential backoff + jitter:
    2s → 4s → 8s → 16s

    Context should include:
        - modelo: Model ID that hit rate limit
        - question_id: Question being processed
        - foco: Foco being processed

    Retry Strategy:
        1. Wait with exponential backoff (2^retry_count seconds)
        2. Add random jitter (0-1s) to prevent thundering herd
        3. Max 5 retries before marking as failed

    Example:
        >>> raise LLMRateLimitError(
        ...     "Rate limit exceeded",
        ...     modelo="gpt-4o",
        ...     rodada=2
        ... )
    """


class LLMTimeoutError(LLMProviderError):
    """Request timeout error - retryable with fallback.

    Raised when an LLM API call exceeds the configured timeout (typically 30s).
    These errors should be retried, but may indicate a model issue if persistent.

    Context should include:
        - modelo: Model ID that timed out
        - question_id: Question being processed
        - rodada: Current retry attempt

    Retry Strategy:
        1. Immediate retry (timeout may be transient)
        2. If fails 2+ times, fallback to different provider
        3. Max 3 retries before marking as failed

    Example:
        >>> raise LLMTimeoutError(
        ...     "Request timed out after 30s",
        ...     modelo="claude-sonnet-4-5",
        ...     question_id=456
        ... )
    """


class OutputParsingError(PipelineError):
    """JSON or Pydantic parsing failed - retryable with prompt modification.

    Raised when the LLM output cannot be parsed to the expected format.
    Common causes:
    - Invalid JSON syntax
    - Pydantic validation failure (missing fields, wrong types)
    - LLM returned text instead of JSON

    These errors are retryable - regenerate with modified prompt emphasizing
    JSON format and schema compliance.

    Context should include:
        - modelo: Model that generated invalid output
        - question_id: Question being processed
        - rodada: Current retry attempt

    Retry Strategy:
        1. Retry with enhanced prompt (emphasize JSON format)
        2. Max 2 retries before marking as failed
        3. Log raw response for debugging

    Example:
        >>> raise OutputParsingError(
        ...     "Failed to parse LLM output as Questao",
        ...     modelo="gpt-4o",
        ...     question_id=789
        ... )
    """


class InputValidationError(PipelineError):
    """Input validation failed - non-retryable, requires user intervention.

    Raised when input data fails validation checks such as:
    - Missing required columns in Excel files
    - Invalid values (e.g., invalid periodo)
    - Missing data in required fields
    - Schema mismatches between input and expected format

    These errors are non-retryable and require the user to fix the input data
    before rerunning the pipeline.

    Context should include:
        - foco: Foco being processed (if applicable)

    Handling:
        1. Stop processing immediately
        2. Report clear error message to user
        3. Indicate which file/row/column failed validation

    Example:
        >>> raise InputValidationError(
        ...     "Missing required column 'periodo' in Excel file",
        ...     foco="Anatomia"
        ... )
    """


class PineconeError(PipelineError):
    """Pinecone RAG query failed - fallback to no-RAG generation.

    Raised when Pinecone vector database query fails due to:
    - Connection timeout
    - API key invalid
    - Index not found
    - Query syntax error

    These errors should not stop question generation. Instead, fallback to
    generating questions without RAG context.

    Context should include:
        - question_id: Question being processed
        - foco: Foco being processed

    Handling:
        1. Log warning about RAG failure
        2. Continue question generation without RAG context
        3. Flag question with metadata: rag_used=False

    Example:
        >>> raise PineconeError(
        ...     "Pinecone query timeout after 10s",
        ...     foco="Anatomia",
        ...     question_id=101
        ... )
    """


class ConfigurationError(PipelineError):
    """Configuration error — non-retryable, requires .env correction.

    Raised when:
        - A required API key is missing or empty
        - The .env file is not found (and keys are not in the environment)
        - A configuration value is invalid

    Handling:
        1. Stop immediately (fail-fast)
        2. Display clear message indicating which configuration is missing
        3. Guide the user to check the .env file

    Example:
        >>> raise ConfigurationError(
        ...     "API key 'OPENAI_API_KEY' não encontrada. Verifique .env"
        ... )
    """


__all__ = [
    "ConfigurationError",
    "InputValidationError",
    "LLMProviderError",
    "LLMRateLimitError",
    "LLMTimeoutError",
    "OutputParsingError",
    "PineconeError",
    "PipelineError",
]
