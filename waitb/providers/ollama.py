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
        
        with httpx.Client(timeout=120.0) as client:
            response = client.post(
                f"{base_url}/api/chat",
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
