"""LLM provider abstraction layer.

This package provides a unified interface for calling OpenAI and Anthropic LLMs
through the LLMProvider Protocol. All providers implement the same interface,
making it easy to switch between models without changing agent code.

Available providers:
    - LLMProvider: Protocol defining the provider interface
    - OpenAIProvider: Implementation for OpenAI's GPT models
    - AnthropicProvider: Implementation for Anthropic's Claude models

Example:
    ```python
    from asyncio import Semaphore
    from construtor.providers import OpenAIProvider, AnthropicProvider

    # Create shared semaphore for concurrency control
    semaphore = Semaphore(5)

    # Initialize providers
    openai = OpenAIProvider(api_key="sk-...", semaphore=semaphore)
    anthropic = AnthropicProvider(api_key="sk-ant-...", semaphore=semaphore)

    # Both providers have the same interface
    result1 = await openai.generate(
        prompt="Test", model="gpt-4o", temperature=0.7
    )
    result2 = await anthropic.generate(
        prompt="Test", model="claude-sonnet-4-5", temperature=0.7
    )
    ```
"""

from construtor.providers.anthropic_provider import AnthropicProvider
from construtor.providers.base import LLMProvider
from construtor.providers.openai_provider import OpenAIProvider

__all__ = [
    "AnthropicProvider",
    "LLMProvider",
    "OpenAIProvider",
]
