"""Google (Gemini) provider"""

import base64
import json
import os

import httpx

from .base import BaseProvider, Message


class GoogleProvider(BaseProvider):
    name = "google"

    def get_api_key_env(self) -> str:
        return "GOOGLE_API_KEY"

    def chat(self, messages: list[Message], model: str = None) -> str:
        api_key = os.environ.get(self.get_api_key_env())
        if not api_key:
            raise ValueError(
                f"API key not found. Set {self.get_api_key_env()} environment variable."
            )

        model = model or "gemini-1.5-flash"

        contents = []
        for m in messages:
            if m.role == "system":
                continue
            parts = [{"text": m.content}]
            role = "user" if m.role == "user" else "model"
            contents.append({"role": role, "parts": parts})

        system_instruction = None
        for m in messages:
            if m.role == "system":
                system_instruction = m.content
                break

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 1024,
            },
        }

        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

        base_url = os.environ.get(
            "GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com"
        )

        url = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    url,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()

                if not data.get("candidates"):
                    raise ValueError("No candidates returned from Google API")

                content = data["candidates"][0]["content"]["parts"][0]["text"]
                if not content:
                    raise ValueError("Empty content returned from Google API")

                return content
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                raise ValueError(
                    f"Invalid request to Google API. Status: {e.response.status_code} - {e.response.text}"
                )
            elif e.response.status_code == 401:
                raise ValueError(
                    f"Invalid API key for Google. Status: {e.response.status_code}"
                )
            elif e.response.status_code == 429:
                raise ValueError(
                    f"Rate limit exceeded. Status: {e.response.status_code}"
                )
            else:
                raise ValueError(
                    f"Google API error: {e.response.status_code} - {e.response.text}"
                )
        except httpx.TimeoutException:
            raise ValueError("Google API request timed out")
        except httpx.RequestError as e:
            raise ValueError(f"Failed to connect to Google API: {e}")
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected response format from Google: {e}")
