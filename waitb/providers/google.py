"""Google (Gemini) provider"""

import os
import httpx
import base64
import json
from .base import BaseProvider, Message


class GoogleProvider(BaseProvider):
    name = "google"
    
    def get_api_key_env(self) -> str:
        return "GOOGLE_API_KEY"
    
    def chat(self, messages: list[Message], model: str = None) -> str:
        api_key = os.environ.get(self.get_api_key_env())
        if not api_key:
            raise ValueError(f"API key not found. Set {self.get_api_key_env()} environment variable.")
        
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
            }
        }
        
        if system_instruction:
            payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
        
        base_url = os.environ.get("GOOGLE_BASE_URL", "https://generativelanguage.googleapis.com")
        
        url = f"{base_url}/v1beta/models/{model}:generateContent?key={api_key}"
        
        with httpx.Client(timeout=60.0) as client:
            response = client.post(
                url,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
