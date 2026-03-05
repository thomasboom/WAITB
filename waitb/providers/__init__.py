"""LLM Provider abstraction"""

from .base import BaseProvider, Message
from .openai import OpenAIProvider
from .anthropic import AnthropicProvider
from .google import GoogleProvider
from .ollama import OllamaProvider
from .groq import GroqProvider

PROVIDERS = {
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
    "google": GoogleProvider,
    "ollama": OllamaProvider,
    "groq": GroqProvider,
}


def get_provider(name: str) -> BaseProvider:
    name = name.lower()
    if name not in PROVIDERS:
        raise ValueError(f"Unknown provider: {name}. Available: {list(PROVIDERS.keys())}")
    return PROVIDERS[name]()


def list_providers() -> list[str]:
    return list(PROVIDERS.keys())
