# Experiment Bravo: Converting Logs to Evaluations
## From Logged Interactions to Systematic Evaluation Framework

**Experiment Date:** September 28, 2025
**Prerequisites:** Completed Experiment Alpha with logged interactions
**GitHub Repo:** https://go.fabswill.com/braintrustdeepdive

This experiment focuses on converting your logged email management agent interactions into a systematic evaluation framework using Braintrust's dataset and evaluation features.

## 🎯 Experiment Objectives

1. **Extract Evaluation Scenarios**: Convert logged interactions into structured test cases
2. **Create Braintrust Datasets**: Build versioned datasets from real agent outputs
3. **Implement Systematic Scoring**: Score existing outputs to establish baselines
4. **Build Evaluation Framework**: Create reproducible evaluations for continuous improvement

## 📋 Prerequisites Check

Before starting, ensure you have:
- ✅ Completed Experiment Alpha with logs in Braintrust
- ✅ Access to Braintrust UI with your logged interactions
- ✅ Environment variables configured (`BRAINTRUST_API_KEY`, `OPENAI_API_KEY`)
- ✅ Python environment with requirements installed

## 🚀 Phase 1: Analyze Existing Logs

### Step 1: Run Agent Demo to Generate Fresh Logs
```bash
cd /Users/fabswill/ReposClaudeCode/braintrustdevdeepdive
python demo_email_agent.py
```

### Step 2: Review Logged Interactions in Braintrust UI
1. Open Braintrust UI: https://www.braintrust.dev/
2. Navigate to your project logs
3. Document the following for each successful interaction:
   - **Input query** (what user asked)
   - **Agent output** (what agent responded)
   - **Intermediate steps** (decision, tools used, judgment)
   - **Success indicators** (did it work as expected?)

### Step 3: Create Evaluation Scenarios Matrix
Create a spreadsheet or document tracking:

| Scenario ID | Input Query | Expected Behavior | Agent Output (Baseline) | Success? | Notes |
|-------------|-------------|-------------------|-------------------------|----------|-------|
| BRAVO-001 | "Give me a quick system status" | Should return email counts for all accounts | [Actual output from logs] | ✅ | Good baseline |
| BRAVO-002 | "Get all my inboxes to zero" | Should process emails from all accounts | [Actual output from logs] | ✅ | Check account coverage |
| BRAVO-003 | "Find emails about Aidvantage" | Should search and return relevant results | [Actual output from logs] | ❓ | Verify search accuracy |

## 🗃️ Phase 2: Create Braintrust Datasets

### Step 4: Create Dataset Creation Script
Create `scripts/create_dataset_from_logs.py`:

```python
from braintrust import initDataset
import json

# Initialize dataset
dataset = initDataset("EmailAgentEvals", {"dataset": "Real Interactions v1"})

# Define evaluation scenarios based on your logged interactions
scenarios = [
    {
        "input": "Give me a quick system status",
        "expected": {
            "action_type": "system_status",
            "accounts_checked": ["adotob_primary", "gmail_fabsgwill", "gmail_jahmekyanbwoy", "hotmail_fabian_williams"],
            "should_include_counts": True,
            "response_type": "summary"
        },
        "metadata": {
            "scenario_type": "system_health",
            "complexity": "low",
            "expected_duration_ms": 5000
        }
    },
    {
        "input": "Get all my inboxes to zero and categorize everything",
        "expected": {
            "action_type": "zero_inbox",
            "accounts_processed": ["adotob_primary", "gmail_fabsgwill", "gmail_jahmekyanbwoy", "hotmail_fabian_williams"],
            "should_categorize": True,
            "should_report_counts": True
        },
        "metadata": {
            "scenario_type": "zero_inbox",
            "complexity": "high",
            "expected_duration_ms": 15000
        }
    },
    {
        "input": "Find emails about Aidvantage student loans",
        "expected": {
            "action_type": "search",
            "search_type": "hybrid",
            "should_find_results": True,
            "accounts_searched": ["adotob_primary"]  # Based on your business context
        },
        "metadata": {
            "scenario_type": "search",
            "complexity": "medium",
            "expected_duration_ms": 8000
        }
    }
]

# Insert scenarios into dataset
for scenario in scenarios:
    dataset.insert(scenario)

print(f"Created dataset with {len(scenarios)} scenarios")
```

### Step 5: Run Dataset Creation
```bash
python scripts/create_dataset_from_logs.py
```

## 📊 Phase 3: Create Evaluation Framework

### Step 6: Create Enhanced Evaluation File
Create `evals/eval_email_from_logs.py`:

```python
from braintrust import Eval, initDataset
from agents.email_management import manage_emails
from scoring.email_scoring import DualEmailScorer
import json

# Load dataset created from logs
dataset = initDataset("EmailAgentEvals", {"dataset": "Real Interactions v1"})

def enhanced_email_scorer(expected, output):
    """
    Enhanced scorer that evaluates based on logged interaction patterns
    """
    scorer = DualEmailScorer()

    # Use the dual scoring system created in Alpha experiment
    result = scorer.evaluate(expected, output)

    return {
        "code_score": result.code_score,
        "llm_score": result.llm_score,
        "combined_score": result.combined_score,
        "details": {
            "code_details": result.code_details,
            "llm_details": result.llm_details
        }
    }

Eval(
    "Email Agent - From Logs to Evals",
    data=lambda: dataset,  # Use the dataset we created
    task=manage_emails,    # Your email management function
    scores=[enhanced_email_scorer]
)
```

### Step 7: Run Initial Evaluation
```bash
braintrust eval evals/eval_email_from_logs.py
```

## 🎯 Phase 4: Baseline Scoring and Analysis

### Step 8: Score Your Current Agent Performance
After running the evaluation:

1. **Review Results in Braintrust UI**:
   - Go to Experiments → "Email Agent - From Logs to Evals"
   - Note scores for each scenario
   - Identify low-performing areas

2. **Document Baseline Performance**:
   ```markdown
   ## Baseline Performance (Experiment Bravo)
   - System Status: 95% (strong performance)
   - Zero Inbox: 87% (good but room for improvement)
   - Search Queries: 73% (needs optimization)
   - Overall Average: 85%
   ```

### Step 9: Create Improvement Targets
Based on baseline scores, set improvement targets:

```python
# Add to your evaluation file
improvement_targets = {
    "system_status": {"current": 0.95, "target": 0.98},
    "zero_inbox": {"current": 0.87, "target": 0.93},
    "search": {"current": 0.73, "target": 0.85},
    "overall": {"current": 0.85, "target": 0.92}
}
```

## 🔄 Phase 5: Iterative Improvement Cycle

### Step 10: Identify Improvement Areas
Based on evaluation results:

1. **Low-scoring scenarios**: Focus on specific failure modes
2. **Consistency issues**: Look for scenarios with high variance
3. **Edge cases**: Add more challenging test cases

### Step 11: Implement Improvements
Make targeted improvements to:
- Agent prompts
- Tool selection logic
- Error handling
- Response formatting

### Step 12: Re-evaluate and Compare
```bash
# After making improvements
braintrust eval evals/eval_email_from_logs.py
```

Compare new results with baseline to measure improvement.

## 📈 Success Metrics

### Phase Completion Criteria

**Phase 1: Log Analysis ✅**
- [ ] Fresh logs generated
- [ ] At least 5 scenarios documented
- [ ] Success/failure patterns identified

**Phase 2: Dataset Creation ✅**
- [ ] Braintrust dataset created
- [ ] Scenarios properly structured with input/expected/metadata
- [ ] Dataset accessible in Braintrust UI

**Phase 3: Evaluation Framework ✅**
- [ ] Evaluation file created and runs successfully
- [ ] Scores generated for all scenarios
- [ ] Results viewable in Braintrust UI

**Phase 4: Baseline Analysis ✅**
- [ ] Baseline performance documented
- [ ] Improvement targets set
- [ ] Low-performing areas identified

**Phase 5: Improvement Cycle ✅**
- [ ] At least one improvement iteration completed
- [ ] Performance comparison between runs
- [ ] Documented improvement strategy

## 🚀 Commands for Execution

### Essential Commands
```bash
# Generate fresh logs
python demo_email_agent.py

# Create dataset from logs
python scripts/create_dataset_from_logs.py

# Run evaluation
braintrust eval evals/eval_email_from_logs.py

# Run all evaluations
python run_email_evals.py --run all

# Check evaluation syntax
python -m py_compile evals/eval_email_from_logs.py
```

### Debugging Commands
```bash
# Test dataset creation
python -c "from braintrust import initDataset; print('Dataset OK')"

# Verify evaluation structure
python -c "from evals.eval_email_from_logs import *; print('Eval OK')"

# Run with verbose output
EVAL_VERBOSE_LOGGING=true braintrust eval evals/eval_email_from_logs.py
```

## 🎯 Expected Outcomes

### Immediate Results
- Structured evaluation framework based on real logged interactions
- Baseline performance scores for all major scenarios
- Reproducible evaluation process

### Long-term Benefits
- Systematic approach to agent improvement
- Data-driven development cycle
- Quality assurance for agent changes
- Performance tracking over time

## 📝 Next Steps (Experiment Charlie)

After completing this experiment:

1. **Advanced Scoring**: Implement domain-specific scoring metrics
2. **CI/CD Integration**: Add evaluations to GitHub Actions
3. **Production Monitoring**: Set up alerts based on evaluation thresholds
4. **Human-in-the-Loop**: Add manual review for edge cases

---

This experiment transforms your ad-hoc logged interactions into a systematic evaluation framework, enabling data-driven improvement of your email management agent.