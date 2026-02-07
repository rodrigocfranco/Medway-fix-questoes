"""Tests for OpenAIProvider implementation."""

import asyncio
from asyncio import Semaphore
from unittest.mock import AsyncMock, Mock, patch

import pytest
from pydantic import BaseModel

from construtor.config.exceptions import (
    LLMProviderError,
    LLMRateLimitError,
    LLMTimeoutError,
)
from construtor.providers.base import LLMProvider
from construtor.providers.openai_provider import OpenAIProvider


class SampleOutputModel(BaseModel):
    """Sample Pydantic model for structured output tests."""

    text: str
    count: int


class TestOpenAIProviderInitialization:
    """Test OpenAIProvider initialization and Protocol conformance."""

    def test_implements_llm_provider_protocol(self):
        """Test that OpenAIProvider implements LLMProvider Protocol."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)
        assert isinstance(provider, LLMProvider)

    def test_stores_api_key_and_semaphore(self):
        """Test that provider stores semaphore and creates client."""
        semaphore = Semaphore(3)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)
        assert provider.semaphore is semaphore
        assert hasattr(provider, "client")

    def test_default_timeout_is_30_seconds(self):
        """Test that default timeout is 30 seconds."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)
        assert provider.timeout == 30.0

    def test_custom_timeout_can_be_set(self):
        """Test that custom timeout can be configured."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(
            api_key="test-key",
            semaphore=semaphore,
            timeout=60.0,
        )
        assert provider.timeout == 60.0


class TestOpenAIProviderGenerate:
    """Test OpenAIProvider.generate() method."""

    @pytest.mark.asyncio
    async def test_generate_returns_dict_with_required_keys(self):
        """Test that generate returns dict with content, tokens_used, cost, latency."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        # Mock the OpenAI client response
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await provider.generate(
                prompt="Test prompt",
                model="gpt-4o",
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
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test"))]
        mock_response.usage = Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        # Track semaphore acquisition
        semaphore_acquired = False

        async def mock_create(*args, **kwargs):
            nonlocal semaphore_acquired
            # Semaphore should be acquired when API is called
            semaphore_acquired = semaphore.locked()
            return mock_response

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock:
            mock.side_effect = mock_create

            await provider.generate(
                prompt="Test",
                model="gpt-4o",
                temperature=0.7,
            )

            assert semaphore_acquired is True


class TestOpenAIProviderCostCalculation:
    """Test token counting and cost calculation."""

    @pytest.mark.asyncio
    async def test_calculates_cost_for_gpt_4o(self):
        """Test cost calculation for GPT-4o ($2.50 input / $10.00 output per 1M)."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        # 1000 input + 2000 output tokens
        mock_response.usage = Mock(
            prompt_tokens=1000,
            completion_tokens=2000,
            total_tokens=3000,
        )

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await provider.generate(
                prompt="Test",
                model="gpt-4o",
                temperature=0.7,
            )

            # Expected: (1000/1M * $2.50) + (2000/1M * $10.00) = $0.0025 + $0.02 = $0.0225
            expected_cost = 0.0225
            assert result["cost"] == pytest.approx(expected_cost, abs=0.000001)
            assert result["tokens_used"] == 3000

    @pytest.mark.asyncio
    async def test_calculates_cost_for_gpt_4o_mini(self):
        """Test cost calculation for GPT-4o-mini ($0.15 input / $0.60 output per 1M)."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Test response"))]
        mock_response.usage = Mock(
            prompt_tokens=1000,
            completion_tokens=2000,
            total_tokens=3000,
        )

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.return_value = mock_response

            result = await provider.generate(
                prompt="Test",
                model="gpt-4o-mini",
                temperature=0.7,
            )

            # Expected: (1000/1M * $0.15) + (2000/1M * $0.60) = $0.00015 + $0.0012 = $0.00135
            expected_cost = 0.00135
            assert result["cost"] == pytest.approx(expected_cost, abs=0.000001)


class TestOpenAIProviderStructuredOutput:
    """Test structured output with Pydantic models."""

    @pytest.mark.asyncio
    async def test_structured_output_with_pydantic_model(self):
        """Test that response_model triggers beta.parse() for structured output."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        # Mock parsed response
        parsed_output = SampleOutputModel(text="test", count=42)
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(parsed=parsed_output))]
        mock_response.usage = Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        with patch.object(
            provider.client.beta.chat.completions,
            "parse",
            new_callable=AsyncMock,
        ) as mock_parse:
            mock_parse.return_value = mock_response

            result = await provider.generate(
                prompt="Test",
                model="gpt-4o",
                temperature=0.7,
                response_model=SampleOutputModel,
            )

            # Should use beta.parse() not regular create()
            mock_parse.assert_called_once()
            assert result["content"] == parsed_output
            assert isinstance(result["content"], SampleOutputModel)


class TestOpenAIProviderErrorHandling:
    """Test error handling and custom exceptions."""

    @pytest.mark.asyncio
    async def test_raises_rate_limit_error_on_429(self):
        """Test that HTTP 429 raises LLMRateLimitError."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        # Mock rate limit error
        from openai import RateLimitError

        mock_error = RateLimitError(
            "Rate limit exceeded",
            response=Mock(status_code=429),
            body=None,
        )

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_error

            with pytest.raises(LLMRateLimitError) as exc_info:
                await provider.generate(
                    prompt="Test",
                    model="gpt-4o",
                    temperature=0.7,
                )

            assert "rate limit" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_raises_timeout_error_on_timeout(self):
        """Test that timeout raises LLMTimeoutError."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(
            api_key="test-key",
            semaphore=semaphore,
            timeout=0.001,
        )

        # Mock slow API call
        async def slow_call(*args, **kwargs):
            await asyncio.sleep(1)  # Sleep longer than timeout
            return Mock()

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = slow_call

            with pytest.raises(LLMTimeoutError) as exc_info:
                await provider.generate(
                    prompt="Test",
                    model="gpt-4o",
                    temperature=0.7,
                )

            assert "timeout" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_raises_provider_error_on_general_api_error(self):
        """Test that general API errors raise LLMProviderError."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        # Mock generic API error
        mock_error = Exception("Invalid API key")

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_error

            with pytest.raises(LLMProviderError) as exc_info:
                await provider.generate(
                    prompt="Test",
                    model="gpt-4o",
                    temperature=0.7,
                )

            assert "Invalid API key" in str(exc_info.value)


class TestOpenAIProviderRetry:
    """Test exponential backoff retry logic."""

    @pytest.mark.asyncio
    async def test_retries_on_rate_limit_with_backoff(self):
        """Test that rate limits trigger retry with exponential backoff."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        from openai import RateLimitError

        # First call fails, second succeeds
        mock_response = Mock()
        mock_response.choices = [Mock(message=Mock(content="Success"))]
        mock_response.usage = Mock(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )

        call_count = 0

        async def mock_call(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RateLimitError(
                    "Rate limit",
                    response=Mock(status_code=429),
                    body=None,
                )
            return mock_response

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_call

            result = await provider.generate(
                prompt="Test",
                model="gpt-4o",
                temperature=0.7,
            )

            # Should have retried once
            assert call_count == 2
            assert result["content"] == "Success"

    @pytest.mark.asyncio
    async def test_fails_after_max_retries(self):
        """Test that provider fails after max retry attempts."""
        semaphore = Semaphore(5)
        provider = OpenAIProvider(api_key="test-key", semaphore=semaphore)

        from openai import RateLimitError

        # Always fail
        mock_error = RateLimitError(
            "Rate limit",
            response=Mock(status_code=429),
            body=None,
        )

        with patch.object(
            provider.client.chat.completions,
            "create",
            new_callable=AsyncMock,
        ) as mock_create:
            mock_create.side_effect = mock_error

            with pytest.raises(LLMRateLimitError):
                await provider.generate(
                    prompt="Test",
                    model="gpt-4o",
                    temperature=0.7,
                )

            # Should have tried 3 times (initial + 2 retries)
            assert mock_create.call_count == 3
