# agents/email_management_with_observability.py
"""
Enhanced email management agent with full OpenTelemetry observability integration.
Demonstrates production-ready observability patterns for multi-step agents.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from braintrust import init_logger, wrap_openai, trace

from .mock_email_services import MockEmailService
from .email_management import EmailManagementAgent

# Import observability components
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from observability.email_otel_setup import setup_email_tracing, EmailOperationTracer

load_dotenv()


class ObservableEmailManagementAgent(EmailManagementAgent):
    """
    Email management agent with comprehensive OpenTelemetry instrumentation.
    Extends the base agent with detailed tracing and monitoring.
    """

    def __init__(self):
        super().__init__()

        # Initialize email-specific tracing
        self.email_tracer = setup_email_tracing()

        # Performance tracking
        self.operation_start_times = {}

    def process_email_request(self, user_query: str) -> str:
        """
        Main entry point with full observability instrumentation.
        """
        workflow_id = f"email_workflow_{datetime.now().timestamp()}"
        workflow_start_time = datetime.now()

        # Create main workflow span
        with self.email_tracer.trace_agent_workflow(user_query, workflow_id) as workflow_span:
            try:
                # Initialize OpenAI client
                client, model = self._get_openai_client()

                # Step 1: Decision with observability
                decision_result = self._analyze_user_intent_with_tracing(
                    client, model, user_query, workflow_span
                )

                # Step 2: Tool execution with observability
                tool_results = self._execute_email_operations_with_tracing(
                    decision_result, workflow_span
                )

                # Step 3: Judgment with observability
                judgment_result = self._judge_actions_with_tracing(
                    client, model, user_query, decision_result, tool_results, workflow_span
                )

                # Step 4: Composition with observability
                final_response = self._compose_response_with_tracing(
                    client, model, user_query, decision_result, tool_results,
                    judgment_result, workflow_span
                )

                # Add final performance metrics
                workflow_end_time = datetime.now()
                self.email_tracer.add_performance_metrics(
                    workflow_span, workflow_start_time, workflow_end_time
                )

                # Add success indicators to workflow span
                workflow_span.set_attribute("workflow.success", True)
                workflow_span.set_attribute("workflow.response_length", len(final_response))
                workflow_span.set_attribute("workflow.total_operations", len(tool_results.get("operations_performed", [])))

                return final_response

            except Exception as e:
                # Handle errors with proper tracing
                self.email_tracer.add_error_details(workflow_span, e)
                workflow_span.set_attribute("workflow.success", False)

                # Return error response
                return f"ERROR: Email management workflow failed: {type(e).__name__}: {e}"

    def _analyze_user_intent_with_tracing(self, client, model, user_query: str,
                                        parent_span) -> Dict[str, Any]:
        """Step 1: Decision analysis with detailed tracing."""

        with self.email_tracer.trace_decision_step(user_query, {}) as decision_span:
            decision_start_time = datetime.now()

            try:
                # Execute decision logic
                decision_result = self._analyze_user_intent(client, model, user_query)

                # Add decision details to span
                decision_span.set_attribute("decision.primary_action", decision_result.get("primary_action", "unknown"))
                decision_span.set_attribute("decision.urgency_level", decision_result.get("urgency_level", "medium"))
                decision_span.set_attribute("decision.target_accounts_count", len(decision_result.get("target_accounts", [])))

                # Add performance metrics
                self.email_tracer.add_performance_metrics(decision_span, decision_start_time)

                decision_span.set_attribute("decision.success", True)
                return decision_result

            except Exception as e:
                self.email_tracer.add_error_details(decision_span, e)
                raise

    def _execute_email_operations_with_tracing(self, decision: Dict[str, Any],
                                             parent_span) -> Dict[str, Any]:
        """Step 2: Tool execution with individual operation tracing."""

        primary_action = decision.get("primary_action", "get_system_status")
        secondary_actions = decision.get("secondary_actions", [])
        target_accounts = decision.get("target_accounts", [])
        search_query = decision.get("search_query", "")

        results = {
            "operations_performed": [],
            "successes": 0,
            "failures": 0,
            "operation_details": {}
        }

        try:
            # Execute primary action with tracing
            if primary_action == "zero_inbox":
                result = self._execute_zero_inbox_with_tracing(target_accounts)
                results["operation_details"]["zero_inbox"] = result
                results["operations_performed"].append("zero_inbox")
                results["successes"] += 1 if result.get("success") else 0
                results["failures"] += 0 if result.get("success") else 1

            elif primary_action == "hybrid_search":
                result = self._execute_search_with_tracing("hybrid", search_query)
                results["operation_details"]["hybrid_search"] = result
                results["operations_performed"].append("hybrid_search")
                results["successes"] += 1 if result.get("success") else 0
                results["failures"] += 0 if result.get("success") else 1

            elif primary_action == "process_inbox":
                inbox_results = {}
                for account in target_accounts:
                    account_result = self._execute_inbox_processing_with_tracing(account)
                    inbox_results[account] = account_result
                    results["successes"] += 1 if account_result.get("success") else 0
                    results["failures"] += 0 if account_result.get("success") else 1

                results["operation_details"]["process_inbox"] = inbox_results
                results["operations_performed"].append("process_inbox")

            elif primary_action == "get_system_status":
                result = self._execute_system_status_with_tracing()
                results["operation_details"]["system_status"] = result
                results["operations_performed"].append("get_system_status")
                results["successes"] += 1 if result.get("success") else 0
                results["failures"] += 0 if result.get("success") else 1

            # Execute secondary actions with tracing
            for action in secondary_actions:
                if action == "categorize_emails":
                    categorization_result = self._execute_categorization_with_tracing(results)
                    results["operation_details"]["categorize_emails"] = categorization_result
                    results["operations_performed"].append("categorize_emails")
                    results["successes"] += 1

            # Add overall tool execution metrics to parent span
            parent_span.set_attribute("tools.operations_count", len(results["operations_performed"]))
            parent_span.set_attribute("tools.success_count", results["successes"])
            parent_span.set_attribute("tools.failure_count", results["failures"])

            return results

        except Exception as e:
            results["failures"] += 1
            results["operation_details"]["error"] = str(e)
            parent_span.set_attribute("tools.error", str(e))
            return results

    def _execute_zero_inbox_with_tracing(self, target_accounts: List[str]) -> Dict[str, Any]:
        """Execute zero inbox with detailed tracing."""
        with self.email_tracer.trace_zero_inbox_operation(
            len(target_accounts), 0, False  # Will update with actual values
        ) as zero_inbox_span:

            zero_inbox_start_time = datetime.now()
            total_emails_processed = 0
            accounts_successfully_processed = 0

            try:
                # Execute the actual zero inbox logic
                result = self._execute_zero_inbox(target_accounts)

                # Update span with actual results
                total_emails_processed = result.get("total_emails_processed", 0)
                accounts_successfully_processed = result.get("accounts_processed", 0)
                achieved = result.get("success", False)

                zero_inbox_span.set_attribute("zero_inbox.emails_processed", total_emails_processed)
                zero_inbox_span.set_attribute("zero_inbox.accounts_processed", accounts_successfully_processed)
                zero_inbox_span.set_attribute("zero_inbox.achieved", achieved)

                # Add per-account details
                for account, details in result.get("account_details", {}).items():
                    if isinstance(details, dict) and "emails_found" in details:
                        zero_inbox_span.set_attribute(f"account.{account}.emails", details["emails_found"])
                        zero_inbox_span.set_attribute(f"account.{account}.urgent", details.get("urgent_emails", 0))

                # Add performance metrics
                self.email_tracer.add_performance_metrics(zero_inbox_span, zero_inbox_start_time)

                return result

            except Exception as e:
                self.email_tracer.add_error_details(zero_inbox_span, e)
                raise

    def _execute_search_with_tracing(self, search_type: str, query: str) -> Dict[str, Any]:
        """Execute search operations with tracing."""
        with self.email_tracer.trace_search_operation(search_type, query) as search_span:
            search_start_time = datetime.now()

            try:
                # Execute the actual search
                result = self.email_service.hybrid_search(query)

                # Update span with results
                search_span.set_attribute("search.total_results", result.get("total_results", 0))
                search_span.set_attribute("search.vector_results", result.get("vector_results", 0))
                search_span.set_attribute("search.sql_results", result.get("sql_results", 0))

                # Add top result score if available
                if result.get("results") and len(result["results"]) > 0:
                    top_score = result["results"][0].get("score", 0)
                    search_span.set_attribute("search.top_score", top_score)

                # Add performance metrics
                self.email_tracer.add_performance_metrics(search_span, search_start_time)

                return result

            except Exception as e:
                self.email_tracer.add_error_details(search_span, e)
                raise

    def _execute_inbox_processing_with_tracing(self, account: str) -> Dict[str, Any]:
        """Execute inbox processing with tracing."""
        with self.email_tracer.trace_email_operation("process_inbox", account) as inbox_span:
            inbox_start_time = datetime.now()

            try:
                # Execute the actual inbox processing
                result = self.email_service.process_inbox(account, 50)

                # Update span with results
                inbox_span.set_attribute("inbox.emails_processed", result.get("stats", {}).get("emails_processed", 0))
                inbox_span.set_attribute("inbox.auth_errors", result.get("stats", {}).get("authentication_errors", 0))
                inbox_span.set_attribute("inbox.api_errors", result.get("stats", {}).get("api_errors", 0))

                # Add performance metrics
                self.email_tracer.add_performance_metrics(inbox_span, inbox_start_time)

                return result

            except Exception as e:
                self.email_tracer.add_error_details(inbox_span, e)
                raise

    def _execute_system_status_with_tracing(self) -> Dict[str, Any]:
        """Execute system status check with tracing."""
        with self.email_tracer.tracer.start_span("system_status_check") as status_span:
            status_start_time = datetime.now()

            try:
                # Execute the actual system status check
                result = self.email_service.get_system_status()

                # Update span with results
                status_span.set_attribute("system.total_emails", result.get("total_emails", 0))
                status_span.set_attribute("system.accounts_configured", result.get("accounts_configured", 0))
                status_span.set_attribute("system.vector_count", result.get("vector_status", {}).get("vectors_count", 0))

                # Add performance metrics
                self.email_tracer.add_performance_metrics(status_span, status_start_time)

                return result

            except Exception as e:
                self.email_tracer.add_error_details(status_span, e)
                raise

    def _execute_categorization_with_tracing(self, previous_results: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email categorization with tracing."""
        emails_processed = sum([
            details.get("total_emails_processed", 0) if isinstance(details, dict) else 0
            for details in previous_results.get("operation_details", {}).values()
        ])

        categories = ["business", "personal", "newsletter", "travel", "finance"]
        success_rate = 0.9  # Mock success rate

        with self.email_tracer.trace_categorization_operation(
            emails_processed, categories, success_rate
        ) as cat_span:

            categorization_start_time = datetime.now()

            try:
                # Mock categorization results
                result = {
                    "success": True,
                    "emails_categorized": emails_processed,
                    "categories": categories,
                    "success_rate": success_rate
                }

                # Add performance metrics
                self.email_tracer.add_performance_metrics(cat_span, categorization_start_time)

                return result

            except Exception as e:
                self.email_tracer.add_error_details(cat_span, e)
                raise

    def _judge_actions_with_tracing(self, client, model, user_query: str,
                                  decision: Dict[str, Any], tool_results: Dict[str, Any],
                                  parent_span) -> Dict[str, Any]:
        """Step 3: Judgment with tracing."""

        with self.email_tracer.trace_judgment_step({}) as judgment_span:
            judgment_start_time = datetime.now()

            try:
                # Execute judgment logic
                judgment_result = self._judge_actions(client, model, user_query, decision, tool_results)

                # Add judgment details to span
                self.email_tracer.trace_judgment_step(judgment_result)

                # Add performance metrics
                self.email_tracer.add_performance_metrics(judgment_span, judgment_start_time)

                return judgment_result

            except Exception as e:
                self.email_tracer.add_error_details(judgment_span, e)
                raise

    def _compose_response_with_tracing(self, client, model, user_query: str,
                                     decision: Dict[str, Any], tool_results: Dict[str, Any],
                                     judgment: Dict[str, Any], parent_span) -> str:
        """Step 4: Response composition with tracing."""

        with self.email_tracer.trace_composition_step(0) as composition_span:  # Will update length
            composition_start_time = datetime.now()

            try:
                # Execute composition logic
                final_response = self._compose_response(client, model, user_query, decision, tool_results, judgment)

                # Update span with response details
                composition_span.set_attribute("composition.response_length", len(final_response))

                # Estimate user satisfaction based on success metrics
                user_satisfaction = min(
                    (tool_results["successes"] / max(1, tool_results["successes"] + tool_results["failures"])) +
                    (judgment.get("success_rating", 5) / 10),
                    1.0
                )
                composition_span.set_attribute("composition.estimated_satisfaction", user_satisfaction)

                # Add performance metrics
                self.email_tracer.add_performance_metrics(composition_span, composition_start_time)

                return final_response

            except Exception as e:
                self.email_tracer.add_error_details(composition_span, e)
                raise


# Main function for observable email management
def manage_emails_with_observability(user_query: str) -> str:
    """
    Main entry point for observable email management agent.
    Provides full OpenTelemetry instrumentation and monitoring.
    """
    agent = ObservableEmailManagementAgent()
    return agent.process_email_request(user_query)