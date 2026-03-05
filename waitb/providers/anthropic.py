"""Anthropic (Claude) provider"""

import os

import httpx

from .base import BaseProvider, Message


class AnthropicProvider(BaseProvider):
    name = "anthropic"

    def get_api_key_env(self) -> str:
        return "ANTHROPIC_API_KEY"

    def chat(self, messages: list[Message], model: str = None) -> str:
        api_key = os.environ.get(self.get_api_key_env())
        if not api_key:
            raise ValueError(
                f"API key not found. Set {self.get_api_key_env()} environment variable."
            )

        model = model or "claude-3-5-sonnet-20241022"

        anthropic_messages = []
        for m in messages:
            if m.role == "system":
                continue
            anthropic_messages.append({"role": m.role, "content": m.content})

        system_prompt = None
        for m in messages:
            if m.role == "system":
                system_prompt = m.content
                break

        payload = {
            "model": model,
            "messages": anthropic_messages,
            "max_tokens": 1024,
            "temperature": 0.7,
        }

        if system_prompt:
            payload["system"] = system_prompt

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        }

        base_url = os.environ.get("ANTHROPIC_BASE_URL", "https://api.anthropic.com")

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{base_url}/v1/messages",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("content"):
                    raise ValueError("No content returned from Anthropic API")

                content = data["content"][0]["text"]
                if not content:
                    raise ValueError("Empty content returned from Anthropic API")

                return content
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    f"Invalid API key for Anthropic. Status: {e.response.status_code}"
                )
            elif e.response.status_code == 429:
                raise ValueError(
                    f"Rate limit exceeded. Status: {e.response.status_code}"
                )
            else:
                raise ValueError(
                    f"Anthropic API error: {e.response.status_code} - {e.response.text}"
                )
        except httpx.TimeoutException:
            raise ValueError("Anthropic API request timed out")
        except httpx.RequestError as e:
            raise ValueError(f"Failed to connect to Anthropic API: {e}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected response format from Anthropic: {e}")
