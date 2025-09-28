# observability/email_otel_setup.py
"""
Extended OpenTelemetry setup for email management agent observability.
Implements email-specific semantic conventions and custom spans.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from braintrust.otel import BraintrustSpanProcessor

# Azure Monitor imports (optional)
AzureMonitorTraceExporter = None
try:
    from azure.monitor.opentelemetry.exporter import AzureMonitorTraceExporter as _AZ_Exporter
    AzureMonitorTraceExporter = _AZ_Exporter
except Exception:
    pass


class EmailSemanticConventions:
    """
    Semantic conventions for email management operations.
    Based on OpenTelemetry guidelines and custom email-specific attributes.
    """

    # Email operation attributes
    EMAIL_OPERATION_TYPE = "email.operation.type"
    EMAIL_OPERATION_ACCOUNT = "email.operation.account"
    EMAIL_OPERATION_COUNT = "email.operation.count"
    EMAIL_OPERATION_SUCCESS = "email.operation.success"
    EMAIL_OPERATION_ERROR = "email.operation.error"

    # Agent workflow attributes
    AGENT_STEP = "agent.step"
    AGENT_STEP_TYPE = "agent.step.type"
    AGENT_DECISION = "agent.decision"
    AGENT_REASONING = "agent.reasoning"
    AGENT_CONFIDENCE = "agent.confidence"

    # Email processing attributes
    EMAIL_ACCOUNT_TYPE = "email.account.type"  # gmail, microsoft, etc.
    EMAIL_AUTH_METHOD = "email.auth.method"    # oauth, device_code
    EMAIL_CATEGORIES_FOUND = "email.categories.found"
    EMAIL_URGENCY_LEVELS = "email.urgency.levels"

    # Search and vector attributes
    SEARCH_QUERY = "search.query"
    SEARCH_TYPE = "search.type"  # vector, sql, hybrid
    SEARCH_RESULTS_COUNT = "search.results.count"
    SEARCH_VECTOR_SCORE = "search.vector.score"

    # Performance attributes
    PROCESSING_TIME_MS = "processing.time.ms"
    BATCH_SIZE = "batch.size"
    CONCURRENT_OPERATIONS = "concurrent.operations"

    # Business logic attributes
    ZERO_INBOX_ACHIEVED = "zero_inbox.achieved"
    CATEGORIZATION_SUCCESS_RATE = "categorization.success_rate"
    USER_SATISFACTION_SCORE = "user.satisfaction.score"


class EmailOperationTracer:
    """
    Specialized tracer for email management operations with custom spans.
    """

    def __init__(self, tracer_name: str = "email_management_agent"):
        self.tracer = trace.get_tracer(tracer_name)
        self.conventions = EmailSemanticConventions()

    def trace_agent_workflow(self, user_query: str, workflow_id: str = None) -> trace.Span:
        """Create a span for the entire agent workflow."""
        span_name = "email_agent_workflow"
        span = self.tracer.start_span(span_name)

        # Set basic attributes
        span.set_attribute("user.query", user_query)
        span.set_attribute("workflow.id", workflow_id or f"workflow_{datetime.now().timestamp()}")
        span.set_attribute("agent.type", "email_management")
        span.set_attribute("workflow.start_time", datetime.now().isoformat())

        return span

    def trace_decision_step(self, user_query: str, decision_data: Dict[str, Any]) -> trace.Span:
        """Create a span for the agent's decision step."""
        span_name = "agent_decision"
        span = self.tracer.start_span(span_name)

        span.set_attribute(self.conventions.AGENT_STEP, "decision")
        span.set_attribute(self.conventions.AGENT_STEP_TYPE, "analysis")
        span.set_attribute("input.query", user_query)

        # Extract decision details
        primary_action = decision_data.get("primary_action", "unknown")
        secondary_actions = decision_data.get("secondary_actions", [])
        target_accounts = decision_data.get("target_accounts", [])
        urgency_level = decision_data.get("urgency_level", "medium")
        reasoning = decision_data.get("reasoning", "")

        span.set_attribute(self.conventions.AGENT_DECISION, primary_action)
        span.set_attribute(self.conventions.AGENT_REASONING, reasoning)
        span.set_attribute("decision.secondary_actions", ",".join(secondary_actions))
        span.set_attribute("decision.target_accounts", ",".join(target_accounts))
        span.set_attribute("decision.urgency_level", urgency_level)

        return span

    def trace_email_operation(self, operation_type: str, account_name: str,
                            operation_data: Optional[Dict[str, Any]] = None) -> trace.Span:
        """Create a span for email processing operations."""
        span_name = f"email_operation_{operation_type}"
        span = self.tracer.start_span(span_name)

        span.set_attribute(self.conventions.EMAIL_OPERATION_TYPE, operation_type)
        span.set_attribute(self.conventions.EMAIL_OPERATION_ACCOUNT, account_name)
        span.set_attribute(self.conventions.AGENT_STEP, "tool_execution")
        span.set_attribute(self.conventions.AGENT_STEP_TYPE, "email_processing")

        # Determine account type
        if "gmail" in account_name.lower():
            account_type = "gmail"
            auth_method = "oauth"
        elif "adotob" in account_name.lower() or "hotmail" in account_name.lower():
            account_type = "microsoft"
            auth_method = "device_code"
        else:
            account_type = "unknown"
            auth_method = "unknown"

        span.set_attribute(self.conventions.EMAIL_ACCOUNT_TYPE, account_type)
        span.set_attribute(self.conventions.EMAIL_AUTH_METHOD, auth_method)

        # Add operation-specific data
        if operation_data:
            if "emails_processed" in operation_data:
                span.set_attribute(self.conventions.EMAIL_OPERATION_COUNT, operation_data["emails_processed"])

            if "success" in operation_data:
                span.set_attribute(self.conventions.EMAIL_OPERATION_SUCCESS, operation_data["success"])

            if "error" in operation_data:
                span.set_attribute(self.conventions.EMAIL_OPERATION_ERROR, operation_data["error"])

        return span

    def trace_search_operation(self, search_type: str, query: str,
                             results: Optional[Dict[str, Any]] = None) -> trace.Span:
        """Create a span for search operations."""
        span_name = f"search_operation_{search_type}"
        span = self.tracer.start_span(span_name)

        span.set_attribute(self.conventions.SEARCH_TYPE, search_type)
        span.set_attribute(self.conventions.SEARCH_QUERY, query)
        span.set_attribute(self.conventions.AGENT_STEP, "tool_execution")
        span.set_attribute(self.conventions.AGENT_STEP_TYPE, "search")

        if results:
            total_results = results.get("total_results", 0)
            vector_results = results.get("vector_results", 0)
            sql_results = results.get("sql_results", 0)

            span.set_attribute(self.conventions.SEARCH_RESULTS_COUNT, total_results)
            span.set_attribute("search.vector_results", vector_results)
            span.set_attribute("search.sql_results", sql_results)

            # Add top search score if available
            if results.get("results") and len(results["results"]) > 0:
                top_score = results["results"][0].get("score", 0)
                span.set_attribute(self.conventions.SEARCH_VECTOR_SCORE, top_score)

        return span

    def trace_categorization_operation(self, emails_processed: int, categories: List[str],
                                     success_rate: float = 1.0) -> trace.Span:
        """Create a span for email categorization operations."""
        span_name = "email_categorization"
        span = self.tracer.start_span(span_name)

        span.set_attribute(self.conventions.EMAIL_OPERATION_TYPE, "categorization")
        span.set_attribute(self.conventions.EMAIL_OPERATION_COUNT, emails_processed)
        span.set_attribute(self.conventions.EMAIL_CATEGORIES_FOUND, ",".join(categories))
        span.set_attribute(self.conventions.CATEGORIZATION_SUCCESS_RATE, success_rate)
        span.set_attribute(self.conventions.AGENT_STEP, "tool_execution")
        span.set_attribute(self.conventions.AGENT_STEP_TYPE, "categorization")

        return span

    def trace_zero_inbox_operation(self, accounts_processed: int, total_emails: int,
                                 achieved: bool) -> trace.Span:
        """Create a span for zero inbox operations."""
        span_name = "zero_inbox_operation"
        span = self.tracer.start_span(span_name)

        span.set_attribute(self.conventions.EMAIL_OPERATION_TYPE, "zero_inbox")
        span.set_attribute(self.conventions.EMAIL_OPERATION_COUNT, total_emails)
        span.set_attribute(self.conventions.ZERO_INBOX_ACHIEVED, achieved)
        span.set_attribute("zero_inbox.accounts_processed", accounts_processed)
        span.set_attribute(self.conventions.AGENT_STEP, "tool_execution")
        span.set_attribute(self.conventions.AGENT_STEP_TYPE, "inbox_management")

        return span

    def trace_judgment_step(self, judgment_data: Dict[str, Any]) -> trace.Span:
        """Create a span for the agent's judgment step."""
        span_name = "agent_judgment"
        span = self.tracer.start_span(span_name)

        span.set_attribute(self.conventions.AGENT_STEP, "judgment")
        span.set_attribute(self.conventions.AGENT_STEP_TYPE, "evaluation")

        # Extract judgment details
        actions_appropriate = judgment_data.get("actions_appropriate", True)
        effectiveness_score = judgment_data.get("effectiveness_score", 5)
        success_rating = judgment_data.get("success_rating", 5)
        reasoning = judgment_data.get("reasoning", "")

        span.set_attribute("judgment.actions_appropriate", actions_appropriate)
        span.set_attribute("judgment.effectiveness_score", effectiveness_score)
        span.set_attribute("judgment.success_rating", success_rating)
        span.set_attribute(self.conventions.AGENT_REASONING, reasoning)

        # Add improvement suggestions if available
        improvements = judgment_data.get("improvement_suggestions", [])
        if improvements:
            span.set_attribute("judgment.improvement_suggestions", ",".join(improvements))

        return span

    def trace_composition_step(self, response_length: int, user_satisfaction: float = None) -> trace.Span:
        """Create a span for the agent's response composition step."""
        span_name = "agent_composition"
        span = self.tracer.start_span(span_name)

        span.set_attribute(self.conventions.AGENT_STEP, "composition")
        span.set_attribute(self.conventions.AGENT_STEP_TYPE, "response_generation")
        span.set_attribute("composition.response_length", response_length)

        if user_satisfaction is not None:
            span.set_attribute(self.conventions.USER_SATISFACTION_SCORE, user_satisfaction)

        return span

    def add_performance_metrics(self, span: trace.Span, start_time: datetime,
                              end_time: Optional[datetime] = None) -> None:
        """Add performance metrics to an existing span."""
        if end_time is None:
            end_time = datetime.now()

        processing_time_ms = int((end_time - start_time).total_seconds() * 1000)
        span.set_attribute(self.conventions.PROCESSING_TIME_MS, processing_time_ms)

    def add_error_details(self, span: trace.Span, error: Exception) -> None:
        """Add error information to a span."""
        span.set_attribute("error.type", type(error).__name__)
        span.set_attribute("error.message", str(error))
        span.set_status(trace.Status(trace.StatusCode.ERROR, str(error)))


def setup_email_tracing():
    """
    Set up OpenTelemetry tracing for email management operations.
    Configures both Braintrust and optional Azure Monitor exporters.
    """
    load_dotenv()

    project_name = os.getenv("PROJECT_NAME", "Fabs27Sep25DeepDive")
    os.environ.setdefault("BRAINTRUST_PARENT", f"project_name:{project_name}")

    # Create tracer provider
    provider = TracerProvider()
    trace.set_tracer_provider(provider)

    # Add Braintrust span processor
    braintrust_api_key = os.getenv("BRAINTRUST_API_KEY", "")
    if braintrust_api_key:
        provider.add_span_processor(
            BraintrustSpanProcessor(api_key=braintrust_api_key)
        )

    # Add Azure Monitor span processor (optional)
    azure_conn_string = os.getenv("AZURE_MONITOR_CONNECTION_STRING", "")
    if azure_conn_string and AzureMonitorTraceExporter is not None:
        azure_exporter = AzureMonitorTraceExporter(connection_string=azure_conn_string)
        provider.add_span_processor(BatchSpanProcessor(azure_exporter))

    # Create and return email-specific tracer
    return EmailOperationTracer()


def create_email_dashboard_metrics() -> Dict[str, Any]:
    """
    Generate metrics for email management dashboard.
    These could be used with Azure Monitor or other APM tools.
    """
    return {
        "email_operations_per_hour": "Count of email operations",
        "avg_processing_time_ms": "Average email processing time",
        "zero_inbox_success_rate": "Percentage of successful zero inbox operations",
        "search_accuracy_score": "Average relevance score for search results",
        "categorization_accuracy": "Percentage of correctly categorized emails",
        "user_satisfaction_score": "Average user satisfaction with agent responses",
        "auth_failure_rate": "Percentage of authentication failures",
        "error_rate_by_account_type": "Error rates grouped by email provider",
        "concurrent_operations": "Number of simultaneous operations",
        "agent_decision_confidence": "Average confidence in agent decisions"
    }


if __name__ == "__main__":
    # Test the email tracing setup
    print("Setting up email management observability...")

    tracer = setup_email_tracing()
    print("✓ OpenTelemetry tracer configured")

    # Test span creation
    with tracer.trace_agent_workflow("Test email processing workflow") as workflow_span:
        with tracer.trace_decision_step("Process my inbox", {
            "primary_action": "process_inbox",
            "target_accounts": ["adotob_primary"],
            "urgency_level": "medium",
            "reasoning": "Test decision"
        }) as decision_span:
            pass

        with tracer.trace_email_operation("process_inbox", "adotob_primary", {
            "emails_processed": 5,
            "success": True
        }) as email_span:
            pass

        with tracer.trace_search_operation("hybrid", "test query", {
            "total_results": 3,
            "vector_results": 2,
            "sql_results": 1
        }) as search_span:
            pass

    print("✓ Test spans created successfully")

    # Print dashboard metrics info
    metrics = create_email_dashboard_metrics()
    print(f"✓ {len(metrics)} dashboard metrics defined")

    print("\nEmail observability setup complete!")
    print(f"Project: {os.getenv('PROJECT_NAME', 'Fabs27Sep25DeepDive')}")
    print(f"Braintrust enabled: {'Yes' if os.getenv('BRAINTRUST_API_KEY') else 'No'}")
    print(f"Azure Monitor enabled: {'Yes' if os.getenv('AZURE_MONITOR_CONNECTION_STRING') and AzureMonitorTraceExporter else 'No'}")