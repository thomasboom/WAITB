"""Main CLI entry point"""

import argparse
import sys
import time
import re
from datetime import datetime

from waitb.wordle import WordleGame, is_valid_word
from waitb.providers import get_provider, list_providers, Message
from waitb.results import ResultsLogger, GameResult
from waitb.config import Config


def parse_args():
    parser = argparse.ArgumentParser(
        description="WAITB - Wordle AI Terminal Benchmark",
        prog="waitb"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    run_parser = subparsers.add_parser("run", help="Run a benchmark game")
    run_parser.add_argument("--provider", "-p", help="LLM provider to use")
    run_parser.add_argument("--model", "-m", help="Model to use")
    run_parser.add_argument("--games", "-g", type=int, default=1, help="Number of games to play")
    run_parser.add_argument("--word", "-w", help="Specific word to play (random if not set)")
    run_parser.add_argument("--csv", help="Path to CSV results file")
    
    subparsers.add_parser("list-providers", help="List available providers")
    subparsers.add_parser("results", help="Show results summary")
    subparsers.add_parser("config", help="Show configuration")
    
    return parser.parse_args()


def extract_guess(response: str) -> str:
    response = response.strip().upper()
    words = re.findall(r'\b[A-Z]{5}\b', response)
    
    for word in words:
        if is_valid_word(word):
            return word
    
    for word in words:
        if len(word) == 5 and word.isalpha():
            return word
    
    return None


def run_game(provider, model: str, target_word: str = None, csv_path: str = None):
    print(f"\n{'='*50}")
    print(f"Starting Wordle game")
    if target_word:
        print(f"Target word: {target_word}")
    print(f"Provider: {provider.name}, Model: {model or 'default'}")
    print(f"{'='*50}\n")
    
    game = WordleGame(target=target_word)
    messages = [
        Message(role="system", content=provider.get_system_prompt()),
    ]
    
    guess_times = []
    start_time = time.time()
    
    while not game.game_over:
        game_state = game.get_state_for_ai()
        prompt = provider.get_turn_prompt(game_state)
        
        messages.append(Message(role="user", content=prompt))
        
        try:
            guess_start = time.time()
            response = provider.chat(messages, model)
            guess_time = time.time() - guess_start
            guess_times.append(guess_time)
            
            messages.append(Message(role="assistant", content=response))
            
            guess = extract_guess(response)
            
            if not guess:
                print(f"  Could not extract valid guess from response: {response[:100]}...")
                continue
            
            print(f"  Guess {len(game.attempts) + 1}: {guess} ({guess_time:.1f}s)")
            
            success, feedback = game.make_guess(guess)
            
            if not success:
                print(f"  Invalid: {feedback[0]}")
                continue
            
            fb_display = "".join(
                "G" if f == "G" else "Y" if f == "Y" else "_"
                for f in feedback
            )
            print(f"  Feedback: {fb_display}")
            
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    total_time = time.time() - start_time
    
    print(f"\n{'='*50}")
    if game.won:
        print(f"WON! Solved in {len(game.attempts)} attempts ({total_time:.1f}s)")
    else:
        print(f"LOST! The word was: {game.target}")
    print(f"{'='*50}\n")
    
    result = GameResult(
        timestamp=datetime.now().isoformat(),
        provider=provider.name,
        model=model or "default",
        word=game.target,
        attempts=len(game.attempts),
        won=game.won,
        guess_times=guess_times,
        total_time=total_time,
    )
    
    if csv_path:
        logger = ResultsLogger(csv_path)
        logger.log(result)
        print(f"Results saved to {csv_path}")
    
    return result


def cmd_run(args):
    config = Config()
    
    provider_name = args.provider or config.get("default_provider", "openai")
    model = args.model or config.get("default_model")
    csv_path = args.csv or config.get("csv_path")
    
    try:
        provider = get_provider(provider_name)
    except ValueError as e:
        print(f"Error: {e}")
        print("\nAvailable providers: " + ", ".join(list_providers()))
        sys.exit(1)
    
    env_var = provider.get_api_key_env()
    if env_var and not os.environ.get(env_var):
        print(f"Warning: {env_var} environment variable not set")
        if provider_name == "ollama":
            print("Note: Ollama runs locally, no API key required")
        else:
            print("Results may fail without proper API key")
    
    for i in range(args.games):
        if args.games > 1:
            print(f"\n=== Game {i + 1}/{args.games} ===")
        
        target = args.word
        run_game(provider, model, target, csv_path)


def cmd_list_providers(args):
    print("Available LLM providers:")
    for p in list_providers():
        env_var = get_provider(p).get_api_key_env()
        if env_var:
            print(f"  - {p} (set {env_var})")
        else:
            print(f"  - {p} (no API key)")


def cmd_results(args):
    logger = ResultsLogger()
    logger.print_summary()


def cmd_config(args):
    config = Config()
    print("Current configuration:")
    for key, value in config.data.items():
        print(f"  {key}: {value}")


def main():
    import os
    
    args = parse_args()
    
    if not args.command:
        print("WAITB - Wordle AI Terminal Benchmark")
        print("Use 'waitb run --help' to get started")
        print("Use 'waitb list-providers' to see available providers")
        sys.exit(1)
    
    if args.command == "run":
        cmd_run(args)
    elif args.command == "list-providers":
        cmd_list_providers(args)
    elif args.command == "results":
        cmd_results(args)
    elif args.command == "config":
        cmd_config(args)


if __name__ == "__main__":
    main()
