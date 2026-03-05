"""Wordle game engine"""

import os
import random

VALID_GUESSES = None
TARGET_WORDS = None


def load_words():
    global VALID_GUESSES, TARGET_WORDS

    if VALID_GUESSES is not None:
        return

    words_dir = os.path.join(os.path.dirname(__file__), "words")
    words_path = os.path.join(words_dir, "words.txt")

    if os.path.exists(words_path):
        with open(words_path, "r") as f:
            lines = [line.strip().upper() for line in f if line.strip()]

        # Split by separator line if present
        if "-----" in lines:
            sep_index = lines.index("-----")
            TARGET_WORDS = lines[:sep_index]
            VALID_GUESSES = set(lines[sep_index + 1 :])
        else:
            # No separator - all words are both valid and potential targets
            TARGET_WORDS = lines
            VALID_GUESSES = set(lines)
    else:
        VALID_GUESSES = None
        TARGET_WORDS = None


def is_valid_word(word: str) -> bool:
    load_words()
    if VALID_GUESSES is None:
        return len(word) == 5 and word.isalpha()
    return word.upper() in VALID_GUESSES


def get_random_word() -> str:
    load_words()
    if TARGET_WORDS:
        return random.choice(TARGET_WORDS)

    if VALID_GUESSES:
        return random.choice(list(VALID_GUESSES))

    return "WORDS"


class WordleGame:
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    GRAY = "\033[90m"
    RESET = "\033[0m"

    def __init__(self, target: str = None, max_attempts: int = 6):
        self.target = (target or get_random_word()).upper()
        self.max_attempts = max_attempts
        self.attempts = []
        self.game_over = False
        self.won = False

    def get_feedback(self, guess: str) -> list[str]:
        guess = guess.upper()
        target = self.target
        feedback = []

        target_letter_counts = {}
        for letter in target:
            target_letter_counts[letter] = target_letter_counts.get(letter, 0) + 1

        for i, letter in enumerate(guess):
            if letter == target[i]:
                feedback.append("G")
                target_letter_counts[letter] -= 1
            else:
                feedback.append(None)

        for i, letter in enumerate(guess):
            if feedback[i] is not None:
                continue

            if target_letter_counts.get(letter, 0) > 0:
                feedback[i] = "Y"
                target_letter_counts[letter] -= 1
            else:
                feedback[i] = "B"

        return feedback

    def get_colored_guess(self, guess: str) -> str:
        feedback = self.get_feedback(guess)
        result = []
        for letter, fb in zip(guess.upper(), feedback):
            if fb == "G":
                result.append(f"{self.GREEN}{letter}{self.RESET}")
            elif fb == "Y":
                result.append(f"{self.YELLOW}{letter}{self.RESET}")
            else:
                result.append(f"{self.GRAY}{letter}{self.RESET}")
        return "".join(result)

    def make_guess(self, guess: str) -> tuple[bool, list[str]]:
        guess = guess.upper()

        if len(guess) != 5:
            return False, ["Guess must be 5 letters"]

        if not guess.isalpha():
            return False, ["Guess must contain only letters"]

        if not is_valid_word(guess):
            return False, ["Not in word list"]

        self.attempts.append(guess)

        feedback = self.get_feedback(guess)

        if guess == self.target:
            self.game_over = True
            self.won = True
        elif len(self.attempts) >= self.max_attempts:
            self.game_over = True
            self.won = False

        return True, feedback

    def display(self) -> str:
        lines = []
        for attempt in self.attempts:
            lines.append(self.get_colored_guess(attempt))

        for _ in range(self.max_attempts - len(self.attempts)):
            lines.append("_____")

        return "\n".join(lines)

    def get_state_for_ai(self) -> str:
        lines = []
        for attempt in self.attempts:
            feedback = self.get_feedback(attempt)
            fb_str = "".join(
                "G" if f == "G" else "Y" if f == "Y" else "_" for f in feedback
            )
            lines.append(f"{attempt} -> {fb_str}")

        if not lines:
            return "No guesses yet"

        return "\n".join(lines)
