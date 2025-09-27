import os
from dotenv import load_dotenv
from braintrust import Eval
from autoevals import Levenshtein
from braintrust import init_logger, wrap_openai

load_dotenv()

MODE = os.environ.get("HELLO_MODE", "basic")
USE_LOCAL = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

def task_basic(user_input: str) -> str:
    return "Hi " + user_input

def task_llm(name: str) -> str:
    project = os.getenv("PROJECT_NAME", "LocalDevProject")
    os.environ.setdefault("BRAINTRUST_PARENT", f"project_name:{project}")
    init_logger(project=project)

    if USE_LOCAL:
        from openai import OpenAI
        base_url = os.getenv("LOCAL_OPENAI_BASE_URL", "http://localhost:11434/v1")
        api_key = os.getenv("OPENAI_API_KEY", "ollama")
        model_name = os.getenv("LOCAL_OPENAI_MODEL", "llama3.3:70b")
        client = OpenAI(base_url=base_url, api_key=api_key)
    else:
        import openai
        client = wrap_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")))
        model_name = os.getenv("FRONTIER_MODEL", "gpt-4o-mini")

    resp = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": f"Say hello to {name} exactly as 'Hello, {name}!'"}],
        temperature=0.0,
    )
    return resp.choices[0].message.content.strip()

data = [
    {"input": "Alice", "expected": "Hello, Alice!" if MODE == "llm" else "Hi Alice"},
    {"input": "Bob",   "expected": "Hello, Bob!"   if MODE == "llm" else "Hi Bob"},
]

Eval(
    "Say Hi Bot" + (" (LLM)" if MODE == "llm" else ""),
    {
        "data": lambda: data,
        "task": (task_llm if MODE == "llm" else task_basic),
        "scores": [Levenshtein],
    },
)
