# scoring/email_scoring.py
"""
Dual scoring system for email management agent evaluation.
Implements both deterministic code-based scoring and LLM-as-a-Judge evaluation.
"""

import os
import json
import re
from typing import Dict, Any, List, Union, Optional
from dataclasses import dataclass
from braintrust import wrap_openai
from autoevals import LLMClassifier


@dataclass
class EmailEvaluationResult:
    """Result of email agent evaluation."""
    code_score: float
    llm_score: float
    combined_score: float
    code_details: Dict[str, Any]
    llm_details: Dict[str, Any]
    evaluation_metadata: Dict[str, Any]


class CodeBasedEmailScorer:
    """
    Deterministic, rule-based scoring for email management agent actions.
    Evaluates specific, measurable aspects of agent performance.
    """

    def __init__(self):
        self.scoring_weights = {
            "action_appropriateness": 0.3,  # Did agent choose right actions?
            "efficiency": 0.25,             # Avoided unnecessary operations?
            "completeness": 0.25,           # Covered all required aspects?
            "accuracy": 0.2                 # Correct results and data?
        }

    def score_email_agent_output(self, expected: Dict[str, Any], output: str, row: Optional[Dict] = None) -> float:
        """
        Main scoring function for email agent evaluation.

        Args:
            expected: Expected behavior and results
            output: Agent's actual output (string response)
            row: Additional context data

        Returns:
            Score between 0.0 and 1.0
        """
        try:
            # Parse the agent output to extract structured information
            agent_data = self._parse_agent_output(output)

            # Calculate individual component scores
            action_score = self._score_action_appropriateness(expected, agent_data)
            efficiency_score = self._score_efficiency(expected, agent_data)
            completeness_score = self._score_completeness(expected, agent_data)
            accuracy_score = self._score_accuracy(expected, agent_data)

            # Calculate weighted total score
            total_score = (
                action_score * self.scoring_weights["action_appropriateness"] +
                efficiency_score * self.scoring_weights["efficiency"] +
                completeness_score * self.scoring_weights["completeness"] +
                accuracy_score * self.scoring_weights["accuracy"]
            )

            return min(max(total_score, 0.0), 1.0)  # Clamp to [0, 1]

        except Exception as e:
            # Return low score for unparseable or error outputs
            return 0.1

    def _parse_agent_output(self, output: str) -> Dict[str, Any]:
        """Extract structured data from agent's text output."""
        parsed_data = {
            "actions_mentioned": [],
            "accounts_processed": [],
            "email_counts": {},
            "error_indicators": [],
            "success_indicators": [],
            "operation_types": []
        }

        output_lower = output.lower()

        # Extract actions mentioned
        action_patterns = {
            "zero_inbox": r"zero inbox|inbox.*zero|get.*inbox.*zero",
            "search": r"search|find|found|looking for",
            "process_inbox": r"process.*inbox|inbox.*process",
            "categorize": r"categor|classify|organized",
            "hybrid_search": r"hybrid.*search|semantic.*search|vector.*search",
            "system_status": r"system.*status|status.*check|total.*emails"
        }

        for action, pattern in action_patterns.items():
            if re.search(pattern, output_lower):
                parsed_data["actions_mentioned"].append(action)

        # Extract account references
        account_patterns = {
            "adotob_primary": r"adotob|business|primary",
            "gmail_fabsgwill": r"gmail.*fab|fabsgwill",
            "gmail_jahmekyanbwoy": r"gmail.*jah|jahmekyanbwoy",
            "hotmail_fabian_williams": r"hotmail|fabian.*williams"
        }

        for account, pattern in account_patterns.items():
            if re.search(pattern, output_lower):
                parsed_data["accounts_processed"].append(account)

        # Extract numerical data
        email_count_match = re.search(r"(\d+).*emails?", output_lower)
        if email_count_match:
            parsed_data["email_counts"]["total"] = int(email_count_match.group(1))

        # Detect success/failure indicators
        success_patterns = [
            r"success", r"completed", r"finished", r"accomplished",
            r"processed.*\d+", r"found.*\d+", r"categorized.*\d+"
        ]
        for pattern in success_patterns:
            if re.search(pattern, output_lower):
                parsed_data["success_indicators"].append(pattern)

        error_patterns = [
            r"error", r"failed", r"unable", r"couldn't", r"authentication.*failed"
        ]
        for pattern in error_patterns:
            if re.search(pattern, output_lower):
                parsed_data["error_indicators"].append(pattern)

        return parsed_data

    def _score_action_appropriateness(self, expected: Dict[str, Any], agent_data: Dict[str, Any]) -> float:
        """Score whether the agent chose appropriate actions for the request."""
        expected_actions = set(expected.get("expected_actions", []))
        agent_actions = set(agent_data.get("actions_mentioned", []))

        if not expected_actions:
            return 1.0  # No specific actions expected

        # Calculate overlap between expected and actual actions
        correct_actions = len(expected_actions.intersection(agent_actions))
        missing_actions = len(expected_actions - agent_actions)
        extra_actions = len(agent_actions - expected_actions)

        # Score based on precision and recall
        precision = correct_actions / max(len(agent_actions), 1)
        recall = correct_actions / max(len(expected_actions), 1)

        # Penalize for missing or extra actions
        completeness_penalty = missing_actions * 0.2
        efficiency_penalty = extra_actions * 0.1

        score = (precision + recall) / 2 - completeness_penalty - efficiency_penalty
        return max(score, 0.0)

    def _score_efficiency(self, expected: Dict[str, Any], agent_data: Dict[str, Any]) -> float:
        """Score efficiency - avoiding unnecessary operations."""
        max_expected_operations = expected.get("max_operations", 3)
        actual_operations = len(agent_data.get("actions_mentioned", []))

        # Perfect efficiency score if within expected range
        if actual_operations <= max_expected_operations:
            return 1.0

        # Penalize for excessive operations
        excess_operations = actual_operations - max_expected_operations
        penalty = excess_operations * 0.2
        return max(1.0 - penalty, 0.0)

    def _score_completeness(self, expected: Dict[str, Any], agent_data: Dict[str, Any]) -> float:
        """Score completeness - covering all required aspects."""
        required_accounts = set(expected.get("required_accounts", []))
        processed_accounts = set(agent_data.get("accounts_processed", []))

        required_data_points = expected.get("required_data_points", [])
        provided_data_points = []

        # Check for presence of required data points
        if "email_count" in required_data_points:
            if agent_data.get("email_counts", {}).get("total", 0) > 0:
                provided_data_points.append("email_count")

        if "success_confirmation" in required_data_points:
            if agent_data.get("success_indicators"):
                provided_data_points.append("success_confirmation")

        # Score account coverage
        account_score = 1.0
        if required_accounts:
            account_coverage = len(required_accounts.intersection(processed_accounts)) / len(required_accounts)
            account_score = account_coverage

        # Score data point coverage
        data_score = 1.0
        if required_data_points:
            data_coverage = len(provided_data_points) / len(required_data_points)
            data_score = data_coverage

        return (account_score + data_score) / 2

    def _score_accuracy(self, expected: Dict[str, Any], agent_data: Dict[str, Any]) -> float:
        """Score accuracy of results and data."""
        accuracy_score = 1.0

        # Check for error indicators when success is expected
        if expected.get("should_succeed", True):
            if agent_data.get("error_indicators"):
                accuracy_score -= 0.5

        # Check for success indicators when success is expected
        if expected.get("should_succeed", True):
            if not agent_data.get("success_indicators"):
                accuracy_score -= 0.3

        # Validate email counts if expected
        expected_min_emails = expected.get("min_emails", 0)
        actual_emails = agent_data.get("email_counts", {}).get("total", 0)

        if expected_min_emails > 0 and actual_emails < expected_min_emails:
            accuracy_score -= 0.4

        return max(accuracy_score, 0.0)


class LLMEmailJudge:
    """
    LLM-based evaluation of email management agent responses.
    Provides qualitative assessment of user experience and response quality.
    """

    def __init__(self):
        self.client = self._setup_client()
        self.model = os.getenv("FRONTIER_MODEL", "gpt-4o-mini")

    def _setup_client(self):
        """Setup OpenAI client with Braintrust wrapping."""
        import openai

        if os.getenv("USE_LOCAL_MODEL", "false").lower() == "true":
            client = wrap_openai(
                openai.OpenAI(
                    base_url=os.getenv("LOCAL_OPENAI_BASE_URL", "http://localhost:11434/v1"),
                    api_key=os.getenv("OPENAI_API_KEY", "ollama"),
                )
            )
        else:
            client = wrap_openai(openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY", "")))

        return client

    def create_llm_scorer(self) -> LLMClassifier:
        """Create an LLM-based classifier for email agent evaluation."""
        return LLMClassifier(
            name="email_agent_judge",
            prompt_template="""
            Evaluate this email management agent response for overall quality and user experience:

            User Query: {input}
            Agent Response: {output}
            Expected Behavior: {expected}

            Rate the response on these criteria:
            1. Helpfulness: Does it address the user's needs?
            2. Clarity: Is the response clear and understandable?
            3. Completeness: Does it cover all important aspects?
            4. Professionalism: Is the tone appropriate?
            5. Actionability: Does it provide useful next steps?

            Respond with one of these ratings:
            - "excellent": Outstanding response that exceeds expectations
            - "good": Solid response that meets most needs
            - "satisfactory": Adequate response with minor issues
            - "needs_improvement": Response has significant issues
            - "poor": Response fails to meet basic requirements

            Consider both the technical accuracy and user experience quality.
            """,
            choice_scores={
                "excellent": 1.0,
                "good": 0.8,
                "satisfactory": 0.6,
                "needs_improvement": 0.4,
                "poor": 0.2
            },
            client=self.client,
            model=self.model,
        )

    def create_specific_criteria_scorer(self, criteria: str) -> LLMClassifier:
        """Create a scorer for specific evaluation criteria."""
        criteria_prompts = {
            "user_experience": """
            Focus specifically on user experience quality:
            - Is the response user-friendly and conversational?
            - Does it provide clear status updates?
            - Would a typical user find this helpful?
            - Does it avoid technical jargon appropriately?
            """,
            "technical_accuracy": """
            Focus specifically on technical accuracy:
            - Are the operations described technically sound?
            - Do the numbers and statistics make sense?
            - Are error conditions handled appropriately?
            - Is the workflow logical and efficient?
            """,
            "completeness": """
            Focus specifically on response completeness:
            - Does it address all aspects of the user query?
            - Are important details included?
            - Does it provide sufficient context?
            - Are any critical steps or information missing?
            """
        }

        prompt_addition = criteria_prompts.get(criteria, "")

        return LLMClassifier(
            name=f"email_agent_{criteria}_judge",
            prompt_template=f"""
            Evaluate this email management agent response for {criteria}:

            User Query: {{input}}
            Agent Response: {{output}}
            Expected Behavior: {{expected}}

            {prompt_addition}

            Rate the response: excellent/good/satisfactory/needs_improvement/poor
            """,
            choice_scores={
                "excellent": 1.0,
                "good": 0.8,
                "satisfactory": 0.6,
                "needs_improvement": 0.4,
                "poor": 0.2
            },
            client=self.client,
            model=self.model,
        )


class DualEmailScorer:
    """
    Combined scoring system using both code-based and LLM-based evaluation.
    Provides comprehensive assessment of email agent performance.
    """

    def __init__(self, code_weight: float = 0.6, llm_weight: float = 0.4):
        self.code_scorer = CodeBasedEmailScorer()
        self.llm_judge = LLMEmailJudge()
        self.code_weight = code_weight
        self.llm_weight = llm_weight

        # Initialize LLM scorers
        self.general_llm_scorer = self.llm_judge.create_llm_scorer()
        self.ux_scorer = self.llm_judge.create_specific_criteria_scorer("user_experience")
        self.technical_scorer = self.llm_judge.create_specific_criteria_scorer("technical_accuracy")
        self.completeness_scorer = self.llm_judge.create_specific_criteria_scorer("completeness")

    def evaluate(self, expected: Dict[str, Any], output: str, row: Optional[Dict] = None) -> EmailEvaluationResult:
        """
        Comprehensive evaluation using both scoring systems.

        Args:
            expected: Expected behavior and results
            output: Agent's actual output
            row: Additional context data

        Returns:
            EmailEvaluationResult with detailed scoring information
        """
        # Code-based scoring
        code_score = self.code_scorer.score_email_agent_output(expected, output, row)

        # LLM-based scoring
        llm_scores = {}
        try:
            # General quality assessment
            general_result = self.general_llm_scorer(output, expected, row)
            llm_scores["general"] = general_result.score if hasattr(general_result, 'score') else 0.6

            # Specific criteria assessments
            ux_result = self.ux_scorer(output, expected, row)
            llm_scores["user_experience"] = ux_result.score if hasattr(ux_result, 'score') else 0.6

            technical_result = self.technical_scorer(output, expected, row)
            llm_scores["technical_accuracy"] = technical_result.score if hasattr(technical_result, 'score') else 0.6

            completeness_result = self.completeness_scorer(output, expected, row)
            llm_scores["completeness"] = completeness_result.score if hasattr(completeness_result, 'score') else 0.6

        except Exception as e:
            # Fallback scores if LLM evaluation fails
            llm_scores = {
                "general": 0.6,
                "user_experience": 0.6,
                "technical_accuracy": 0.6,
                "completeness": 0.6
            }

        # Calculate average LLM score
        llm_score = sum(llm_scores.values()) / len(llm_scores)

        # Calculate combined score
        combined_score = (code_score * self.code_weight) + (llm_score * self.llm_weight)

        return EmailEvaluationResult(
            code_score=code_score,
            llm_score=llm_score,
            combined_score=combined_score,
            code_details={
                "action_appropriateness": self.code_scorer._score_action_appropriateness(expected, self.code_scorer._parse_agent_output(output)),
                "efficiency": self.code_scorer._score_efficiency(expected, self.code_scorer._parse_agent_output(output)),
                "completeness": self.code_scorer._score_completeness(expected, self.code_scorer._parse_agent_output(output)),
                "accuracy": self.code_scorer._score_accuracy(expected, self.code_scorer._parse_agent_output(output))
            },
            llm_details=llm_scores,
            evaluation_metadata={
                "code_weight": self.code_weight,
                "llm_weight": self.llm_weight,
                "total_criteria_evaluated": len(llm_scores) + 4  # 4 code criteria
            }
        )


# Scoring functions for use in Braintrust evaluations
def email_code_scorer(expected, output, row=None):
    """Code-based scorer function for Braintrust."""
    scorer = CodeBasedEmailScorer()
    return scorer.score_email_agent_output(expected, output, row)


def email_llm_scorer():
    """LLM-based scorer function for Braintrust."""
    judge = LLMEmailJudge()
    return judge.create_llm_scorer()


def email_dual_scorer(expected, output, row=None):
    """Combined dual scorer function for Braintrust."""
    scorer = DualEmailScorer()
    result = scorer.evaluate(expected, output, row)
    return result.combined_score