"""Tests for AnthropicProvider implementation."""

import asyncio
from asyncio import Semaphore
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel

from construtor.config.exceptions import (
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
    OutputParsingError,
)
from construtor.providers.anthropic_provider import AnthropicProvider
from construtor.providers.base import LLMProvider


class SampleOutputModel(BaseModel):
    """Sample Pydantic model for structured output tests."""

    text: str
    count: int


class TestAnthropicProviderInitialization:
    """Test AnthropicProvider initialization and Protocol conformance."""

    def test_implements_llm_provider_protocol(self):
        """Test that AnthropicProvider implements LLMProvider Protocol."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)
        assert isinstance(provider, LLMProvider)

    def test_stores_api_key_and_semaphore(self):
        """Test that provider stores semaphore and creates client."""
        semaphore = Semaphore(3)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)
        assert provider.semaphore is semaphore
        assert hasattr(provider, "client")

    def test_default_timeout_is_30_seconds(self):
        """Test that default timeout is 30 seconds."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)
        assert provider.timeout == 30.0

    def test_custom_timeout_can_be_set(self):
        """Test that custom timeout can be configured."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(
            api_key="test-key",
            semaphore=semaphore,
            timeout=60.0,
        )
        assert provider.timeout == 60.0


class TestAnthropicProviderGenerate:
    """Test AnthropicProvider.generate() method."""

    @pytest.mark.asyncio
    async def test_generate_returns_dict_with_required_keys(self):
        """Test that generate returns dict with content, tokens_used, cost, latency."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        # Mock the Anthropic client response
        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await provider.generate(
                prompt="Test prompt",
                model="claude-sonnet-4-5",
                temperature=0.7,
            )

            assert isinstance(result, dict)
            assert "content" in result
            assert "tokens_used" in result
            assert "cost" in result
            assert "latency" in result

    @pytest.mark.asyncio
    async def test_generate_uses_semaphore(self):
        """Test that generate acquires semaphore before API call."""
        semaphore = Semaphore(1)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        mock_response = Mock()
        mock_response.content = [Mock(text="Test")]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)

        # Track semaphore acquisition
        semaphore_acquired = False

        async def mock_create(*args, **kwargs):
            nonlocal semaphore_acquired
            # Semaphore should be acquired when API is called
            semaphore_acquired = semaphore.locked()
            return mock_response

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock:
            mock.side_effect = mock_create

            await provider.generate(
                prompt="Test",
                model="claude-sonnet-4-5",
                temperature=0.7,
            )

            assert semaphore_acquired is True


class TestAnthropicProviderCostCalculation:
    """Test token counting and cost calculation."""

    @pytest.mark.asyncio
    async def test_calculates_cost_for_claude_sonnet(self):
        """Test cost calculation for Claude Sonnet ($3 input / $15 output per 1M)."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        # 1000 input + 2000 output tokens
        mock_response.usage = Mock(input_tokens=1000, output_tokens=2000)

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await provider.generate(
                prompt="Test",
                model="claude-sonnet-4-5",
                temperature=0.7,
            )

            # Expected: (1000/1M * $3) + (2000/1M * $15) = $0.003 + $0.03 = $0.033
            expected_cost = 0.033
            assert result["cost"] == pytest.approx(expected_cost, abs=0.000001)
            assert result["tokens_used"] == 3000

    @pytest.mark.asyncio
    async def test_calculates_cost_for_claude_haiku(self):
        """Test cost calculation for Claude Haiku ($1 input / $5 output per 1M)."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        mock_response = Mock()
        mock_response.content = [Mock(text="Test response")]
        mock_response.usage = Mock(input_tokens=1000, output_tokens=2000)

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await provider.generate(
                prompt="Test",
                model="claude-haiku-4-5",
                temperature=0.7,
            )

            # Expected: (1000/1M * $1) + (2000/1M * $5) = $0.001 + $0.01 = $0.011
            expected_cost = 0.011
            assert result["cost"] == pytest.approx(expected_cost, abs=0.000001)


class TestAnthropicProviderStructuredOutput:
    """Test structured output with Pydantic models."""

    @pytest.mark.asyncio
    async def test_structured_output_with_pydantic_model(self):
        """Test that response_model triggers JSON parsing."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        # Mock JSON response from Anthropic
        json_response = '{"text": "test", "count": 42}'
        mock_response = Mock()
        mock_response.content = [Mock(text=json_response)]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await provider.generate(
                prompt="Test",
                model="claude-sonnet-4-5",
                temperature=0.7,
                response_model=SampleOutputModel,
            )

            # Should parse JSON to Pydantic model
            assert isinstance(result["content"], SampleOutputModel)
            assert result["content"].text == "test"
            assert result["content"].count == 42

            # Should use structured outputs header
            call_kwargs = mock_create.call_args.kwargs
            assert "extra_headers" in call_kwargs
            assert call_kwargs["extra_headers"]["anthropic-beta"] == "structured-outputs-2025-11-13"

    @pytest.mark.asyncio
    async def test_raises_parsing_error_on_invalid_json(self):
        """Test that invalid JSON raises OutputParsingError."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        # Mock invalid JSON response
        mock_response = Mock()
        mock_response.content = [Mock(text='{"invalid": json}')]  # Invalid JSON
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            with pytest.raises(OutputParsingError) as exc_info:
                await provider.generate(
                    prompt="Test",
                    model="claude-sonnet-4-5",
                    temperature=0.7,
                    response_model=SampleOutputModel,
                )

            assert "parse" in str(exc_info.value).lower()


class TestAnthropicProviderErrorHandling:
    """Test error handling and custom exceptions."""

    @pytest.mark.asyncio
    async def test_raises_rate_limit_error_on_429(self):
        """Test that rate limit error raises LLMRateLimitError."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        # Mock rate limit error
        mock_error = Exception("rate_limit_error: Too many requests")

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_error

            with pytest.raises(LLMRateLimitError) as exc_info:
                await provider.generate(
                    prompt="Test",
                    model="claude-sonnet-4-5",
                    temperature=0.7,
                )

            assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_raises_timeout_error_on_timeout(self):
        """Test that timeout raises LLMTimeoutError."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(
            api_key="test-key",
            semaphore=semaphore,
            timeout=0.001,
        )

        # Mock slow API call
        async def slow_call(*args, **kwargs):
            await asyncio.sleep(1)  # Sleep longer than timeout
            return Mock()

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = slow_call

            with pytest.raises(LLMTimeoutError) as exc_info:
                await provider.generate(
                    prompt="Test",
                    model="claude-sonnet-4-5",
                    temperature=0.7,
                )

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_raises_provider_error_on_general_api_error(self):
        """Test that general API errors raise LLMProviderError."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        # Mock generic API error
        mock_error = Exception("Invalid API key")

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_error

            with pytest.raises(LLMProviderError) as exc_info:
                await provider.generate(
                    prompt="Test",
                    model="claude-sonnet-4-5",
                    temperature=0.7,
                )

            assert "Invalid API key" in str(exc_info.value)


class TestAnthropicProviderRetry:
    """Test exponential backoff retry logic."""

    @pytest.mark.asyncio
    async def test_retries_on_rate_limit_with_backoff(self):
        """Test that rate limits trigger retry with exponential backoff."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        # First call fails, second succeeds
        mock_response = Mock()
        mock_response.content = [Mock(text="Success")]
        mock_response.usage = Mock(input_tokens=10, output_tokens=20)

        call_count = 0

        class MockRateLimitError(Exception):
            """Mock rate limit error for testing."""

            pass

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise MockRateLimitError("rate_limit_error: Too many requests")
            return mock_response

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_call

            result = await provider.generate(
                prompt="Test",
                model="claude-sonnet-4-5",
                temperature=0.7,
            )

            # Should have retried once
            assert call_count == 2
            assert result["content"] == "Success"

    @pytest.mark.asyncio
    async def test_fails_after_max_retries(self):
        """Test that provider fails after max retry attempts."""
        semaphore = Semaphore(5)
        provider = AnthropicProvider(api_key="test-key", semaphore=semaphore)

        # Always fail
        mock_error = Exception("rate_limit_error: Too many requests")

        with patch.object(
            provider.client.messages,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_error

            with pytest.raises(LLMRateLimitError):
                await provider.generate(
                    prompt="Test",
                    model="claude-sonnet-4-5",
                    temperature=0.7,
                )

            # Should have tried 3 times (initial + 2 retries)
            assert mock_create.call_count == 3
