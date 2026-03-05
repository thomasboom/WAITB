# WAITB - Wordle AI Terminal Benchmark

Test and benchmark Large Language Models (LLMs) by having them play Wordle in the terminal.

## Features

- 🎯 Test multiple LLM providers (OpenAI, Anthropic, Google, Ollama, Groq)
- 📊 Track performance metrics (win rate, average attempts, response time)
- 💾 CSV results logging for analysis
- 🔧 Easy-to-extend provider architecture
- 🎨 Color-coded terminal output

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd WAITB

# Install the package
pip install -e .
```

**Requirements:** Python 3.10+

## Quick Start

### Interactive Mode

Run the interactive menu to configure and play:

```bash
waitb
# or
python -m waitb
```

### Command Line

```bash
# Run a single game with OpenAI
waitb run --provider openai --model gpt-4

# Run 10 games and save results
waitb run --provider anthropic --model claude-3 --games 10 --csv results.csv

# Test a local model with Ollama
waitb run --provider ollama --model llama2 --games 5
```

## Commands

| Command | Description |
|---------|-------------|
| `waitb` | Open interactive menu |
| `waitb run` | Run benchmark game(s) |
| `waitb list-providers` | Show available providers |
| `waitb results` | Display results summary |
| `waitb view` | Open results in browser |
| `waitb config` | Show current configuration |

## Run Options

```bash
waitb run [OPTIONS]

Options:
  -p, --provider TEXT   LLM provider (openai, anthropic, google, ollama, groq)
  -m, --model TEXT      Model name to use
  -g, --games INT       Number of games to play (default: 1)
  -w, --word TEXT       Specific target word (random if not set)
  --csv TEXT            Path to CSV results file
```

### Examples

```bash
# Test GPT-4 on a specific word
waitb run -p openai -m gpt-4 -w BRAIN

# Benchmark Claude with 20 games
waitb run -p anthropic -m claude-3-sonnet -g 20 --csv benchmark.csv

# Run local model (no API key needed)
waitb run -p ollama -m mistral -g 5
```

## Configuration

### API Keys

Set environment variables for cloud providers:

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."

# Google
export GOOGLE_API_KEY="..."

# Groq
export GROQ_API_KEY="gsk_..."
```

**Ollama** runs locally - no API key required. Install from [ollama.com](https://ollama.com).

### Config File

Create `~/.waitb/config.json` or `./waitb_config.json`:

```json
{
  "default_provider": "openai",
  "default_model": "gpt-4",
  "csv_path": "waitb_results.csv",
  "max_attempts": 6
}
```

## Word List

Wordle words are stored in `waitb/words/words.txt`:

- Lines **before** `-----`: Target words (possible solutions)
- Lines **after** `-----**: All valid guesses

Format:
```
APPLE
BEACH
BRAIN
-----
AAHED
AALII
ABACA
...
```

## Results

Results are saved to CSV with the following columns:

| Column | Description |
|--------|-------------|
| `timestamp` | ISO format timestamp |
| `provider` | LLM provider name |
| `model` | Model identifier |
| `word` | Target word |
| `attempts` | Number of guesses used |
| `won` | Game result (true/false) |
| `guess_times` | JSON array of response times per guess |
| `total_time` | Total game duration in seconds |

### View Results

```bash
# Show summary in terminal
waitb results

# Open in browser
waitb view

# Raw CSV
cat waitb_results.csv
```

## Adding a New Provider

1. Create `waitb/providers/yourprovider.py`:

```python
from .base import BaseProvider, Message

class YourProviderProvider(BaseProvider):
    name = "yourprovider"
    
    def chat(self, messages: list[Message], model: str = None) -> str:
        # Implement API call
        response = api.chat(model, messages)
        return response.content
    
    def get_api_key_env(self) -> str:
        return "YOURPROVIDER_API_KEY"
```

2. Register in `waitb/providers/__init__.py`:

```python
from .yourprovider import YourProviderProvider

PROVIDERS = {
    # ... existing providers
    "yourprovider": YourProviderProvider,
}
```

## Architecture

```
waitb/
├── __main__.py      # CLI entry point
├── wordle.py        # Game engine
├── results.py       # CSV logging
├── config.py        # Configuration handling
├── providers/       # LLM integrations
│   ├── base.py      # Abstract provider class
│   ├── openai.py
│   ├── anthropic.py
│   ├── google.py
│   ├── ollama.py
│   └── groq.py
└── words/
    └── words.txt    # Word lists
```

## License

AGPLv3 License - see LICENSE file for details.

## Contributing

Contributions welcome! Please read SPEC.md for project specifications before contributing.
