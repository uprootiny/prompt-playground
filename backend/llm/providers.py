"""
LLM provider wrappers
Supports OpenAI and Anthropic APIs
"""

from typing import Optional, Dict, Any
from abc import ABC, abstractmethod
import os


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate response from LLM"""
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """Get model name"""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI API wrapper"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """
        Initialize OpenAI provider

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model name (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Lazy import to avoid dependency issues
        from openai import OpenAI
        self.client = OpenAI(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generate response from OpenAI

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional arguments passed to API

        Returns:
            Generated text response
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        response = self.client.chat.completions.create(
            model=kwargs.get("model", self.model),
            messages=messages,
            temperature=kwargs.get("temperature", self.temperature),
            max_tokens=kwargs.get("max_tokens", self.max_tokens),
        )

        return response.choices[0].message.content

    def get_model_name(self) -> str:
        """Get model name"""
        return self.model


class AnthropicProvider(LLMProvider):
    """Anthropic API wrapper"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.7,
        max_tokens: int = 1000,
    ):
        """
        Initialize Anthropic provider

        Args:
            api_key: Anthropic API key (defaults to ANTHROPIC_API_KEY env var)
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if not self.api_key:
            raise ValueError("Anthropic API key required")

        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Lazy import to avoid dependency issues
        from anthropic import Anthropic
        self.client = Anthropic(api_key=self.api_key)

    def generate(self, prompt: str, system_prompt: Optional[str] = None, **kwargs) -> str:
        """
        Generate response from Anthropic

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional arguments passed to API

        Returns:
            Generated text response
        """
        message_params = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", self.max_tokens),
            "temperature": kwargs.get("temperature", self.temperature),
            "messages": [{"role": "user", "content": prompt}],
        }

        if system_prompt:
            message_params["system"] = system_prompt

        response = self.client.messages.create(**message_params)

        return response.content[0].text

    def get_model_name(self) -> str:
        """Get model name"""
        return self.model


def create_provider(
    provider_name: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    **kwargs,
) -> LLMProvider:
    """
    Factory function to create LLM provider

    Args:
        provider_name: "openai" or "anthropic"
        api_key: API key (optional, uses env var if not provided)
        model: Model name (optional, uses default if not provided)
        **kwargs: Additional provider-specific arguments

    Returns:
        Initialized LLMProvider instance

    Raises:
        ValueError: If provider_name is not supported
    """
    provider_name = provider_name.lower()

    if provider_name == "openai":
        provider_kwargs = {"api_key": api_key}
        if model:
            provider_kwargs["model"] = model
        provider_kwargs.update(kwargs)
        return OpenAIProvider(**provider_kwargs)

    elif provider_name == "anthropic":
        provider_kwargs = {"api_key": api_key}
        if model:
            provider_kwargs["model"] = model
        provider_kwargs.update(kwargs)
        return AnthropicProvider(**provider_kwargs)

    else:
        raise ValueError(f"Unsupported provider: {provider_name}. Use 'openai' or 'anthropic'")
