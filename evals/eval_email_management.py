# evals/eval_email_management.py
"""
Comprehensive evaluation scenarios for email management agent.
Implements both deterministic and LLM-based scoring for complex multi-agent workflows.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from braintrust import Eval

# Add the project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from agents.email_management import manage_emails
from scoring.email_scoring import email_code_scorer, email_llm_scorer, email_dual_scorer

load_dotenv()


# -------- Helper Functions --------
def _row_text(row):
    """Accept dict rows ({'input': ...}) or bare string rows."""
    if isinstance(row, dict):
        return row.get("input", row.get("text", ""))
    return str(row)


def _get_scorers():
    """Get scoring functions based on environment configuration."""
    eval_mode = os.getenv("EMAIL_EVAL_MODE", "dual").lower()

    if eval_mode == "code_only":
        return [email_code_scorer]
    elif eval_mode == "llm_only":
        return [email_llm_scorer()]
    else:  # dual mode (default)
        return [email_code_scorer, email_llm_scorer(), email_dual_scorer]


# -------- Evaluation Datasets --------

# Core Zero Inbox Scenarios
ZERO_INBOX_DATA = [
    {
        "input": "Get all my inboxes to zero and categorize everything",
        "expected": {
            "expected_actions": ["zero_inbox", "categorize_emails", "get_system_status"],
            "required_accounts": ["adotob_primary", "gmail_fabsgwill", "gmail_jahmekyanbwoy", "hotmail_fabian_williams"],
            "required_data_points": ["email_count", "success_confirmation"],
            "max_operations": 4,
            "should_succeed": True,
            "min_emails": 5,
            "scenario_type": "zero_inbox"
        }
    },
    {
        "input": "Clear out my business email accounts and organize them by priority",
        "expected": {
            "expected_actions": ["process_inbox", "categorize_emails"],
            "required_accounts": ["adotob_primary"],
            "required_data_points": ["email_count", "success_confirmation"],
            "max_operations": 3,
            "should_succeed": True,
            "min_emails": 2,
            "scenario_type": "business_focus"
        }
    },
    {
        "input": "Process all my personal Gmail accounts and get them organized",
        "expected": {
            "expected_actions": ["process_inbox", "categorize_emails"],
            "required_accounts": ["gmail_fabsgwill", "gmail_jahmekyanbwoy"],
            "required_data_points": ["email_count", "success_confirmation"],
            "max_operations": 3,
            "should_succeed": True,
            "min_emails": 1,
            "scenario_type": "personal_focus"
        }
    }
]

# Specific Search Scenarios
SEARCH_DATA = [
    {
        "input": "Find all emails about Aidvantage student loans from the last 6 months",
        "expected": {
            "expected_actions": ["hybrid_search", "search_emails"],
            "required_accounts": ["adotob_primary"],  # Business account likely has loan emails
            "required_data_points": ["search_results", "success_confirmation"],
            "max_operations": 2,
            "should_succeed": True,
            "min_results": 1,
            "scenario_type": "financial_search"
        }
    },
    {
        "input": "Search for quarterly planning meetings using both semantic and SQL filtering",
        "expected": {
            "expected_actions": ["hybrid_search"],
            "required_accounts": [],  # Cross-account search
            "required_data_points": ["search_results", "vector_results", "sql_results"],
            "max_operations": 2,
            "should_succeed": True,
            "min_results": 1,
            "scenario_type": "hybrid_search"
        }
    },
    {
        "input": "Look for travel confirmations and flight information in my Gmail",
        "expected": {
            "expected_actions": ["search_emails", "hybrid_search"],
            "required_accounts": ["gmail_fabsgwill"],
            "required_data_points": ["search_results", "success_confirmation"],
            "max_operations": 2,
            "should_succeed": True,
            "min_results": 1,
            "scenario_type": "travel_search"
        }
    },
    {
        "input": "Find security alerts from Microsoft across all my accounts",
        "expected": {
            "expected_actions": ["hybrid_search", "search_emails"],
            "required_accounts": ["adotob_primary", "hotmail_fabian_williams"],
            "required_data_points": ["search_results", "success_confirmation"],
            "max_operations": 3,
            "should_succeed": True,
            "min_results": 1,
            "scenario_type": "security_search"
        }
    }
]

# Writing Style and Analysis Scenarios
WRITING_ANALYSIS_DATA = [
    {
        "input": "Analyze my writing style from sent emails and draft a response to the latest customer inquiry",
        "expected": {
            "expected_actions": ["process_inbox", "search_emails"],  # Would need sent items processing
            "required_accounts": ["adotob_primary"],
            "required_data_points": ["writing_analysis", "draft_response"],
            "max_operations": 4,
            "should_succeed": True,
            "min_emails": 1,
            "scenario_type": "writing_analysis"
        }
    },
    {
        "input": "Review my business communication patterns and suggest improvements",
        "expected": {
            "expected_actions": ["process_inbox", "categorize_emails"],
            "required_accounts": ["adotob_primary"],
            "required_data_points": ["communication_analysis", "improvement_suggestions"],
            "max_operations": 3,
            "should_succeed": True,
            "min_emails": 2,
            "scenario_type": "communication_analysis"
        }
    }
]

# Multi-Account Triage Scenarios
TRIAGE_DATA = [
    {
        "input": "Process urgent emails from my business accounts and defer personal ones",
        "expected": {
            "expected_actions": ["process_inbox", "categorize_emails"],
            "required_accounts": ["adotob_primary"],
            "required_data_points": ["urgency_classification", "business_personal_split"],
            "max_operations": 3,
            "should_succeed": True,
            "min_emails": 2,
            "scenario_type": "urgency_triage"
        }
    },
    {
        "input": "Show me what needs immediate attention across all my email accounts",
        "expected": {
            "expected_actions": ["process_inbox", "categorize_emails", "get_system_status"],
            "required_accounts": ["adotob_primary", "gmail_fabsgwill", "gmail_jahmekyanbwoy", "hotmail_fabian_williams"],
            "required_data_points": ["urgency_summary", "account_status"],
            "max_operations": 4,
            "should_succeed": True,
            "min_emails": 3,
            "scenario_type": "urgent_summary"
        }
    }
]

# System Status and Health Check Scenarios
SYSTEM_DATA = [
    {
        "input": "Give me a summary of all my email accounts and their current status",
        "expected": {
            "expected_actions": ["get_system_status"],
            "required_accounts": [],
            "required_data_points": ["account_summary", "email_counts", "system_health"],
            "max_operations": 1,
            "should_succeed": True,
            "min_emails": 0,
            "scenario_type": "status_check"
        }
    },
    {
        "input": "Check if my email processing and vector search systems are working properly",
        "expected": {
            "expected_actions": ["get_system_status"],
            "required_accounts": [],
            "required_data_points": ["system_health", "vector_status"],
            "max_operations": 2,
            "should_succeed": True,
            "min_emails": 0,
            "scenario_type": "health_check"
        }
    }
]

# Edge Cases and Error Scenarios
ERROR_DATA = [
    {
        "input": "Process emails from nonexistent_account@fake.com",
        "expected": {
            "expected_actions": ["process_inbox"],
            "required_accounts": [],
            "required_data_points": ["error_handling"],
            "max_operations": 1,
            "should_succeed": False,  # Should fail gracefully
            "min_emails": 0,
            "scenario_type": "invalid_account"
        }
    },
    {
        "input": "Search for emails about a topic that doesn't exist in my mailbox",
        "expected": {
            "expected_actions": ["hybrid_search", "search_emails"],
            "required_accounts": [],
            "required_data_points": ["empty_results", "no_results_message"],
            "max_operations": 2,
            "should_succeed": True,  # Should succeed with empty results
            "min_results": 0,
            "scenario_type": "no_results"
        }
    }
]

# -------- Combined Dataset --------
ALL_EMAIL_DATA = (
    ZERO_INBOX_DATA +
    SEARCH_DATA +
    WRITING_ANALYSIS_DATA +
    TRIAGE_DATA +
    SYSTEM_DATA +
    ERROR_DATA
)


# -------- Task Wrapper --------
def email_task(row):
    """Wrapper function to call the email management agent."""
    text = _row_text(row)
    return manage_emails(text)


# -------- Evaluation Definitions --------

# Main comprehensive evaluation
PROJECT = os.getenv("EVAL_PROJECT_NAME") or os.getenv("PROJECT_NAME") or "Fabs27Sep25DeepDive"

email_management_eval = Eval(
    PROJECT,
    data=lambda: ALL_EMAIL_DATA,
    task=email_task,
    scores=_get_scorers(),
    metadata={
        "description": "Comprehensive email management agent evaluation",
        "version": "1.0",
        "scenarios": [
            "zero_inbox", "search", "writing_analysis",
            "triage", "system_status", "error_handling"
        ],
        "scoring_types": ["deterministic", "llm_judge", "hybrid"]
    }
    # maxConcurrency=2,  # Limit concurrency for stability
)

# Focused evaluations for specific scenarios
zero_inbox_eval = Eval(
    f"{PROJECT}_ZeroInbox",
    data=lambda: ZERO_INBOX_DATA,
    task=email_task,
    scores=_get_scorers(),
    metadata={
        "description": "Zero inbox achievement scenarios",
        "focus": "inbox_processing"
    }
)

search_eval = Eval(
    f"{PROJECT}_Search",
    data=lambda: SEARCH_DATA,
    task=email_task,
    scores=_get_scorers(),
    metadata={
        "description": "Email search and discovery scenarios",
        "focus": "search_capabilities"
    }
)

error_handling_eval = Eval(
    f"{PROJECT}_ErrorHandling",
    data=lambda: ERROR_DATA,
    task=email_task,
    scores=_get_scorers(),
    metadata={
        "description": "Error handling and edge case scenarios",
        "focus": "robustness"
    }
)

# -------- Conditional Evaluations Based on Environment --------

# Run different evaluations based on EMAIL_EVAL_FOCUS environment variable
eval_focus = os.getenv("EMAIL_EVAL_FOCUS", "all").lower()

if eval_focus == "zero_inbox":
    # Only run zero inbox scenarios
    focused_eval = zero_inbox_eval
elif eval_focus == "search":
    # Only run search scenarios
    focused_eval = search_eval
elif eval_focus == "errors":
    # Only run error handling scenarios
    focused_eval = error_handling_eval
else:
    # Run all scenarios (default)
    focused_eval = email_management_eval


# -------- Performance Testing Evaluation --------

# Lightweight dataset for performance testing
PERFORMANCE_DATA = [
    {
        "input": "Quick system status check",
        "expected": {
            "expected_actions": ["get_system_status"],
            "required_accounts": [],
            "max_operations": 1,
            "should_succeed": True,
            "scenario_type": "performance_test"
        }
    },
    {
        "input": "Fast inbox check for adotob",
        "expected": {
            "expected_actions": ["process_inbox"],
            "required_accounts": ["adotob_primary"],
            "max_operations": 1,
            "should_succeed": True,
            "scenario_type": "performance_test"
        }
    }
]

performance_eval = Eval(
    f"{PROJECT}_Performance",
    data=lambda: PERFORMANCE_DATA,
    task=email_task,
    scores=[email_code_scorer],  # Only code scoring for speed
    metadata={
        "description": "Performance and speed testing",
        "focus": "performance"
    }
)


if __name__ == "__main__":
    # Print evaluation configuration when run directly
    print("Email Management Evaluation Configuration:")
    print(f"Project: {PROJECT}")
    print(f"Eval Mode: {os.getenv('EMAIL_EVAL_MODE', 'dual')}")
    print(f"Eval Focus: {os.getenv('EMAIL_EVAL_FOCUS', 'all')}")
    print(f"Use Mock Services: {os.getenv('USE_MOCK_EMAIL_SERVICES', 'true')}")
    print(f"Total Scenarios: {len(ALL_EMAIL_DATA)}")
    print("\nScenario Types:")
    scenario_counts = {}
    for item in ALL_EMAIL_DATA:
        scenario_type = item["expected"]["scenario_type"]
        scenario_counts[scenario_type] = scenario_counts.get(scenario_type, 0) + 1

    for scenario_type, count in sorted(scenario_counts.items()):
        print(f"  {scenario_type}: {count} scenarios")