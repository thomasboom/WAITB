"""CSV results logging"""

import csv
import os
from datetime import datetime
from dataclasses import dataclass


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


class ResultsLogger:
    def __init__(self, csv_path: str = None):
        if csv_path is None:
            csv_path = os.path.join(os.getcwd(), "waitb_results.csv")
        self.csv_path = csv_path
        self._ensure_header()
    
    def _ensure_header(self):
        if not os.path.exists(self.csv_path):
            with open(self.csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "timestamp",
                    "provider",
                    "model",
                    "word",
                    "attempts",
                    "won",
                    "guess_times",
                    "total_time",
                ])
    
    def log(self, result: GameResult):
        with open(self.csv_path, "a", newline="") as f:
            writer = csv.writer(f)
            guess_times_str = ";".join(str(t) for t in result.guess_times) if result.guess_times else ""
            writer.writerow([
                result.timestamp,
                result.provider,
                result.model,
                result.word,
                result.attempts,
                str(result.won).lower(),
                guess_times_str,
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
