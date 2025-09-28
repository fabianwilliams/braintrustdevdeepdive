# evals/eval_trip.py
import os
from dotenv import load_dotenv
from braintrust import Eval

# Your agent entrypoint
from agents.plan_trip import plan_trip as task_fn

load_dotenv()

# -------- helpers --------
def _row_text(row):
    """Accept dict rows ({'input': ...}) or bare string rows."""
    if isinstance(row, dict):
        return row.get("input", row.get("text", ""))
    return str(row)

def _norm_choice(x):
    """Normalize model/agent output into a lowercase choice string."""
    if isinstance(x, str):
        return x.strip().lower()
    if isinstance(x, dict):
        # prefer explicit fields but fall back to any stringy content
        for k in ("choice", "raw", "output", "result"):
            if k in x and x[k]:
                return str(x[k]).strip().lower()
        return str(x).strip().lower()
    return str(x).strip().lower()

# -------- deterministic scorer (default / CI-safe) --------
def trip_scorer_rule(expected, output, row=None):
    exp = _norm_choice(expected)
    out = _norm_choice(output)
    return 1.0 if out == exp else 0.0

# -------- OPTIONAL LLM scorer (commented out) --------
# from autoevals import LLMClassifier
# import openai
# from braintrust import wrap_openai
#
# def trip_scorer_llm():
#     client = wrap_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")))
#     return LLMClassifier(
#         name="trip_scorer",
#         prompt_template=(
#             "Given results {results}, did I choose unnecessary actions? "
#             "Reply 'yes' or 'no'."
#         ),
#         choice_scores={"yes": 0.0, "no": 1.0},
#         client=client,
#         model=os.getenv("FRONTIER_MODEL", "gpt-4o-mini"),
#     )

def _get_scorers():
    use_llm = os.getenv("TRIP_SCORER", "rule").lower() == "llm"
    if use_llm and "trip_scorer_llm" in globals():
        return [trip_scorer_llm()]
    return [trip_scorer_rule]

# -------- dataset (dict rows; works even if Braintrust feeds strings) --------
DATA = [
    {"input": "Find flights and tell me the weather in Madrid!", "expected": "both"},
    {"input": "Plan a trip from NYC to LAX",                      "expected": "flight"},
    {"input": "Do I need an umbrella in Paris tomorrow?",        "expected": "weather"},
]

# -------- task wrapper --------
def task(row):
    text = _row_text(row)
    return task_fn(text)

# -------- eval definition --------
PROJECT = os.getenv("EVAL_PROJECT_NAME") or os.getenv("PROJECT_NAME") or "Fabs27Sep25DeepDive"

eval_run = Eval(
    PROJECT,
    data=lambda: DATA,          # can be replaced by a dataset later
    task=task,
    scores=_get_scorers(),
    # maxConcurrency=3,         # uncomment if you want to tune throughput
)

# (Run with `braintrust eval evals/eval_trip.py`)
