"""Base provider interface"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Message:
    role: str
    content: str


class BaseProvider(ABC):
    name: str = "base"
    
    @abstractmethod
    def chat(self, messages: list[Message], model: str = None) -> str:
        """Send a chat request and return the response content"""
        pass
    
    @abstractmethod
    def get_api_key_env(self) -> str:
        """Return the environment variable name for the API key"""
        pass
    
    def get_system_prompt(self) -> str:
        return """You are playing Wordle. The goal is to guess a 5-letter word in 6 attempts.

After each guess, you'll receive feedback:
- G = Green (correct letter, correct position)
- Y = Yellow (correct letter, wrong position)
- _ = Gray (letter not in the word)

Example feedback: GUESS -> G_Y__
This means: G is correct, U is wrong position, E is wrong position, S is correct, S is wrong position.

Rules:
1. Only guess valid 5-letter English words
2. Use the feedback to eliminate possibilities and find the word
3. Try to solve in as few guesses as possible

When it's your turn, respond with ONLY your guess (a single 5-letter word). Do not explain your reasoning, just give the word.

Start by making your first guess."""
    
    def get_turn_prompt(self, game_state: str) -> str:
        return f"""Game state:
{game_state}

Make your next guess (just the 5-letter word):"""
