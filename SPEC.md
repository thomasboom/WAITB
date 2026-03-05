# WAITB - Wordle AI Terminal Benchmark

## Project Overview

- **Project name**: WAITB (Wordle AI Terminal Benchmark)
- **Type**: Terminal-based AI benchmark tool
- **Core functionality**: Benchmark different LLM providers by having them play Wordle, with results stored in CSV for analysis
- **Target users**: Developers and researchers testing LLM capabilities

## UI/UX Specification

### Layout Structure

- Single terminal interface with clean output
- Progress indicators during game play
- Summary table after benchmark completion
- Color-coded feedback (green/yellow/gray for Wordle results)

### Visual Design

- **Color palette**:
  - Correct letter (green): `#2ecc71`
  - Wrong position (yellow): `#f39c12`
  - Not in word (gray): `#7f8c8d`
  - Primary text: `#ecf0f1`
  - Accent: `#3498db`
  - Error: `#e74c3c`

- **Typography**: Monospace terminal font
- **Spacing**: Clean line breaks between game states

### Components

1. **Game Display**: Shows current board state with color-coded letters
2. **Provider Selection**: Configure which LLM to test
3. **Results Table**: ASCII table showing benchmark results
4. **Configuration**: JSON/YAML config file for API keys

## Functionality Specification

### Core Features

1. **Wordle Game Engine**
   - Standard 5-letter word, 6 attempts
   - Standard Wordle coloring rules
   - Word list validation

2. **LLM Provider Support**
   - OpenAI (GPT-4, GPT-3.5)
   - Anthropic (Claude)
   - Google (Gemini)
   - Ollama (local models)
   - Groq
   - extensible provider interface

3. **Prompt Engineering**
   - System prompt instructing AI to play Wordle
   - Include game rules and previous attempts
   - Parse guess responses

4. **Benchmark Mode**
   - Run multiple games in sequence
   - Track: attempts, win/loss, time per guess, total time
   - Calculate success rate and average attempts

5. **CSV Results Logging**
   - Timestamp
   - Provider/model name
   - Word played
   - Attempts used
   - Win (true/false)
   - Time per guess
   - Total time
   - Raw conversation (optional)

### User Interactions

- CLI with subcommands: `run`, `list-providers`, `config`, `results`
- Config file at `~/.waitb/config.json` or `./config.json`
- Optional arguments: `--provider`, `--model`, `--games`, `--word`

### Edge Cases

- Invalid API keys: Clear error message
- Rate limiting: Retry with backoff
- Invalid guesses: Skip to next attempt
- Model doesn't respond: Mark as loss after timeout

## Acceptance Criteria

1. Can connect to at least 3 different LLM providers
2. Successfully plays Wordle game to completion
3. Results are accurately stored in CSV
4. CLI is functional with all subcommands
5. Handles errors gracefully with useful messages

## Technical Stack

- Python 3.10+
- No external framework dependencies (pure stdlib + httpx for API calls)
- Environment variables for API keys
