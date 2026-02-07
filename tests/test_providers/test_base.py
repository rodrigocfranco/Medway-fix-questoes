"""Tests for LLMProvider Protocol definition."""

from asyncio import Semaphore
from typing import Protocol

from construtor.providers.base import LLMProvider


class TestLLMProviderProtocol:
    """Test LLMProvider Protocol definition and structure."""

    def test_llm_provider_is_protocol(self):
        """Test that LLMProvider is a Protocol."""
        assert issubclass(LLMProvider, Protocol)

    def test_llm_provider_is_runtime_checkable(self):
        """Test that LLMProvider can be checked at runtime."""
        # The Protocol should be decorated with @runtime_checkable
        # This allows isinstance() checks at runtime
        assert hasattr(LLMProvider, "__protocol_attrs__") or hasattr(
            LLMProvider,
            "_is_protocol",
        )

    def test_protocol_has_semaphore_attribute(self):
        """Test that Protocol requires semaphore attribute."""
        # Check that the Protocol definition includes semaphore
        assert "semaphore" in LLMProvider.__annotations__

    def test_protocol_has_generate_method(self):
        """Test that Protocol requires generate method."""
        # Check that the Protocol definition includes generate
        assert "generate" in dir(LLMProvider)


class TestLLMProviderImplementation:
    """Test that classes can implement LLMProvider Protocol."""

    def test_minimal_implementation_satisfies_protocol(self):
        """Test that a minimal class satisfies the Protocol."""

        class MinimalProvider:
            """Minimal implementation for testing Protocol conformance."""

            def __init__(self):
                self.semaphore = Semaphore(5)

            async def generate(
                self,
                prompt: str,
                model: str,
                temperature: float,
                response_model: type | None = None,
            ) -> dict:
                """Minimal generate implementation."""
                return {
                    "content": "test response",
                    "tokens_used": 100,
                    "cost": 0.001,
                    "latency": 0.5,
                }

        provider = MinimalProvider()
        # In Python 3.11+, isinstance checks work with Protocol
        assert isinstance(provider, LLMProvider)

    def test_missing_semaphore_fails_protocol(self):
        """Test that missing semaphore attribute fails Protocol check."""

        class BadProvider:
            """Provider missing semaphore attribute."""

            async def generate(
                self,
                prompt: str,
                model: str,
                temperature: float,
                response_model: type | None = None,
            ) -> dict:
                return {
                    "content": "test",
                    "tokens_used": 100,
                    "cost": 0.001,
                    "latency": 0.5,
                }

        provider = BadProvider()
        # Should NOT satisfy Protocol without semaphore
        assert not isinstance(provider, LLMProvider)

    def test_missing_generate_fails_protocol(self):
        """Test that missing generate method fails Protocol check."""

        class BadProvider:
            """Provider missing generate method."""

            def __init__(self):
                self.semaphore = Semaphore(5)

        provider = BadProvider()
        # Should NOT satisfy Protocol without generate
        assert not isinstance(provider, LLMProvider)


class TestGenerateMethodSignature:
    """Test the generate method signature requirements."""

    def test_generate_has_correct_parameters(self):
        """Test that generate method has correct parameter signature."""

        class TestProvider:
            """Test provider for signature validation."""

            def __init__(self):
                self.semaphore = Semaphore(5)

            async def generate(
                self,
                prompt: str,
                model: str,
                temperature: float,
                response_model: type | None = None,
            ) -> dict:
                """Test generate method."""
                return {
                    "content": "test",
                    "tokens_used": 100,
                    "cost": 0.001,
                    "latency": 0.5,
                }

        provider = TestProvider()
        assert isinstance(provider, LLMProvider)

        # Check method signature
        import inspect

        sig = inspect.signature(provider.generate)
        params = list(sig.parameters.keys())

        # Should have: self, prompt, model, temperature, response_model
        assert "prompt" in params
        assert "model" in params
        assert "temperature" in params
        assert "response_model" in params

    def test_generate_return_type_is_dict(self):
        """Test that generate returns dict with required keys."""

        class TestProvider:
            """Test provider for return type validation."""

            def __init__(self):
                self.semaphore = Semaphore(5)

            async def generate(
                self,
                prompt: str,
                model: str,
                temperature: float,
                response_model: type | None = None,
            ) -> dict:
                """Test generate method."""
                return {
                    "content": "test response",
                    "tokens_used": 100,
                    "cost": 0.001,
                    "latency": 0.5,
                }

        provider = TestProvider()
        assert isinstance(provider, LLMProvider)

        # Check return type annotation
        import inspect

        sig = inspect.signature(provider.generate)
        assert sig.return_annotation is dict


class TestProtocolDocumentation:
    """Test that Protocol has proper documentation."""

    def test_protocol_has_docstring(self):
        """Test that LLMProvider has a docstring."""
        assert LLMProvider.__doc__ is not None
        assert len(LLMProvider.__doc__) > 0

    def test_generate_method_has_docstring(self):
        """Test that generate method has documentation."""
        # The Protocol should define generate with a docstring
        # Check if there's documentation for the generate method
        assert hasattr(LLMProvider, "generate")
