#!/usr/bin/env python3
"""
Email Management Agent Demonstration
Shows the capabilities of the multi-step email management agent with observability.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Load environment
load_dotenv()
os.environ.setdefault("USE_MOCK_EMAIL_SERVICES", "true")
os.environ.setdefault("PROJECT_NAME", "EmailAgentDemo")


def demo_basic_agent():
    """Demonstrate basic email management agent."""
    print("\n" + "="*60)
    print("BASIC EMAIL MANAGEMENT AGENT DEMO")
    print("="*60)

    from agents.email_management import manage_emails

    scenarios = [
        "Get all my inboxes to zero and categorize everything",
        "Find emails about Aidvantage student loans",
        "Show me what needs immediate attention",
        "Give me a summary of all my email accounts"
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing: '{scenario}'")
        print("-" * 50)

        try:
            result = manage_emails(scenario)
            print(f"Response: {result[:200]}...")
            print("✓ Success")
        except Exception as e:
            print(f"✗ Error: {e}")


def demo_observable_agent():
    """Demonstrate email management agent with full observability."""
    print("\n" + "="*60)
    print("OBSERVABLE EMAIL MANAGEMENT AGENT DEMO")
    print("="*60)

    from agents.email_management_with_observability import manage_emails_with_observability

    scenarios = [
        {
            "query": "Process urgent emails from my business accounts",
            "description": "Multi-step workflow with categorization"
        },
        {
            "query": "Search for quarterly planning meetings using hybrid search",
            "description": "Hybrid search with vector and SQL components"
        },
        {
            "query": "Clear out my Gmail accounts and organize them",
            "description": "Zero inbox workflow with multiple accounts"
        }
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"\n{i}. Testing: '{scenario['query']}'")
        print(f"   Purpose: {scenario['description']}")
        print("-" * 60)

        try:
            result = manage_emails_with_observability(scenario["query"])
            print(f"Response: {result[:250]}...")
            print("✓ Success - Check Braintrust UI for detailed traces")
        except Exception as e:
            print(f"✗ Error: {e}")


def demo_scoring_system():
    """Demonstrate the dual scoring system."""
    print("\n" + "="*60)
    print("DUAL SCORING SYSTEM DEMO")
    print("="*60)

    from scoring.email_scoring import DualEmailScorer
    from agents.email_management import manage_emails

    scorer = DualEmailScorer()

    test_cases = [
        {
            "input": "Get all my inboxes to zero",
            "expected": {
                "expected_actions": ["zero_inbox", "categorize_emails"],
                "required_accounts": ["adotob_primary", "gmail_fabsgwill"],
                "max_operations": 3,
                "should_succeed": True,
                "min_emails": 2
            }
        },
        {
            "input": "Find emails about student loans",
            "expected": {
                "expected_actions": ["hybrid_search", "search_emails"],
                "required_accounts": [],
                "max_operations": 2,
                "should_succeed": True,
                "min_results": 1
            }
        }
    ]

    for i, case in enumerate(test_cases, 1):
        print(f"\n{i}. Evaluating: '{case['input']}'")
        print("-" * 50)

        try:
            # Get agent response
            output = manage_emails(case["input"])

            # Score the response
            evaluation = scorer.evaluate(case["expected"], output)

            print(f"Code Score: {evaluation.code_score:.2f}")
            print(f"LLM Score: {evaluation.llm_score:.2f}")
            print(f"Combined Score: {evaluation.combined_score:.2f}")

            print("\nCode Details:")
            for metric, score in evaluation.code_details.items():
                print(f"  {metric}: {score:.2f}")

            print("\nLLM Details:")
            for metric, score in evaluation.llm_details.items():
                print(f"  {metric}: {score:.2f}")

        except Exception as e:
            print(f"✗ Scoring error: {e}")


def demo_mock_services():
    """Demonstrate the mock email services."""
    print("\n" + "="*60)
    print("MOCK EMAIL SERVICES DEMO")
    print("="*60)

    from agents.mock_email_services import MockEmailService

    email_service = MockEmailService()

    # Test system status
    print("1. System Status:")
    status = email_service.get_system_status()
    print(f"   Total emails: {status['total_emails']}")
    print(f"   Accounts: {status['accounts_configured']}")
    print(f"   Vector status: {status['vector_status']['vectors_count']} vectors")

    # Test inbox processing
    print("\n2. Inbox Processing:")
    for account in ["adotob_primary", "gmail_fabsgwill"]:
        result = email_service.process_inbox(account, 5)
        if result["success"]:
            print(f"   {account}: {result['stats']['emails_processed']} emails")
        else:
            print(f"   {account}: Failed - {result.get('error', 'Unknown error')}")

    # Test search
    print("\n3. Search Operations:")
    search_queries = ["Aidvantage", "planning", "Madrid"]
    for query in search_queries:
        result = email_service.hybrid_search(query)
        print(f"   '{query}': {result['total_results']} results ({result['vector_results']} vector, {result['sql_results']} SQL)")


def demo_observability():
    """Demonstrate observability features."""
    print("\n" + "="*60)
    print("OBSERVABILITY FEATURES DEMO")
    print("="*60)

    from observability.email_otel_setup import setup_email_tracing, create_email_dashboard_metrics

    # Setup tracing
    print("1. Setting up OpenTelemetry tracing...")
    tracer = setup_email_tracing()
    print("   ✓ Email-specific tracer configured")

    # Show available metrics
    print("\n2. Available Dashboard Metrics:")
    metrics = create_email_dashboard_metrics()
    for metric, description in metrics.items():
        print(f"   {metric}: {description}")

    # Create sample spans
    print("\n3. Creating sample traces...")
    with tracer.trace_agent_workflow("Demo workflow") as workflow_span:
        with tracer.trace_decision_step("Demo decision", {
            "primary_action": "demo",
            "reasoning": "Demonstration purpose"
        }):
            pass

        with tracer.trace_email_operation("demo_operation", "demo_account", {
            "emails_processed": 5,
            "success": True
        }):
            pass

    print("   ✓ Sample traces created - Check Braintrust UI")


def main():
    """Run all demonstrations."""
    print("EMAIL MANAGEMENT AGENT SYSTEM DEMONSTRATION")
    print("This demo showcases the complete email management evaluation system")

    try:
        demo_mock_services()
        demo_basic_agent()
        demo_observable_agent()
        demo_scoring_system()
        demo_observability()

        print("\n" + "="*60)
        print("DEMONSTRATION COMPLETE")
        print("="*60)
        print("✓ All components demonstrated successfully")
        print("\nNext steps:")
        print("1. Configure your .env file with real API keys")
        print("2. Run evaluations: python run_email_evals.py --run all")
        print("3. Check Braintrust UI for detailed results and traces")
        print("4. Optional: Configure Azure Monitor for additional telemetry")

    except Exception as e:
        print(f"\n✗ Demo failed: {e}")
        print("\nTroubleshooting:")
        print("1. Ensure all required packages are installed")
        print("2. Check that environment variables are set correctly")
        print("3. Verify Braintrust API key is valid")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())