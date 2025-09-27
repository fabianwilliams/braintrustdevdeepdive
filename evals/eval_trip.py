from braintrust import Eval
from autoevals import LLMClassifier
from agents.plan_trip import plan_trip

eval_data = [
    {"input": "Plan a trip from NYC to London next week", "expected": "flight"},
    {"input": "Do I need an umbrella in Paris tomorrow?", "expected": "weather"},
    {"input": "Find flights and tell me the weather in Madrid", "expected": "both"},
]

# The LLMClassifier asks a judge model to verify if expected info appears.
def judge_prompt(output: str, expected: str) -> str:
    return f"Does this answer include '{expected}' information? Reply strictly 'yes' or 'no'.\nAnswer to check: {output}"

Eval(
    "Travel Agent E2E",
    {
        "data": lambda: eval_data,
        "task": plan_trip,
        "scores": [LLMClassifier(judge_prompt)],
    },
)
