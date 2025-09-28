# SOP: Email Management Agent Experiment Execution

## 📋 Standard Operating Procedure for Running Email Management Agent Experiments

**Version**: 1.0
**Date**: September 28, 2025
**Purpose**: Step-by-step procedure to execute and evaluate email management agent experiments

---

## 🎯 Overview

This SOP covers the complete process from running the email management agent through Braintrust logging to creating evaluations from the results.

## 📋 Prerequisites

### Required Environment
- Braintrust account with API key configured
- OpenAI API key configured in Braintrust
- Python environment with requirements installed
- Project directory: `/Users/fabswill/ReposClaudeCode/braintrustdevdeepdive`

### Environment Variables Check
```bash
# Verify these are set
echo $BRAINTRUST_API_KEY
echo $OPENAI_API_KEY

# If not set, export them:
export BRAINTRUST_API_KEY="your_key_here"
export OPENAI_API_KEY="your_key_here"  # (or configure in Braintrust UI)
```

---

## 🚀 Phase 1: Execute Email Agent (Generate Logs)

### Step 1: Navigate to Project Directory
```bash
cd /Users/fabswill/ReposClaudeCode/braintrustdevdeepdive
```

### Step 2: Run Demo to Generate Logs
```bash
python demo_email_agent.py
```

**Expected Output**:
- Console output showing each demo section
- Logs appearing in Braintrust UI under your project
- No evaluation scores (since no evals defined yet)

### Step 3: Verify Logs in Braintrust
1. Open Braintrust UI: https://www.braintrust.dev/
2. Navigate to your project: `Fabs27Sep25DeepDive` (or current project name)
3. Go to **Logs** section
4. Verify you see traces for:
   - `process_email_request` (root spans)
   - Individual step spans: `decision_step`, `tool_execution_step`, etc.

### Step 4: Export Initial Results (Optional)
```bash
# If you want to export the raw logs
braintrust export --project "Fabs27Sep25DeepDive" --output logs_export.json
```

---

## 📊 Phase 2: Analyze Results and Create Evaluation Scenarios

### Step 5: Review Logged Interactions
In Braintrust UI:
1. Click on individual traces to see:
   - Input queries processed
   - Agent decisions made
   - Tool operations executed
   - Final responses generated
2. Identify successful patterns and edge cases
3. Note any unexpected behaviors or errors

### Step 6: Document Scenarios for Evaluation
Create a list of test scenarios based on what you observed:

**Example scenarios to capture**:
```markdown
1. System Status Query: "Give me a quick system status"
2. Zero Inbox Request: "Get all my inboxes to zero and categorize everything"
3. Specific Search: "Find emails about Aidvantage student loans"
4. Urgent Attention: "Show me what needs immediate attention"
5. Account Summary: "Give me a summary of all my email accounts"
```

---

## 🧪 Phase 3: Create Evaluation Framework

### Step 7: Create Evaluation Dataset
```bash
# Create new evaluation file
touch evals/eval_email_management_v2.py
```

### Step 8: Define Evaluation Structure
Based on Braintrust documentation patterns:

```python
# Template structure for evals/eval_email_management_v2.py
from braintrust import Eval
from agents.email_management import manage_emails
from scoring.email_scoring import DualEmailScorer

# Define test cases based on logged interactions
eval_data = [
    {
        "input": "Give me a quick system status",
        "expected": {
            "expected_actions": ["get_system_status"],
            "required_accounts": ["adotob_primary", "gmail_fabsgwill", "gmail_jahmekyanbwoy", "hotmail_fabian_williams"],
            "should_succeed": True,
            "scenario_type": "system_health"
        }
    },
    # Add more scenarios based on your logged interactions
]

Eval(
    "Email Management Agent v2",
    data=lambda: eval_data,
    task=manage_emails,  # Your agent function
    scores=[DualEmailScorer()]  # Your scoring function
)
```

### Step 9: Run Evaluation
```bash
braintrust eval evals/eval_email_management_v2.py
```

---

## 📈 Phase 4: Iterative Improvement

### Step 10: Analyze Evaluation Results
1. Review scores in Braintrust UI
2. Identify low-scoring scenarios
3. Compare agent outputs with expected results
4. Note areas for improvement

### Step 11: Refine Agent or Scoring
Based on results:
- Adjust agent prompts/logic
- Refine scoring criteria
- Add edge case handling

### Step 12: Re-run and Compare
```bash
# Run evaluation again after changes
braintrust eval evals/eval_email_management_v2.py
```

Compare results to see improvements.

---

## 🔧 Commands Reference

### Essential Commands
```bash
# Run agent demo (generates logs)
python demo_email_agent.py

# Run specific evaluation
braintrust eval evals/eval_email_management_v2.py

# Run all evaluations
python run_email_evals.py --run all

# Export data
braintrust export --project "ProjectName" --output filename.json

# Test setup only
python run_email_evals.py --test
```

### Debugging Commands
```bash
# Check Python syntax
python -m py_compile agents/email_management.py

# Test environment
python -c "import braintrust; print('Braintrust OK')"
python -c "import openai; print('OpenAI OK')"

# Verbose logging
EVAL_VERBOSE_LOGGING=true python demo_email_agent.py
```

---

## 🎯 Success Criteria

### Phase 1 Success
- ✅ Demo runs without errors
- ✅ Logs appear in Braintrust UI
- ✅ All agent steps traced properly
- ✅ Realistic email data processed

### Phase 2 Success
- ✅ Agent responses reviewed and documented
- ✅ Test scenarios identified from real interactions
- ✅ Edge cases and error conditions noted

### Phase 3 Success
- ✅ Evaluation file created with real scenarios
- ✅ Evaluation runs successfully
- ✅ Scores generated for all test cases
- ✅ Results provide actionable insights

---

## 🚨 Troubleshooting

### Common Issues
1. **"Not initialized" errors**: Check `BRAINTRUST_API_KEY` is set
2. **Import errors**: Verify `pip install -r requirements.txt` completed
3. **No logs appearing**: Check API key and network connectivity
4. **Evaluation failures**: Verify evaluation file syntax with `python -m py_compile`

### Log Locations
- Braintrust logs: UI → Project → Logs
- Python errors: Console output
- Evaluation results: UI → Project → Experiments

---

## 📝 Notes for Next Iteration

**Current Status**: Agent generates logs but no evaluations defined
**Next Goal**: Create evaluations from logged interactions
**Key Insight**: Use actual agent outputs as baseline for expected results

This SOP enables repeatable experimentation and continuous improvement of the email management agent through systematic evaluation.