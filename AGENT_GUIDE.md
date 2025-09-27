# Agent Coding Guide

This guide brings coding assistants up to speed on the current plan.

## Project Context
- Repo: `braintrustdevdeepdive`
- Language: Python 3.10+
- Environment: macOS, VS Code, Ollama local models, Docker Desktop
- Core libraries: `braintrust`, `autoevals`, `openai`, `opentelemetry-sdk`

## Objectives
1. Create and run evals (Hello World → multi-step agent)
2. Integrate **local (Ollama)** and **frontier (OpenAI/Anthropic)** models
3. Add **OpenTelemetry observability** (Braintrust backend + Azure Monitor)
4. Automate evals in **GitHub Actions CI/CD**

## Development Guidelines
- Always use `.env` for secrets and exclude it with `.gitignore`
- Place eval scripts in `evals/` and name them `eval_*.py`
- Use Braintrust helpers:  
  - `wrap_openai()` for frontier OpenAI client  
  - `init_logger(project=...)` for logging  
  - Ensure `BRAINTRUST_PARENT=project_name:${PROJECT_NAME}` is set
- Emit step-level details with `braintrust.trace()`

## Tasks for Coding Agents
- Generate new eval datasets
- Wrap OpenAI / local models via Braintrust proxy
- Extend CI workflows (`.github/workflows/run-evals.yml`)
- Improve observability (e.g., add `gen_ai.conversation.id`, `gen_ai.feedback` attributes)

## Collaboration Mode
- I may diverge from this plan interactively
- Assistants should suggest eval cases, observability improvements, and error handling
- All work should be **CI/CD ready** with regression evals