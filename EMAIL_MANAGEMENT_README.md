# Email Management Agent Evaluation System

A comprehensive Braintrust evaluation system for multi-agent email management scenarios, implementing both deterministic code-based scoring and LLM-as-a-Judge evaluation patterns.

## 🏗️ System Architecture

### Multi-Step Agent Pattern
Following Braintrust best practices with the **decision → tool → judge → compose** workflow:

1. **Decision Agent**: Analyzes user intent and determines required actions
2. **Tool Agents**: Execute email operations (auth, processing, search, categorization)
3. **Judge Agent**: Evaluates action appropriateness and effectiveness
4. **Composition Agent**: Creates comprehensive user-friendly responses

### Core Components

```
braintrustdevdeepdive/
├── agents/
│   ├── email_management.py                    # Core multi-step agent
│   ├── email_management_with_observability.py # Observable agent with OTel
│   └── mock_email_services.py                 # Mock SirFixAlotV2 infrastructure
├── scoring/
│   └── email_scoring.py                       # Dual scoring system
├── evals/
│   └── eval_email_management.py               # Comprehensive evaluation scenarios
├── observability/
│   └── email_otel_setup.py                    # Email-specific OpenTelemetry
├── run_email_evals.py                         # CLI evaluation runner
└── demo_email_agent.py                        # System demonstration
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Create configuration from template
cp .env.email.template .env

# Edit .env with your API keys
vim .env
```

### 2. Required Configuration

```bash
# Minimum required in .env
BRAINTRUST_API_KEY=your_braintrust_api_key
OPENAI_API_KEY=your_openai_api_key
PROJECT_NAME=EmailManagementEvals
```

### 3. Run Demonstration

```bash
# Test all components
python demo_email_agent.py

# Test setup only
python run_email_evals.py --test
```

### 4. Run Evaluations

```bash
# Run all evaluation scenarios
python run_email_evals.py --run all

# Run specific scenario types
python run_email_evals.py --run zero_inbox
python run_email_evals.py --run search
python run_email_evals.py --run errors

# Run with Braintrust CLI directly
braintrust eval evals/eval_email_management.py
```

## 📊 Evaluation Scenarios

### Core User Journey: Zero Inbox Achievement

**Scenario**: Multi-step workflow to achieve "zero inbox" across 4 email accounts:
- M365 Business (`adotob_primary`) - Device code auth
- Hotmail Personal (`hotmail_fabian_williams`) - Device code auth
- Gmail Primary (`gmail_fabsgwill`) - OAuth token
- Gmail Secondary (`gmail_jahmekyanbwoy`) - OAuth token

### Scenario Categories

1. **Zero Inbox Workflows** (3 scenarios)
   - Complete inbox clearing across all accounts
   - Business-focused account processing
   - Personal Gmail organization

2. **Search & Discovery** (4 scenarios)
   - Financial document search (Aidvantage loans)
   - Hybrid semantic + SQL search
   - Travel confirmation retrieval
   - Security alert identification

3. **Writing Analysis** (2 scenarios)
   - Communication style analysis
   - Business writing pattern review

4. **Multi-Account Triage** (2 scenarios)
   - Urgent email prioritization
   - Cross-account attention summary

5. **System Health** (2 scenarios)
   - Account status monitoring
   - Vector database health checks

6. **Error Handling** (2 scenarios)
   - Invalid account processing
   - Empty search result handling

## 🎯 Dual Scoring System

### Code-Based Judge (Deterministic)
Evaluates specific, measurable agent behaviors:

- **Action Appropriateness** (30%): Correct action selection
- **Efficiency** (25%): Minimal unnecessary operations
- **Completeness** (25%): All required aspects covered
- **Accuracy** (20%): Correct results and data

### LLM-as-a-Judge (Qualitative)
Assesses user experience and response quality:

- **General Quality**: Overall response assessment
- **User Experience**: Friendliness and clarity
- **Technical Accuracy**: Sound technical decisions
- **Completeness**: Comprehensive coverage

### Combined Scoring
Default weights: 60% code-based, 40% LLM-based
Configurable via `EMAIL_EVAL_MODE` environment variable.

## 🔍 Observability Features

### Email-Specific Semantic Conventions

```python
# Agent workflow attributes
agent.step = "decision" | "tool_execution" | "judgment" | "composition"
agent.decision = "zero_inbox" | "hybrid_search" | "process_inbox"
agent.reasoning = "Free text explanation"

# Email operation attributes
email.operation.type = "process_inbox" | "hybrid_search" | "categorize"
email.operation.account = "adotob_primary" | "gmail_fabsgwill"
email.operation.count = 25  # emails processed

# Search attributes
search.type = "vector" | "sql" | "hybrid"
search.query = "user search terms"
search.results.count = 5
```

### Tracing Integration

- **Braintrust Backend**: Automatic span collection and analysis
- **Azure Monitor**: Optional enterprise APM integration
- **Custom Dashboards**: Email-specific metrics and KPIs

## 🛠️ Configuration Options

### Environment Variables

```bash
# Evaluation Configuration
EMAIL_EVAL_MODE=dual              # dual, code_only, llm_only
EMAIL_EVAL_FOCUS=all              # all, zero_inbox, search, errors
USE_MOCK_EMAIL_SERVICES=true      # Use mock data for testing

# Model Configuration
USE_LOCAL_MODEL=false             # Use Ollama vs OpenAI
LOCAL_OPENAI_MODEL=llama3.3:70b   # Local model name
FRONTIER_MODEL=gpt-4o-mini        # OpenAI model

# Performance Settings
EVAL_MAX_CONCURRENCY=2            # Parallel evaluation limit
EVAL_OPERATION_TIMEOUT=30         # Individual operation timeout
```

## 📈 Performance Metrics

### Evaluation Benchmarks
- **Full Suite**: ~15 scenarios, 2-3 minutes runtime
- **Code Scoring**: >95% accuracy on deterministic criteria
- **LLM Scoring**: <10% variance between runs
- **Multi-step Tracing**: Complete observability of decision chains

### System Requirements
- **Memory**: ~512MB for mock services
- **CPU**: Moderate for LLM scoring
- **Network**: API calls to Braintrust and OpenAI/local models

## 🔧 Development Guide

### Adding New Scenarios

1. **Define Scenario** in `evals/eval_email_management.py`:
```python
{
    "input": "User query here",
    "expected": {
        "expected_actions": ["action1", "action2"],
        "required_accounts": ["account1"],
        "max_operations": 3,
        "should_succeed": True,
        "scenario_type": "custom_scenario"
    }
}
```

2. **Extend Scoring** in `scoring/email_scoring.py`:
```python
def _score_custom_criteria(self, expected, agent_data):
    # Custom scoring logic
    return score_between_0_and_1
```

3. **Add Observability** in `observability/email_otel_setup.py`:
```python
def trace_custom_operation(self, operation_data):
    span = self.tracer.start_span("custom_operation")
    # Add custom attributes
    return span
```

### Testing New Features

```bash
# Test specific scenarios
python run_email_evals.py --run custom --verbose

# Test scoring systems separately
python -c "
from scoring.email_scoring import DualEmailScorer
scorer = DualEmailScorer()
# Test custom scoring logic
"

# Test observability
python observability/email_otel_setup.py
```

## 🚦 CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Email Agent Evaluation
on: [pull_request]
jobs:
  eval:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"
    - name: Install dependencies
      run: pip install -r requirements.txt
    - name: Run Email Evaluations
      uses: braintrustdata/eval-action@v1
      with:
        api_key: ${{ secrets.BRAINTRUST_API_KEY }}
        runtime: python
        root: .
        eval-pattern: "evals/eval_email_management.py"
```

## 🔍 Troubleshooting

### Common Issues

1. **Mock Service Failures**
   ```bash
   # Verify mock services work
   python -c "
   from agents.mock_email_services import MockEmailService
   service = MockEmailService()
   print(service.get_system_status())
   "
   ```

2. **Authentication Errors**
   ```bash
   # Check API keys are set
   echo $BRAINTRUST_API_KEY
   echo $OPENAI_API_KEY
   ```

3. **Evaluation Failures**
   ```bash
   # Run with verbose logging
   EVAL_VERBOSE_LOGGING=true python run_email_evals.py --run all
   ```

4. **Observability Issues**
   ```bash
   # Test OpenTelemetry setup
   python observability/email_otel_setup.py
   ```

### Performance Optimization

- **Reduce Concurrency**: Lower `EVAL_MAX_CONCURRENCY` for stability
- **Use Code-Only Scoring**: Set `EMAIL_EVAL_MODE=code_only` for speed
- **Focus Evaluations**: Use `EMAIL_EVAL_FOCUS` for specific scenarios
- **Local Models**: Use Ollama for faster/cheaper evaluation

## 🎓 Key Learning Outcomes

This system demonstrates:

1. **Production-Ready Evaluation**: Real-world complexity beyond simple examples
2. **Multi-Dimensional Scoring**: Both deterministic and qualitative assessment
3. **Comprehensive Observability**: Business-specific telemetry and tracing
4. **Scalable Architecture**: Patterns applicable to other multi-agent scenarios
5. **CI/CD Integration**: Automated quality gates for agent development

## 📚 References

- [Braintrust Documentation](https://www.braintrust.dev/docs)
- [OpenTelemetry Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [SirFixAlotV2 Architecture](https://github.com/fabianwilliams/sirfixalotv2)
- [Multi-Agent Evaluation Patterns](https://www.braintrust.dev/docs/cookbook/recipes/PromptChaining)

---

**Next Steps**: Configure your environment, run the demonstration, and explore the evaluation results in the Braintrust UI!