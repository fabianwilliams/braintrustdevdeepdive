# Braintrust Dev Deep Dive (Personal Lab)

This repository documents my **personal learning journey** exploring Braintrust end-to-end:
simple evals → multi-step agents → observability with OpenTelemetry → CI/CD.

⚠️ Note: This is not an official Microsoft or Braintrust project.

## Goals
- Build and evaluate AI agents using Braintrust evals
- Compare local (Ollama) vs frontier (OpenAI, Anthropic) models
- Add observability with OpenTelemetry (`BraintrustSpanProcessor` + project scoping)
- Optionally mirror telemetry to **Azure Application Insights**
- Automate evals in **GitHub Actions CI/CD**

## Setup

```bash
git clone https://github.com/fabianwilliams/braintrustdevdeepdive
cd braintrustdevdeepdive
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.template .env  # then fill values
``` 

Create a `.env` file: 

```bash 
BRAINTRUST_API_KEY=sk-...
PROJECT_NAME=Fabs27Sep25DeepDive
OPENAI_API_KEY=your_openai_key 
AZURE_MONITOR_CONNECTION_STRING="your_conn_str_here" 
``` 

## Usage 

- Hello evals: 
```bash 
braintrust eval eval_hello.py 
``` 

## LLM Mode
```bash
export HELLO_MODE=llm
braintrust eval evals/eval_hello.py
```

## LOCAL model
```bash
export USE_LOCAL_MODEL=true
export LOCAL_OPENAI_MODEL="llama3.3:70b"
braintrust eval evals/eval_hello.py
```

## Multi Step Agent Eval
```bash
braintrust eval evals/eval_trip.py
```

## Observability

```bash
python observability/otel_setup.py
```
## CI/CD
Add BRAINTRUST_API_KEY to GitHub Secrets
Open a PR or push to main to trigger the eval workflow

Runs and agents are logged to Braintrust (scoped to $PROJECT_NAME).
Optionally forward to Azure Monitor via AZURE_MONITOR_CONNECTION_STRING.

- Explore traces in Braintrust UI or Azure Monitor. 
- Submit PRs to see GitHub Actions CI run evals automatically. 

This repo is meant to **document experiments** and invite collaboration. 
Feedback and forks are welcome! 

## Folder Structure
```text
evals/
  eval_hello.py        # Hello evaluation (string match + LLM variant)
  eval_trip.py         # Multi-step agent eval with LLMClassifier
agents/
  plan_trip.py         # Agent logic (decision -> tool -> judge -> compose)
observability/
  otel_setup.py        # OTel config (Braintrust + optional Azure)
.github/workflows/run-evals.yml
requirements.txt
.env.template
.gitignore
AGENT_GUIDE.md
```

--- 

# Agent Coding Guide: Braintrust Lab Context

This document brings coding assistants up to speed on the **current plan**.

## Project Context
- Repo: `braintrustdevdeepdive`
- Language: Python 3.10+
- Environment: MacOS, VS Code, Ollama local models, Docker Desktop
- Core libraries: `braintrust`, `autoevals`, `openai`, `opentelemetry-sdk`

## Objectives
1. Create & run evals (Hello World → multi-step agent).
2. Integrate **local (Ollama)** and **frontier (OpenAI/Anthropic)** models.
3. Add **OpenTelemetry observability** (Braintrust backend + Azure Monitor).
4. Automate evals in **GitHub Actions CI/CD**.

## Development Guidelines
- Always **use `.env` for secrets** and `.gitignore` to exclude it.
- Eval scripts should be named `eval_*.py`.
- Instrument spans with OTel semantic conventions (`ai.model.id`, `ai.prompt`, `ai.response`).
- For multi-step agents, log custom traces (`braintrust.trace()`).

## Coding Tasks for Agents
- Generate eval datasets (synthetic or task-specific).
- Wrap OpenAI / local models with Braintrust proxy.
- Add/modify CI workflows (`.github/workflows/run-evals.yml`).
- Extend observability by tagging spans with context (`gen_ai.conversation.id`, `gen_ai.feedback`).

## Collaboration Mode
- I will experiment interactively and may diverge from this plan.
- Coding assistants should suggest eval cases, observability improvements, and error handling.
- Assume all work should be **CI/CD ready** with eval regression checks.