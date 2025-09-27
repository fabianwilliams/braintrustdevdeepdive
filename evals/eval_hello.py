import os
from dotenv import load_dotenv
from braintrust import Eval, init_logger, wrap_openai
from autoevals import Levenshtein

load_dotenv()

MODE = os.getenv("HELLO_MODE", "basic")  # 'basic' or 'llm'
USE_LOCAL = os.getenv("USE_LOCAL_MODEL", "false").lower() == "true"

def task_basic(user_input: str) -> str:
    return "Hi " + user_input

def task_llm(name: str) -> str:
    project = os.getenv("PROJECT_NAME", "Fabs27Sep25DeepDive")
    os.environ.setdefault("BRAINTRUST_PARENT", f"project_name:{project}")
    init_logger(project=project)

    import openai
    if USE_LOCAL:
        client = wrap_openai(
            openai.OpenAI(
                base_url=os.getenv("LOCAL_OPENAI_BASE_URL", "http://localhost:11434/v1"),
                api_key=os.getenv("OPENAI_API_KEY", "ollama"),
            )
        )
        model_name = os.getenv("LOCAL_OPENAI_MODEL", "gpt-oss:120b")
    else:
        client = wrap_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")))
        model_name = os.getenv("FRONTIER_MODEL", "gpt-4o-mini")

    resp = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": f"Say hello to {name} exactly as 'Hello, {name}!'"}],
        temperature=0.0,
    )
    return resp.choices[0].message.content.strip()

data = [
    {"input": "Fabian", "expected": "Hi, Fabian!" if MODE == "llm" else "Hi Fabian"},
    {"input": "Gabby",  "expected": "Hello, Gabby!"  if MODE == "llm" else "Hello Gabby"},
    {"input": "Vesa",   "expected": "Hi, Vesa!"   if MODE == "llm" else "Hi Vesa"},
    {"input": "Rob",    "expected": "Hello, Rob!"    if MODE == "llm" else "Hello Rob"},
    {"input": "Yina",   "expected": "Hi, Yina!"   if MODE == "llm" else "Hi Yina"},
]

Eval(
    os.getenv("EVAL_PROJECT_NAME", os.getenv("PROJECT_NAME", "Fabs27Sep25DeepDive")),
    task=(task_llm if MODE == "llm" else task_basic),
    data=lambda: data,
    scores=[Levenshtein],
)
