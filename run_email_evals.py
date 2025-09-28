#!/usr/bin/env python3
"""
Email Management Agent Evaluation Runner
Provides convenient interface for running email evaluations with different configurations.
"""

import os
import sys
import argparse
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def setup_environment(config_file: str = None):
    """Set up environment configuration for evaluations."""
    if config_file:
        load_dotenv(config_file)
    else:
        # Try to load from standard locations
        env_files = [".env", ".env.email", ".env.local"]
        for env_file in env_files:
            env_path = project_root / env_file
            if env_path.exists():
                load_dotenv(env_path)
                print(f"Loaded environment from: {env_path}")
                break
        else:
            print("Warning: No .env file found. Using environment defaults.")


def print_evaluation_info():
    """Print current evaluation configuration."""
    print("\n" + "="*60)
    print("EMAIL MANAGEMENT AGENT EVALUATION")
    print("="*60)
    print(f"Project: {os.getenv('PROJECT_NAME', 'Fabs27Sep25DeepDive')}")
    print(f"Evaluation Mode: {os.getenv('EMAIL_EVAL_MODE', 'dual')}")
    print(f"Evaluation Focus: {os.getenv('EMAIL_EVAL_FOCUS', 'all')}")
    print(f"Mock Services: {os.getenv('USE_MOCK_EMAIL_SERVICES', 'true')}")
    print(f"Model: {'Local' if os.getenv('USE_LOCAL_MODEL', 'false').lower() == 'true' else 'Frontier'}")
    print(f"Max Concurrency: {os.getenv('EVAL_MAX_CONCURRENCY', '2')}")
    print("="*60)


def run_evaluation(eval_type: str = "all", verbose: bool = False):
    """Run email management evaluations."""
    print_evaluation_info()

    # Set evaluation focus
    os.environ["EMAIL_EVAL_FOCUS"] = eval_type

    if verbose:
        os.environ["EVAL_VERBOSE_LOGGING"] = "true"

    print(f"\nRunning {eval_type} evaluation scenarios...")

    try:
        # Import and run the evaluation
        import subprocess
        result = subprocess.run([
            sys.executable, "-m", "braintrust", "eval", "evals/eval_email_management.py"
        ], cwd=project_root, capture_output=True, text=True)

        if result.returncode == 0:
            print("✓ Evaluation completed successfully!")
            print("\nResults:")
            print(result.stdout)
        else:
            print("✗ Evaluation failed!")
            print("Error output:")
            print(result.stderr)
            return 1

    except Exception as e:
        print(f"Error running evaluation: {e}")
        return 1

    return 0


def test_setup():
    """Test the email management setup."""
    print("Testing email management setup...")

    try:
        # Test mock services
        from agents.mock_email_services import MockEmailService
        email_service = MockEmailService()
        status = email_service.get_system_status()
        print(f"✓ Mock email service: {status['total_emails']} emails across {status['accounts_configured']} accounts")

        # Test agent
        from agents.email_management import manage_emails
        result = manage_emails("Give me a quick system status")
        print(f"✓ Agent response length: {len(result)} characters")

        # Test observability
        from observability.email_otel_setup import setup_email_tracing
        tracer = setup_email_tracing()
        print("✓ OpenTelemetry tracing configured")

        # Test scoring
        from scoring.email_scoring import email_code_scorer, DualEmailScorer
        scorer = DualEmailScorer()
        print("✓ Dual scoring system initialized")

        print("\n✓ All components working correctly!")
        return 0

    except Exception as e:
        print(f"✗ Setup test failed: {e}")
        return 1


def create_sample_config():
    """Create a sample configuration file."""
    config_path = project_root / ".env.email"

    if config_path.exists():
        print(f"Configuration file already exists: {config_path}")
        return

    # Copy template
    template_path = project_root / ".env.email.template"
    if template_path.exists():
        import shutil
        shutil.copy(template_path, config_path)
        print(f"Created configuration file: {config_path}")
        print("Please edit this file with your API keys and preferences.")
    else:
        print("Error: Template file not found")


def main():
    """Main CLI interface."""
    parser = argparse.ArgumentParser(
        description="Email Management Agent Evaluation Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test                    # Test setup
  %(prog)s --run all                # Run all evaluations
  %(prog)s --run zero_inbox         # Run only zero inbox scenarios
  %(prog)s --run search --verbose   # Run search scenarios with verbose output
  %(prog)s --config                 # Create sample configuration
        """
    )

    parser.add_argument("--config", action="store_true",
                       help="Create sample configuration file")
    parser.add_argument("--test", action="store_true",
                       help="Test email management setup")
    parser.add_argument("--run", choices=["all", "zero_inbox", "search", "errors", "performance"],
                       help="Run evaluations")
    parser.add_argument("--env-file", type=str,
                       help="Path to environment file")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose output")

    args = parser.parse_args()

    # Setup environment
    setup_environment(args.env_file)

    if args.config:
        create_sample_config()
        return 0

    if args.test:
        return test_setup()

    if args.run:
        return run_evaluation(args.run, args.verbose)

    # Default: show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    exit(main())