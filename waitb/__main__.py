"""Main CLI entry point - Interactive Mode"""

import argparse
import os
import sys
import time
import re
from datetime import datetime

from waitb.wordle import WordleGame, is_valid_word
from waitb.providers import get_provider, list_providers, Message
from waitb.results import ResultsLogger, GameResult
from waitb.config import Config


def prompt(prompt_text: str) -> str:
    return input(f"\n{prompt_text}: ").strip()


def prompt_choice(prompt_text: str, choices: list, show_numbers: bool = True) -> int:
    print(f"\n{prompt_text}:")
    for i, choice in enumerate(choices):
        if show_numbers:
            print(f"  [{i + 1}] {choice}")
        else:
            print(f"  - {choice}")
    
    while True:
        try:
            if show_numbers:
                idx = int(prompt("Enter number"))
                if 1 <= idx <= len(choices):
                    return idx - 1
            else:
                val = prompt("Enter value")
                if val in choices:
                    return val
        except ValueError:
            pass
        print("Invalid choice, try again.")


def prompt_yes_no(prompt_text: str) -> bool:
    while True:
        resp = prompt(f"{prompt_text} (y/n)").lower().strip()
        if resp in ("y", "yes"):
            return True
        elif resp in ("n", "no"):
            return False


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


def setup_provider_interactive() -> tuple:
    print("\n" + "=" * 50)
    print("PROVIDER SETUP")
    print("=" * 50)
    
    providers = list_providers()
    print("\nAvailable providers:")
    for i, p in enumerate(providers):
        print(f"  [{i + 1}] {p}")
    
    idx = prompt_choice("Select provider", providers)
    provider_name = providers[idx]
    
    provider = get_provider(provider_name)
    env_var = provider.get_api_key_env()
    
    if env_var:
        existing_key = os.environ.get(env_var, "")
        use_existing = prompt_yes_no(f"Use existing {env_var}?")
        
        if use_existing and existing_key:
            api_key = existing_key
            print(f"Using existing API key (starts with {api_key[:8]}...)")
        else:
            api_key = prompt(f"Enter {env_var}")
            os.environ[env_var] = api_key
    else:
        api_key = None
        print("No API key required (local provider)")
    
    model = prompt("Enter model name").strip()
    
    print(f"\nProvider: {provider_name}")
    print(f"Model: {model}")
    
    return provider, model


def run_game(provider, model: str = None, target_word: str = None, csv_path: str = None):
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
        prompt_text = provider.get_turn_prompt(game_state)
        
        messages.append(Message(role="user", content=prompt_text))
        
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


def run_benchmark_interactive():
    provider, model = setup_provider_interactive()
    
    print("\n" + "=" * 50)
    print("GAME SETUP")
    print("=" * 50)
    
    num_games = prompt("How many games to play? (default: 1)")
    if not num_games:
        num_games = 1
    else:
        num_games = int(num_games)
    
    use_specific_word = prompt_yes_no("Use a specific word?")
    if use_specific_word:
        target_word = prompt("Enter the 5-letter word").upper()
    else:
        target_word = None
    
    save_results = prompt_yes_no("Save results to CSV?")
    if save_results:
        csv_path = prompt("CSV file path (default: waitb_results.csv)")
        if not csv_path:
            csv_path = "waitb_results.csv"
    else:
        csv_path = None
    
    for i in range(num_games):
        if num_games > 1:
            print(f"\n{'='*50}")
            print(f"GAME {i + 1}/{num_games}")
            print(f"{'='*50}")
        
        target = target_word
        run_game(provider, model, target, csv_path)
    
    if csv_path and num_games > 1:
        print(f"\nAll games complete! Results saved to {csv_path}")


def show_providers():
    print("\n" + "=" * 50)
    print("AVAILABLE PROVIDERS")
    print("=" * 50)
    
    for p in list_providers():
        print(f"\n{p.upper()}:")
        provider = get_provider(p)
        env_var = provider.get_api_key_env()
        
        if env_var:
            print(f"  API Key: {env_var}")
        else:
            print(f"  API Key: None (local)")


def show_results():
    print("\n" + "=" * 50)
    print("RESULTS SUMMARY")
    print("=" * 50)
    
    logger = ResultsLogger()
    logger.print_summary()


def interactive_menu():
    while True:
        print("\n" + "=" * 50)
        print("WAITB - Wordle AI Terminal Benchmark")
        print("=" * 50)
        print("  [1] Run benchmark (interactive)")
        print("  [2] List providers")
        print("  [3] Show results")
        print("  [4] Exit")
        
        choice = prompt("Choose an option")
        
        if choice == "1":
            run_benchmark_interactive()
        elif choice == "2":
            show_providers()
        elif choice == "3":
            show_results()
        elif choice == "4":
            print("\nGoodbye!")
            sys.exit(0)
        else:
            print("Invalid choice, try again.")


def main():
    args = parse_args()
    
    if not args.command:
        interactive_menu()
        return
    
    if args.command == "run":
        cmd_run(args)
    elif args.command == "list-providers":
        cmd_list_providers(args)
    elif args.command == "results":
        cmd_results(args)
    elif args.command == "config":
        cmd_config(args)


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
    show_providers()


def cmd_results(args):
    show_results()


def cmd_config(args):
    config = Config()
    print("Current configuration:")
    for key, value in config.data.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
