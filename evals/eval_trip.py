import os
from dotenv import load_dotenv
from braintrust import Eval
from autoevals import LLMClassifier
from agents.plan_trip import plan_trip

load_dotenv()

# Simple 3-case dataset
eval_data = [
    {"input": "Plan a trip from NYC to London next week", "expected": "flight"},
    {"input": "Do I need an umbrella in Paris tomorrow?", "expected": "weather"},
    {"input": "Find flights and tell me the weather in Madrid", "expected": "both"},
]

def judge_prompt(output: str, expected: str) -> str:
    return (
        "Does this answer include '{expected}' information? "
        "Reply strictly 'yes' or 'no'.\n"
        f"Answer to check: {output}"
    )

Eval(
    os.getenv("EVAL_PROJECT_NAME", os.getenv("PROJECT_NAME", "Fabs27Sep25DeepDive")),
    task=plan_trip,
    data=lambda: eval_data,
    scores=[LLMClassifier(judge_prompt)],
)
