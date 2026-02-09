"""Tests for custom exception hierarchy."""

from construtor.config.exceptions import (
    ConfigurationError,
    InputValidationError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    OutputParsingError,
    PineconeError,
    PipelineError,
)


class TestPipelineError:
    """Test base PipelineError class."""

    def test_pipeline_error_with_message_only(self):
        """Test PipelineError with just a message."""
        error = PipelineError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.question_id is None
        assert error.foco is None
        assert error.modelo is None
        assert error.rodada is None

    def test_pipeline_error_with_full_context(self):
        """Test PipelineError with message and full context."""
        error = PipelineError(
            "API failed",
            question_id=123,
            foco="Anatomia",
            modelo="gpt-4o",
            rodada=2,
        )
        assert error.question_id == 123
        assert error.foco == "Anatomia"
        assert error.modelo == "gpt-4o"
        assert error.rodada == 2

    def test_pipeline_error_with_partial_context(self):
        """Test PipelineError with only some context parameters."""
        error = PipelineError("Partial context", question_id=456, modelo="claude-sonnet-4-5")
        assert error.question_id == 456
        assert error.modelo == "claude-sonnet-4-5"
        assert error.foco is None
        assert error.rodada is None

    def test_pipeline_error_str_includes_context(self):
        """Test that __str__ includes context in output."""
        error = PipelineError(
            "Processing failed",
            question_id=789,
            foco="Fisiologia",
            modelo="gpt-4o",
        )
        error_str = str(error)
        assert "Processing failed" in error_str
        assert "question_id=789" in error_str
        assert "foco=Fisiologia" in error_str
        assert "modelo=gpt-4o" in error_str
        assert " | " in error_str  # Verify separator

    def test_pipeline_error_str_without_context(self):
        """Test that __str__ works without context."""
        error = PipelineError("Simple error")
        assert str(error) == "Simple error"

    def test_pipeline_error_repr(self):
        """Test that __repr__ provides complete debugging info."""
        error = PipelineError(
            "Debug error",
            question_id=101,
            foco="Anatomia",
        )
        repr_str = repr(error)
        assert "PipelineError" in repr_str
        assert "message='Debug error'" in repr_str
        assert "question_id=101" in repr_str
        assert "foco='Anatomia'" in repr_str
        assert "modelo=None" in repr_str
        assert "rodada=None" in repr_str


class TestLLMProviderError:
    """Test LLMProviderError class."""

    def test_inherits_from_pipeline_error(self):
        """Test that LLMProviderError inherits from PipelineError."""
        error = LLMProviderError("Provider failed")
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_llm_provider_error_with_context(self):
        """Test LLMProviderError with context."""
        error = LLMProviderError("API error", modelo="gpt-4o", question_id=123)
        assert str(error) == "API error | question_id=123 | modelo=gpt-4o"
        assert error.modelo == "gpt-4o"
        assert error.question_id == 123

    def test_llm_provider_error_repr(self):
        """Test LLMProviderError __repr__."""
        error = LLMProviderError("Provider error", modelo="claude-sonnet-4-5")
        repr_str = repr(error)
        assert "LLMProviderError" in repr_str
        assert "Provider error" in repr_str


class TestLLMRateLimitError:
    """Test LLMRateLimitError class."""

    def test_inherits_from_llm_provider_error(self):
        """Test that LLMRateLimitError inherits from LLMProviderError."""
        error = LLMRateLimitError("Rate limit exceeded")
        assert isinstance(error, LLMProviderError)
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_rate_limit_error_with_context(self):
        """Test LLMRateLimitError with rate limit context."""
        error = LLMRateLimitError(
            "Rate limit hit",
            modelo="claude-sonnet-4-5",
            rodada=3,
            question_id=456,
        )
        error_str = str(error)
        assert "Rate limit hit" in error_str
        assert "question_id=456" in error_str
        assert "modelo=claude-sonnet-4-5" in error_str
        assert "rodada=3" in error_str

    def test_rate_limit_error_repr(self):
        """Test LLMRateLimitError __repr__."""
        error = LLMRateLimitError("Rate limit", modelo="gpt-4o", rodada=2)
        repr_str = repr(error)
        assert "LLMRateLimitError" in repr_str


class TestLLMTimeoutError:
    """Test LLMTimeoutError class."""

    def test_inherits_from_llm_provider_error(self):
        """Test that LLMTimeoutError inherits from LLMProviderError."""
        error = LLMTimeoutError("Request timed out")
        assert isinstance(error, LLMProviderError)
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_timeout_error_with_context(self):
        """Test LLMTimeoutError with timeout context."""
        error = LLMTimeoutError(
            "Timeout after 30s",
            modelo="gpt-4o",
            question_id=789,
            rodada=1,
        )
        error_str = str(error)
        assert "Timeout after 30s" in error_str
        assert "question_id=789" in error_str
        assert "modelo=gpt-4o" in error_str
        assert "rodada=1" in error_str


class TestOutputParsingError:
    """Test OutputParsingError class."""

    def test_inherits_from_pipeline_error(self):
        """Test that OutputParsingError inherits from PipelineError."""
        error = OutputParsingError("Failed to parse JSON")
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)
        # Should NOT inherit from LLMProviderError
        assert not isinstance(error, LLMProviderError)

    def test_parsing_error_with_context(self):
        """Test OutputParsingError with parsing context."""
        error = OutputParsingError(
            "Invalid JSON",
            modelo="claude-sonnet-4-5",
            question_id=101,
            rodada=2,
        )
        error_str = str(error)
        assert "Invalid JSON" in error_str
        assert "question_id=101" in error_str
        assert "modelo=claude-sonnet-4-5" in error_str
        assert "rodada=2" in error_str


class TestInputValidationError:
    """Test InputValidationError class."""

    def test_inherits_from_pipeline_error(self):
        """Test that InputValidationError inherits from PipelineError."""
        error = InputValidationError("Validation failed")
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)
        # Should NOT inherit from LLMProviderError
        assert not isinstance(error, LLMProviderError)

    def test_input_validation_error_with_context(self):
        """Test InputValidationError with validation context."""
        error = InputValidationError(
            "Missing required column 'periodo'",
            foco="Anatomia",
        )
        error_str = str(error)
        assert "Missing required column 'periodo'" in error_str
        assert "foco=Anatomia" in error_str

    def test_input_validation_error_without_context(self):
        """Test InputValidationError without context."""
        error = InputValidationError("Invalid input data")
        assert str(error) == "Invalid input data"


class TestPineconeError:
    """Test PineconeError class."""

    def test_inherits_from_pipeline_error(self):
        """Test that PineconeError inherits from PipelineError."""
        error = PineconeError("Pinecone query failed")
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)
        # Should NOT inherit from LLMProviderError
        assert not isinstance(error, LLMProviderError)

    def test_pinecone_error_with_context(self):
        """Test PineconeError with query context."""
        error = PineconeError(
            "Pinecone timeout",
            foco="Fisiologia",
            question_id=202,
        )
        error_str = str(error)
        assert "Pinecone timeout" in error_str
        assert "question_id=202" in error_str
        assert "foco=Fisiologia" in error_str

    def test_pinecone_error_repr(self):
        """Test PineconeError __repr__."""
        error = PineconeError("Query failed", foco="Anatomia")
        repr_str = repr(error)
        assert "PineconeError" in repr_str
        assert "Query failed" in repr_str


class TestConfigurationError:
    """Test ConfigurationError class."""

    def test_inherits_from_pipeline_error(self):
        """Test that ConfigurationError inherits from PipelineError."""
        error = ConfigurationError("Missing API key")
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)
        # Should NOT inherit from LLMProviderError
        assert not isinstance(error, LLMProviderError)

    def test_configuration_error_with_message(self):
        """Test ConfigurationError with custom message."""
        error = ConfigurationError("API key 'OPENAI_API_KEY' não encontrada. Verifique .env")
        assert "OPENAI_API_KEY" in str(error)

    def test_configuration_error_with_context_kwargs(self):
        """Test ConfigurationError with keyword-only context args."""
        error = ConfigurationError(
            "Config invalid",
            question_id=42,
            foco="Anatomia",
        )
        assert error.question_id == 42
        assert error.foco == "Anatomia"
        error_str = str(error)
        assert "question_id=42" in error_str
        assert "foco=Anatomia" in error_str

    def test_configuration_error_catchable_as_pipeline_error(self):
        """Test that ConfigurationError can be caught as PipelineError."""
        try:
            raise ConfigurationError("Bad config")
        except PipelineError as e:
            assert isinstance(e, ConfigurationError)
            assert str(e) == "Bad config"


class TestExceptionHierarchy:
    """Test the complete exception hierarchy relationships."""

    def test_exception_hierarchy_structure(self):
        """Test that the exception hierarchy is correctly structured."""
        # PipelineError is base
        assert issubclass(PipelineError, Exception)

        # LLMProviderError inherits from PipelineError
        assert issubclass(LLMProviderError, PipelineError)

        # LLMRateLimitError inherits from LLMProviderError
        assert issubclass(LLMRateLimitError, LLMProviderError)
        assert issubclass(LLMRateLimitError, PipelineError)

        # LLMTimeoutError inherits from LLMProviderError
        assert issubclass(LLMTimeoutError, LLMProviderError)
        assert issubclass(LLMTimeoutError, PipelineError)

        # OutputParsingError inherits from PipelineError (not LLMProviderError)
        assert issubclass(OutputParsingError, PipelineError)
        assert not issubclass(OutputParsingError, LLMProviderError)

        # InputValidationError inherits from PipelineError (not LLMProviderError)
        assert issubclass(InputValidationError, PipelineError)
        assert not issubclass(InputValidationError, LLMProviderError)

        # PineconeError inherits from PipelineError (not LLMProviderError)
        assert issubclass(PineconeError, PipelineError)
        assert not issubclass(PineconeError, LLMProviderError)

        # ConfigurationError inherits from PipelineError (not LLMProviderError)
        assert issubclass(ConfigurationError, PipelineError)
        assert not issubclass(ConfigurationError, LLMProviderError)

    def test_catching_exceptions_by_hierarchy_llm_provider(self):
        """Test that LLM exceptions can be caught at LLMProviderError level."""
        # Catching LLMProviderError catches rate limits
        try:
            raise LLMRateLimitError("Rate limit", modelo="gpt-4o", rodada=1)
        except LLMProviderError as e:
            assert isinstance(e, LLMRateLimitError)
            assert e.modelo == "gpt-4o"
            assert e.rodada == 1

        # Catching LLMProviderError catches timeouts
        try:
            raise LLMTimeoutError("Timeout", modelo="claude-sonnet-4-5")
        except LLMProviderError as e:
            assert isinstance(e, LLMTimeoutError)
            assert e.modelo == "claude-sonnet-4-5"

    def test_catching_exceptions_by_hierarchy_pipeline(self):
        """Test that all exceptions can be caught at PipelineError level."""
        # Catching PipelineError catches OutputParsingError
        try:
            raise OutputParsingError("Parse failed", question_id=100)
        except PipelineError as e:
            assert isinstance(e, OutputParsingError)
            assert e.question_id == 100

        # Catching PipelineError catches InputValidationError
        try:
            raise InputValidationError("Validation failed", foco="Anatomia")
        except PipelineError as e:
            assert isinstance(e, InputValidationError)
            assert e.foco == "Anatomia"

        # Catching PipelineError catches PineconeError
        try:
            raise PineconeError("Pinecone failed", foco="Fisiologia")
        except PipelineError as e:
            assert isinstance(e, PineconeError)
            assert e.foco == "Fisiologia"

        # Catching PipelineError catches LLM errors
        try:
            raise LLMRateLimitError("Rate limit", modelo="gpt-4o")
        except PipelineError as e:
            assert isinstance(e, LLMRateLimitError)
            assert e.modelo == "gpt-4o"


class TestExceptionChaining:
    """Test exception chaining with 'raise from'."""

    def test_exception_chaining_preserves_cause(self):
        """Test that 'raise from' preserves the original exception."""
        original = ValueError("Original error")

        try:
            try:
                raise original
            except ValueError as e:
                raise LLMTimeoutError("Timeout occurred", modelo="gpt-4o", question_id=123) from e
        except LLMTimeoutError as caught:
            # Verify the new exception has correct context
            assert caught.modelo == "gpt-4o"
            assert caught.question_id == 123
            # Verify __cause__ is set correctly
            assert caught.__cause__ is original
            assert isinstance(caught.__cause__, ValueError)
            assert str(caught.__cause__) == "Original error"

    def test_exception_chaining_with_different_types(self):
        """Test exception chaining with different original exception types."""

        class CustomError(Exception):
            pass

        original = CustomError("Custom error")

        try:
            try:
                raise original
            except CustomError as e:
                raise OutputParsingError(
                    "Failed to parse", modelo="claude-sonnet-4-5", rodada=2
                ) from e
        except OutputParsingError as caught:
            assert caught.__cause__ is original
            assert isinstance(caught.__cause__, CustomError)


class TestExceptionContextEdgeCases:
    """Test edge cases for exception context."""

    def test_context_with_zero_values(self):
        """Test that zero values are included in __str__ output."""
        error = PipelineError("Error", question_id=0, rodada=0)
        error_str = str(error)
        # question_id=0 and rodada=0 should be included (0 is not None)
        assert "question_id=0" in error_str
        assert "rodada=0" in error_str

    def test_context_with_empty_string(self):
        """Test that empty strings are not included in __str__ output."""
        error = PipelineError("Error", foco="", modelo="")
        error_str = str(error)
        # Empty strings should not add parts (falsy check)
        assert error_str == "Error"

    def test_context_with_mixed_values(self):
        """Test context with mix of None, zero, empty, and valid values."""
        error = PipelineError(
            "Mixed context",
            question_id=0,  # Should include (0 is not None)
            foco=None,  # Should exclude
            modelo="gpt-4o",  # Should include
            rodada=None,  # Should exclude
        )
        error_str = str(error)
        assert "question_id=0" in error_str
        assert "foco" not in error_str
        assert "modelo=gpt-4o" in error_str
        assert "rodada" not in error_str or "rodada=None" not in error_str


class TestExceptionPublicAPI:
    """Test that all exceptions are properly exported."""

    def test_all_exceptions_in_all(self):
        """Test that __all__ includes all exception classes."""
        from construtor.config import exceptions

        expected_exports = [
            "PipelineError",
            "LLMProviderError",
            "LLMRateLimitError",
            "LLMTimeoutError",
            "OutputParsingError",
            "InputValidationError",
            "PineconeError",
            "ConfigurationError",
        ]

        assert hasattr(exceptions, "__all__")
        for export in expected_exports:
            assert export in exceptions.__all__
            assert hasattr(exceptions, export)
