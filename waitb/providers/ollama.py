"""Ollama (local) provider"""

import os

import httpx

from .base import BaseProvider, Message


class OllamaProvider(BaseProvider):
    name = "ollama"

    def get_api_key_env(self) -> str:
        return None

    def chat(self, messages: list[Message], model: str = None) -> str:
        model = model or "llama2"

        ollama_messages = []
        for m in messages:
            if m.role == "system":
                ollama_messages.append({"role": "system", "content": m.content})
            else:
                ollama_messages.append({"role": m.role, "content": m.content})

        payload = {
            "model": model,
            "messages": ollama_messages,
            "stream": False,
        }

        base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")

        try:
            with httpx.Client(timeout=120.0) as client:
                response = client.post(
                    f"{base_url}/api/chat",
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("message"):
                    raise ValueError("No message returned from Ollama")

                content = data["message"]["content"]
                if not content:
                    raise ValueError("Empty content returned from Ollama")

                return content
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Ollama API error: {e.response.status_code} - {e.response.text}"
            )
        except httpx.TimeoutException:
            raise ValueError(
                "Ollama request timed out. Ensure Ollama is running and the model is loaded."
            )
        except httpx.ConnectError:
            raise ValueError(
                "Failed to connect to Ollama. Ensure Ollama is running at " + base_url
            )
        except httpx.RequestError as e:
            raise ValueError(f"Failed to connect to Ollama: {e}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected response format from Ollama: {e}")
