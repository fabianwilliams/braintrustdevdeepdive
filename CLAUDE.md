# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview
This is a Braintrust deep dive laboratory for experimenting with AI evaluation pipelines, from basic evals to multi-step agents, with full observability integration via OpenTelemetry (OTel).

## Development Setup

### Environment Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env  # then fill in your API keys
```

### Required Environment Variables
Configure these in `.env`:
- `BRAINTRUST_API_KEY`: Your Braintrust API key
- `PROJECT_NAME`: Braintrust project name (default: "Fabs27Sep25DeepDive")
- `OPENAI_API_KEY`: OpenAI API key
- `AZURE_MONITOR_CONNECTION_STRING`: (Optional) Azure Monitor connection string

### Local Model Configuration
For Ollama local models:
- `USE_LOCAL_MODEL=true`
- `LOCAL_OPENAI_BASE_URL=http://localhost:11434/v1`
- `LOCAL_OPENAI_MODEL=llama3.3:70b`

## Core Commands

### Running Evaluations
```bash
# Basic hello world eval
braintrust eval evals/eval_hello.py

# LLM-based hello eval
export HELLO_MODE=llm
braintrust eval evals/eval_hello.py

# Local model evaluation
export USE_LOCAL_MODEL=true
export LOCAL_OPENAI_MODEL="llama3.3:70b"
braintrust eval evals/eval_hello.py

# Multi-step agent evaluation
braintrust eval evals/eval_trip.py
```

### Observability
```bash
# Test OpenTelemetry setup
python observability/otel_setup.py
```

## Architecture

### Key Components
- **`evals/`**: Evaluation scripts (named `eval_*.py`)
  - `eval_hello.py`: Basic string matching and LLM greeting evaluations
  - `eval_trip.py`: Multi-step agent evaluation for trip planning
- **`agents/`**: Agent implementations
  - `plan_trip.py`: Multi-step agent with decision making, tool calling, and self-judgment
- **`observability/`**: OpenTelemetry configuration
  - `otel_setup.py`: Braintrust + Azure Monitor tracing setup

### Evaluation Patterns
1. **Basic Evals**: Direct function testing with deterministic scoring (Levenshtein distance)
2. **LLM Evals**: Wrapped OpenAI clients with Braintrust logging via `wrap_openai()`
3. **Agent Evals**: Multi-step agents with custom scoring functions

### Model Integration
- **Frontier Models**: OpenAI GPT models via direct API
- **Local Models**: Ollama models via OpenAI-compatible endpoint
- **Braintrust Integration**: All models wrapped with `wrap_openai()` for automatic logging
- **Project Scoping**: Uses `BRAINTRUST_PARENT=project_name:${PROJECT_NAME}` for organization

### Observability Stack
- **Braintrust**: Primary telemetry backend via `BraintrustSpanProcessor`
- **Azure Monitor**: Optional secondary backend via `AzureMonitorTraceExporter`
- **Project Setup**: Automatic logger initialization with `init_logger(project=...)`

## Development Patterns

### Adding New Evaluations
1. Create `evals/eval_<name>.py`
2. Import required Braintrust functions: `Eval`, `init_logger`, `wrap_openai`
3. Set up project scoping with `BRAINTRUST_PARENT` environment variable
4. Define data, task function, and scoring functions
5. Use `Eval()` constructor to create evaluation

### Agent Development
1. Place agent logic in `agents/` directory
2. Use helper functions for client setup (`_frontier_client()`, `_local_client()`)
3. Implement multi-step patterns: decision → tool → judge → compose
4. Handle both local and frontier model routing
5. Return structured outputs for evaluation

### Scoring Functions
- Use deterministic scorers for CI/CD reliability
- Consider LLM-based scorers (`autoevals.LLMClassifier`) for complex evaluations
- Environment variable toggles (e.g., `TRIP_SCORER=llm`) for scorer selection

## Code Conventions
- All secrets in `.env` file (never commit)
- Use `load_dotenv()` at module start
- Prefix evaluation files with `eval_`
- Wrap all OpenAI clients with `wrap_openai()` for telemetry
- Set `BRAINTRUST_PARENT` for project organization
- Handle exceptions gracefully in agent implementations