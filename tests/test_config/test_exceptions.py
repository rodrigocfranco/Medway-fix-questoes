"""Tests for custom exception hierarchy."""

import pytest
from construtor.config.exceptions import (
    PipelineError,
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    OutputParsingError,
)


class TestPipelineError:
    """Test base PipelineError class."""

    def test_pipeline_error_with_message_only(self):
        """Test PipelineError with just a message."""
        error = PipelineError("Something went wrong")
        assert str(error) == "Something went wrong"
        assert error.context == {}

    def test_pipeline_error_with_context(self):
        """Test PipelineError with message and context."""
        context = {"question_id": "Q123", "modelo": "gpt-4o"}
        error = PipelineError("API failed", context=context)
        assert str(error) == "API failed"
        assert error.context == context
        assert error.context["question_id"] == "Q123"
        assert error.context["modelo"] == "gpt-4o"

    def test_pipeline_error_context_defaults_to_empty_dict(self):
        """Test that context defaults to empty dict if None."""
        error = PipelineError("Test error", context=None)
        assert error.context == {}


class TestLLMProviderError:
    """Test LLMProviderError class."""

    def test_inherits_from_pipeline_error(self):
        """Test that LLMProviderError inherits from PipelineError."""
        error = LLMProviderError("Provider failed")
        assert isinstance(error, PipelineError)
        assert isinstance(error, Exception)

    def test_llm_provider_error_with_context(self):
        """Test LLMProviderError with context."""
        context = {"provider": "openai", "model": "gpt-4o"}
        error = LLMProviderError("API error", context=context)
        assert str(error) == "API error"
        assert error.context == context


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
        context = {
            "provider": "anthropic",
            "model": "claude-sonnet-4-5",
            "retry_after": 60,
        }
        error = LLMRateLimitError("Rate limit hit", context=context)
        assert str(error) == "Rate limit hit"
        assert error.context["retry_after"] == 60


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
        context = {"timeout": 30.0, "model": "gpt-4o", "elapsed": 31.5}
        error = LLMTimeoutError("Timeout after 30s", context=context)
        assert str(error) == "Timeout after 30s"
        assert error.context["timeout"] == 30.0
        assert error.context["elapsed"] == 31.5


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
        context = {
            "model": "claude-sonnet-4-5",
            "response_text": '{"invalid": json}',
            "expected_schema": "CriadorOutput",
        }
        error = OutputParsingError("Invalid JSON", context=context)
        assert str(error) == "Invalid JSON"
        assert error.context["model"] == "claude-sonnet-4-5"
        assert "invalid" in error.context["response_text"]


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

        # LLMTimeoutError inherits from LLMProviderError
        assert issubclass(LLMTimeoutError, LLMProviderError)

        # OutputParsingError inherits from PipelineError (not LLMProviderError)
        assert issubclass(OutputParsingError, PipelineError)
        assert not issubclass(OutputParsingError, LLMProviderError)

    def test_catching_exceptions_by_hierarchy(self):
        """Test that exceptions can be caught at different hierarchy levels."""
        # Catching LLMProviderError catches rate limits and timeouts
        try:
            raise LLMRateLimitError("Rate limit", context={"test": True})
        except LLMProviderError as e:
            assert isinstance(e, LLMRateLimitError)
            assert e.context["test"] is True

        # Catching PipelineError catches all custom exceptions
        try:
            raise OutputParsingError("Parse failed")
        except PipelineError as e:
            assert isinstance(e, OutputParsingError)

    def test_exception_context_immutability(self):
        """Test that exception context can be modified after creation."""
        context = {"key": "value"}
        error = PipelineError("Test", context=context)

        # Should be able to add context
        error.context["new_key"] = "new_value"
        assert error.context["new_key"] == "new_value"
