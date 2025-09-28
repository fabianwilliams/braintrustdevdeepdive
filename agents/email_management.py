# agents/email_management.py
"""
Multi-step email management agent for zero inbox and email processing scenarios.
Follows the decision → tool → judge → compose pattern from Braintrust best practices.
"""

import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dotenv import load_dotenv
from braintrust import init_logger, wrap_openai, start_span, traced

from .mock_email_services import MockEmailService

load_dotenv()


class EmailManagementAgent:
    """
    Multi-step agent for comprehensive email management scenarios.

    Agent Architecture:
    1. Decision Step: Analyze user intent and determine required actions
    2. Tool Steps: Execute email operations (auth, search, categorize, etc.)
    3. Judge Step: Evaluate if actions were appropriate and effective
    4. Compose Step: Provide comprehensive summary and recommendations
    """

    def __init__(self):
        self.project = os.getenv("PROJECT_NAME", "Fabs27Sep25DeepDive")
        os.environ.setdefault("BRAINTRUST_PARENT", f"project_name:{self.project}")
        init_logger(project=self.project)

        # Initialize email service (mock or real based on environment)
        self.use_mock = os.getenv("USE_MOCK_EMAIL_SERVICES", "true").lower() == "true"
        if self.use_mock:
            self.email_service = MockEmailService()
        else:
            # In real implementation, this would connect to actual SirFixAlotV2
            raise NotImplementedError("Real email service integration not implemented")

    def _get_openai_client(self):
        """Get configured OpenAI client with Braintrust wrapping."""
        import openai

        if os.getenv("USE_LOCAL_MODEL", "false").lower() == "true":
            client = wrap_openai(
                openai.OpenAI(
                    base_url=os.getenv("LOCAL_OPENAI_BASE_URL", "http://localhost:11434/v1"),
                    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
                )
            )
            model = os.getenv("LOCAL_OPENAI_MODEL", "llama3.3:70b")
        else:
            client = wrap_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")))
            model = os.getenv("FRONTIER_MODEL", "gpt-4o-mini")

        return client, model

    @traced
    def process_email_request(self, user_query: str) -> str:
        """
        Main entry point for email management requests.
        Implements the full multi-step agent workflow.
        """
        try:
            client, model = self._get_openai_client()
        except Exception as e:
            return f"ERROR: Failed to initialize OpenAI client: {type(e).__name__}: {e}"

        # Step 1: Decision - Analyze user intent
        decision_result = self._analyze_user_intent(client, model, user_query)

        # Step 2: Tools - Execute required email operations
        tool_results = self._execute_email_operations(decision_result)

        # Step 3: Judge - Evaluate effectiveness of actions
        judgment_result = self._judge_actions(client, model, user_query, decision_result, tool_results)

        # Step 4: Compose - Create comprehensive response
        final_response = self._compose_response(client, model, user_query, decision_result, tool_results, judgment_result)

        return final_response

    def _analyze_user_intent(self, client, model, user_query: str) -> Dict[str, Any]:
        """Step 1: Analyze user query to determine required actions."""

        with start_span(name="decision_step") as span:
            decision_prompt = f"""
        Analyze this email management request and determine the required actions:

        User Query: "{user_query}"

        Available Actions:
        - process_inbox: Process emails from specific accounts
        - search_emails: Search for specific content or topics
        - categorize_emails: Organize emails by business category
        - get_system_status: Check email counts and system health
        - hybrid_search: Use both semantic and SQL search
        - zero_inbox: Process all accounts to achieve zero inbox
        - draft_response: Analyze writing style and draft emails

        Available Accounts:
        - adotob_primary (Microsoft, business)
        - hotmail_fabian_williams (Microsoft, personal)
        - gmail_fabsgwill (Gmail, personal)
        - gmail_jahmekyanbwoy (Gmail, secondary)

        Respond with a JSON object containing:
        {{
            "primary_action": "main action to take",
            "secondary_actions": ["list", "of", "supporting", "actions"],
            "target_accounts": ["list", "of", "accounts"],
            "search_query": "search terms if applicable",
            "urgency_level": "low/medium/high",
            "reasoning": "explanation of analysis"
        }}
        """

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": decision_prompt}],
                temperature=0,
            )

            decision_text = response.choices[0].message.content.strip()

            # Try to parse JSON, fall back to structured response if needed
            try:
                decision_data = json.loads(decision_text)
            except json.JSONDecodeError:
                # Fallback: create structured response from text
                decision_data = self._parse_decision_fallback(decision_text, user_query)

            span.log(
                input={"query": user_query},
                output={
                    "decision_raw": decision_text,
                    "decision_parsed": decision_data
                },
                metadata={"step": "decision"}
            )

            return decision_data

        except Exception as e:
            # Fallback decision for error cases
            fallback_decision = {
                "primary_action": "get_system_status",
                "secondary_actions": [],
                "target_accounts": [],
                "search_query": "",
                "urgency_level": "medium",
                "reasoning": f"Error in decision analysis: {e}. Defaulting to system status check."
            }

            span.log(
                input={"query": user_query},
                output={"error": str(e), "fallback_decision": fallback_decision},
                metadata={"step": "decision", "error": True}
            )

            return fallback_decision

    def _parse_decision_fallback(self, decision_text: str, user_query: str) -> Dict[str, Any]:
        """Parse decision from text when JSON parsing fails."""
        query_lower = user_query.lower()

        # Simple keyword-based fallback logic
        if "zero inbox" in query_lower or "all" in query_lower:
            return {
                "primary_action": "zero_inbox",
                "secondary_actions": ["categorize_emails", "get_system_status"],
                "target_accounts": ["adotob_primary", "gmail_fabsgwill", "gmail_jahmekyanbwoy", "hotmail_fabian_williams"],
                "search_query": "",
                "urgency_level": "high",
                "reasoning": "Detected zero inbox request"
            }
        elif "search" in query_lower or "find" in query_lower:
            return {
                "primary_action": "hybrid_search",
                "secondary_actions": ["search_emails"],
                "target_accounts": [],
                "search_query": user_query,
                "urgency_level": "medium",
                "reasoning": "Detected search request"
            }
        elif "aidvantage" in query_lower or "student loan" in query_lower:
            return {
                "primary_action": "hybrid_search",
                "secondary_actions": ["search_emails"],
                "target_accounts": ["adotob_primary"],
                "search_query": "aidvantage student loan",
                "urgency_level": "high",
                "reasoning": "Detected financial/loan related query"
            }
        else:
            return {
                "primary_action": "get_system_status",
                "secondary_actions": ["process_inbox"],
                "target_accounts": ["adotob_primary"],
                "search_query": "",
                "urgency_level": "medium",
                "reasoning": "General email management request"
            }

    def _execute_email_operations(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Step 2: Execute the determined email operations."""

        with start_span(name="tool_execution_step") as span:
            results = {
                "operations_performed": [],
                "successes": 0,
                "failures": 0,
                "operation_details": {}
            }

            primary_action = decision.get("primary_action", "get_system_status")
            secondary_actions = decision.get("secondary_actions", [])
            target_accounts = decision.get("target_accounts", [])
            search_query = decision.get("search_query", "")

            try:
                # Execute primary action
                if primary_action == "zero_inbox":
                    result = self._execute_zero_inbox(target_accounts)
                    results["operation_details"]["zero_inbox"] = result
                    results["operations_performed"].append("zero_inbox")
                    results["successes"] += 1 if result.get("success") else 0
                    results["failures"] += 0 if result.get("success") else 1

                elif primary_action == "hybrid_search":
                    result = self.email_service.hybrid_search(search_query)
                    results["operation_details"]["hybrid_search"] = result
                    results["operations_performed"].append("hybrid_search")
                    results["successes"] += 1 if result.get("success") else 0
                    results["failures"] += 0 if result.get("success") else 1

                elif primary_action == "process_inbox":
                    inbox_results = {}
                    for account in target_accounts:
                        account_result = self.email_service.process_inbox(account, 50)
                        inbox_results[account] = account_result
                        results["successes"] += 1 if account_result.get("success") else 0
                        results["failures"] += 0 if account_result.get("success") else 1

                    results["operation_details"]["process_inbox"] = inbox_results
                    results["operations_performed"].append("process_inbox")

                elif primary_action == "get_system_status":
                    result = self.email_service.get_system_status()
                    results["operation_details"]["system_status"] = result
                    results["operations_performed"].append("get_system_status")
                    results["successes"] += 1 if result.get("success") else 0
                    results["failures"] += 0 if result.get("success") else 1

                # Execute secondary actions
                for action in secondary_actions:
                    if action == "categorize_emails" and "zero_inbox" in results["operations_performed"]:
                        # Mock categorization for emails processed in zero inbox
                        categorization_result = {"success": True, "emails_categorized": 15, "categories": ["business", "personal", "newsletter"]}
                        results["operation_details"]["categorize_emails"] = categorization_result
                        results["operations_performed"].append("categorize_emails")
                        results["successes"] += 1

                    elif action == "get_system_status" and "system_status" not in results["operations_performed"]:
                        result = self.email_service.get_system_status()
                        results["operation_details"]["system_status"] = result
                        results["operations_performed"].append("get_system_status")
                        results["successes"] += 1 if result.get("success") else 0
                        results["failures"] += 0 if result.get("success") else 1

                # Log tool execution
                span.log(
                    input={"decision": decision},
                    output=results,
                    metadata={"step": "tool_execution"}
                )

            except Exception as e:
                results["failures"] += 1
                results["operation_details"]["error"] = str(e)

                span.log(
                    input={"decision": decision},
                    output={"error": str(e)},
                    metadata={"step": "tool_execution", "error": True}
                )

            return results

    def _execute_zero_inbox(self, target_accounts: List[str]) -> Dict[str, Any]:
        """Execute zero inbox workflow across multiple accounts."""
        zero_inbox_results = {
            "success": True,
            "accounts_processed": 0,
            "total_emails_processed": 0,
            "categories_assigned": 0,
            "account_details": {}
        }

        for account in target_accounts:
            try:
                # Process inbox
                inbox_result = self.email_service.process_inbox(account, 100)  # Higher limit for zero inbox

                if inbox_result.get("success"):
                    account_summary = {
                        "emails_found": inbox_result["stats"]["emails_processed"],
                        "emails_categorized": inbox_result["stats"]["emails_processed"],  # Mock: all categorized
                        "urgent_emails": len([e for e in inbox_result.get("emails", []) if e.get("urgency", 0) > 7]),
                        "business_emails": len([e for e in inbox_result.get("emails", []) if e.get("category") in ["business", "consulting", "finance"]]),
                        "personal_emails": len([e for e in inbox_result.get("emails", []) if e.get("category") == "personal"])
                    }

                    zero_inbox_results["account_details"][account] = account_summary
                    zero_inbox_results["accounts_processed"] += 1
                    zero_inbox_results["total_emails_processed"] += account_summary["emails_found"]
                    zero_inbox_results["categories_assigned"] += account_summary["emails_categorized"]
                else:
                    zero_inbox_results["account_details"][account] = {"error": inbox_result.get("error", "Unknown error")}
                    zero_inbox_results["success"] = False

            except Exception as e:
                zero_inbox_results["account_details"][account] = {"error": str(e)}
                zero_inbox_results["success"] = False

        return zero_inbox_results

    def _judge_actions(self, client, model, user_query: str, decision: Dict[str, Any],
                      tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Step 3: Judge the effectiveness and appropriateness of actions taken."""

        with start_span(name="judgment_step") as span:
            judge_prompt = f"""
        Evaluate the effectiveness of the email management actions taken:

        Original User Query: "{user_query}"

        Decision Made: {json.dumps(decision, indent=2)}

        Actions Executed: {json.dumps(tool_results, indent=2)}

        Please evaluate:
        1. Were the chosen actions appropriate for the user's request?
        2. Were any unnecessary actions taken?
        3. Were any important actions missed?
        4. How effective were the results?
        5. Overall success rating (0-10)

        Respond with a JSON object:
        {{
            "actions_appropriate": true/false,
            "unnecessary_actions": ["list of unnecessary actions"],
            "missing_actions": ["list of missing actions"],
            "effectiveness_score": 0-10,
            "success_rating": 0-10,
            "reasoning": "detailed evaluation",
            "improvement_suggestions": ["list of suggestions"]
        }}
        """

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": judge_prompt}],
                temperature=0,
            )

            judgment_text = response.choices[0].message.content.strip()

            try:
                judgment_data = json.loads(judgment_text)
            except json.JSONDecodeError:
                # Fallback judgment
                judgment_data = self._create_fallback_judgment(tool_results)

            # Log the judgment step
            span.log(
                input={
                    "user_query": user_query,
                    "decision": decision,
                    "tool_results": tool_results
                },
                output={
                    "judgment_raw": judgment_text,
                    "judgment_parsed": judgment_data
                },
                metadata={"step": "judgment"}
            )

            return judgment_data

        except Exception as e:
            fallback_judgment = self._create_fallback_judgment(tool_results)
            fallback_judgment["reasoning"] += f" (Error in judgment: {e})"

            span.log(
                input={"user_query": user_query},
                output={"error": str(e), "fallback_judgment": fallback_judgment},
                metadata={"step": "judgment", "error": True}
            )

            return fallback_judgment

    def _create_fallback_judgment(self, tool_results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a basic judgment when LLM judgment fails."""
        success_rate = tool_results["successes"] / max(1, tool_results["successes"] + tool_results["failures"])

        return {
            "actions_appropriate": success_rate > 0.7,
            "unnecessary_actions": [],
            "missing_actions": [],
            "effectiveness_score": int(success_rate * 10),
            "success_rating": int(success_rate * 10),
            "reasoning": f"Automated judgment based on success rate: {success_rate:.2f}",
            "improvement_suggestions": ["Review error logs", "Check authentication"] if success_rate < 0.8 else []
        }

    def _compose_response(self, client, model, user_query: str, decision: Dict[str, Any],
                         tool_results: Dict[str, Any], judgment: Dict[str, Any]) -> str:
        """Step 4: Compose final comprehensive response to user."""

        with start_span(name="composition_step") as span:
            compose_prompt = f"""
        Create a comprehensive response to the user's email management request:

        User Query: "{user_query}"

        Actions Taken: {json.dumps(decision, indent=2)}

        Results: {json.dumps(tool_results, indent=2)}

        Evaluation: {json.dumps(judgment, indent=2)}

        Compose a helpful, informative response that:
        1. Summarizes what was accomplished
        2. Provides key insights from the results
        3. Highlights any important findings
        4. Suggests next steps if appropriate
        5. Is conversational and user-friendly

        Keep the response concise but informative.
        """

        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": compose_prompt}],
                temperature=0.3,  # Slightly higher for more natural language
            )

            final_response = response.choices[0].message.content.strip()

            # Log the composition step
            span.log(
                input={
                    "user_query": user_query,
                    "decision": decision,
                    "tool_results": tool_results,
                    "judgment": judgment
                },
                output={"final_response": final_response},
                metadata={"step": "composition"}
            )

            return final_response

        except Exception as e:
            # Fallback composition
            fallback_response = self._create_fallback_response(user_query, tool_results, judgment)

            span.log(
                input={"user_query": user_query},
                output={"error": str(e), "fallback_response": fallback_response},
                metadata={"step": "composition", "error": True}
            )

            return fallback_response

    def _create_fallback_response(self, user_query: str, tool_results: Dict[str, Any],
                                 judgment: Dict[str, Any]) -> str:
        """Create a basic response when LLM composition fails."""
        operations = ", ".join(tool_results["operations_performed"])
        success_count = tool_results["successes"]
        failure_count = tool_results["failures"]
        effectiveness = judgment.get("effectiveness_score", 5)

        return f"""Email Management Results:

Query: "{user_query}"

Operations completed: {operations}
Successful operations: {success_count}
Failed operations: {failure_count}
Effectiveness score: {effectiveness}/10

{self._format_operation_summary(tool_results)}

Status: {'SUCCESS' if success_count > failure_count else 'PARTIAL SUCCESS' if success_count > 0 else 'FAILED'}
"""

    def _format_operation_summary(self, tool_results: Dict[str, Any]) -> str:
        """Format a summary of operation results."""
        summary_parts = []

        for operation, details in tool_results["operation_details"].items():
            if operation == "zero_inbox" and details.get("success"):
                summary_parts.append(f"Zero Inbox: Processed {details['total_emails_processed']} emails across {details['accounts_processed']} accounts")
            elif operation == "hybrid_search" and details.get("success"):
                summary_parts.append(f"Search: Found {details['total_results']} relevant emails")
            elif operation == "system_status" and details.get("success"):
                summary_parts.append(f"System Status: {details['total_emails']} total emails across {details['accounts_configured']} accounts")
            elif operation == "process_inbox":
                processed_accounts = len([acc for acc, result in details.items() if result.get("success")])
                summary_parts.append(f"Inbox Processing: Successfully processed {processed_accounts} accounts")

        return "\n".join(summary_parts) if summary_parts else "No detailed results available."


# Main function for email management
def manage_emails(user_query: str) -> str:
    """
    Main entry point for email management agent.
    Processes user queries through the multi-step agent workflow.
    """
    agent = EmailManagementAgent()
    return agent.process_email_request(user_query)