"""Groq provider"""

import os

import httpx

from .base import BaseProvider, Message


class GroqProvider(BaseProvider):
    name = "groq"

    def get_api_key_env(self) -> str:
        return "GROQ_API_KEY"

    def chat(self, messages: list[Message], model: str = None) -> str:
        api_key = os.environ.get(self.get_api_key_env())
        if not api_key:
            raise ValueError(
                f"API key not found. Set {self.get_api_key_env()} environment variable."
            )

        model = model or "llama-3.1-70b-versatile"

        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": 0.7,
            "max_tokens": 1024,
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        base_url = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("choices"):
                    raise ValueError("No choices returned from Groq API")

                content = data["choices"][0]["message"]["content"]
                if not content:
                    raise ValueError("Empty content returned from Groq API")

                return content
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise ValueError(
                    f"Invalid API key for Groq. Status: {e.response.status_code}"
                )
            elif e.response.status_code == 429:
                raise ValueError(
                    f"Rate limit exceeded. Status: {e.response.status_code}"
                )
            else:
                raise ValueError(
                    f"Groq API error: {e.response.status_code} - {e.response.text}"
                )
        except httpx.TimeoutException:
            raise ValueError("Groq API request timed out")
        except httpx.RequestError as e:
            raise ValueError(f"Failed to connect to Groq API: {e}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected response format from Groq: {e}")
