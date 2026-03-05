"""CSV results logging"""

import csv
import os
import uuid
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class GameResult:
    timestamp: str
    provider: str
    model: str
    word: str
    attempts: int
    won: bool
    guess_times: list[float]
    total_time: float
    guesses: Optional[list[str]] = None
    feedbacks: Optional[list[str]] = None
    game_id: Optional[str] = None


class ResultsLogger:
    def __init__(self, csv_path: Optional[str] = None):
        if csv_path is None:
            csv_path = os.path.join(os.getcwd(), "waitb_results.csv")
        self.csv_path = csv_path
        self._ensure_header()
    
    def _ensure_header(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "game_id",
                    "timestamp",
                    "provider",
                    "model",
                    "word",
                    "try_num",
                    "guess",
                    "feedback",
                    "guess_time",
                    "attempts",
                    "won",
                    "total_time",
                ])
    
    def log(self, result: GameResult):
        game_id = result.game_id or str(uuid.uuid4())[:8]
        
        if result.guesses and result.feedbacks:
            for i, (guess, feedback) in enumerate(zip(result.guesses, result.feedbacks)):
                guess_time = result.guess_times[i] if i < len(result.guess_times) else 0
                feedback_str = "".join(f for f in feedback)
                with open(self.csv_path, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        game_id,
                        result.timestamp,
                        result.provider,
                        result.model,
                        result.word,
                        i + 1,
                        guess,
                        feedback_str,
                        round(guess_time, 2),
                        result.attempts,
                        str(result.won).lower(),
                        round(result.total_time, 2),
                    ])
        else:
            with open(self.csv_path, "a", newline="") as f:
                writer = csv.writer(f)
                guess_times_str = ";".join(str(t) for t in result.guess_times) if result.guess_times else ""
                writer.writerow([
                    game_id,
                    result.timestamp,
                    result.provider,
                    result.model,
                    result.word,
                    "",
                    "",
                    "",
                    "",
                    result.attempts,
                    str(result.won).lower(),
                    round(result.total_time, 2),
                ])
    
    def load(self) -> list[dict]:
        results = []
        with open(self.csv_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                results.append(row)
        return results
    
    def print_summary(self):
        results = self.load()
        if not results:
            print("No results found.")
            return
        
        print(f"\n{'='*60}")
        print(f"WAITB Results Summary")
        print(f"{'='*60}")
        print(f"{'Provider':<15} {'Model':<25} {'Played':<8} {'Won':<6} {'Win%':<6} {'Avg Attempts'}")
        print(f"{'-'*60}")
        
        by_provider = {}
        for r in results:
            key = (r["provider"], r["model"])
            if key not in by_provider:
                by_provider[key] = {"played": 0, "won": 0, "attempts": []}
            by_provider[key]["played"] += 1
            if r["won"].lower() == "true":
                by_provider[key]["won"] += 1
            by_provider[key]["attempts"].append(int(r["attempts"]))
        
        for (provider, model), stats in sorted(by_provider.items()):
            win_rate = (stats["won"] / stats["played"]) * 100
            avg_attempts = sum(stats["attempts"]) / len(stats["attempts"])
            print(f"{provider:<15} {model:<25} {stats['played']:<8} {stats['won']:<6} {win_rate:>5.1f}% {avg_attempts:.1f}")
        
        print(f"{'='*60}")
        print(f"Total games: {len(results)}")
