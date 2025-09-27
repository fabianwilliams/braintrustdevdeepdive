# Braintrust Dev Deep Dive (Personal Lab) 

This repository documents my **personal learning journey** exploring [Braintrust](https://www.braintrust.dev/) end-to-end: from simple AI agent evals, to multi-step workflows, observability with OpenTelemetry, and CI/CD integration. 

⚠️ **Note**: This is not an official Microsoft or Braintrust project. It’s my own lab work, and I’m sharing it openly so others can learn from my experiments. 

## Goals 
- Build and evaluate AI agents using Braintrust evals. 
- Compare local (Ollama) vs frontier (OpenAI, Anthropic) models. 
- Instrument agents with OpenTelemetry (OTel) for observability. 
- Forward telemetry to **Azure Application Insights**. 
- Integrate evals into **GitHub Actions CI/CD**. 

## Local Setup 

```bash 
git clone https://github.com/fabianwilliams/braintrustdevdeepdive 
cd braintrustdevdeepdive 
python3 -m venv .venv 
source .venv/bin/activate 
pip install -r requirements.txt 
``` 

Create a `.env` file: 

```bash 
BRAINTRUST_API_KEY="your_key_here" 
OPENAI_API_KEY="your_key_here" 
AZURE_MONITOR_CONNECTION_STRING="your_conn_str_here" 
``` 

## Usage 
- Run evals: 
```bash 
braintrust eval eval_hello.py 
``` 
- Explore traces in Braintrust UI or Azure Monitor. 
- Submit PRs to see GitHub Actions CI run evals automatically. 

This repo is meant to **document experiments** and invite collaboration. 
Feedback and forks are welcome! 

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