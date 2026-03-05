"""OpenAI provider"""

import os
import httpx
from .base import BaseProvider, Message


class OpenAIProvider(BaseProvider):
    name = "openai"
    
    def get_api_key_env(self) -> str:
        return "OPENAI_API_KEY"
    
    def chat(self, messages: list[Message], model: str = None) -> str:
        api_key = os.environ.get(self.get_api_key_env())
        if not api_key:
            raise ValueError(f"API key not found. Set {self.get_api_key_env()} environment variable.")
        
        model = model or "gpt-4"
        
        payload = {
            "model": model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": 0.7,
        }
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                f"{base_url}/chat/completions",
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"]
