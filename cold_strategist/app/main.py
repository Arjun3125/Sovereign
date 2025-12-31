"""
Cold Strategist - CLI / API Bootstrap
Entry point for the Sovereign system.
"""

from session_runner import SessionRunner


def main():
    """Main entry point for Cold Strategist."""
    runner = SessionRunner()
    runner.execute()


if __name__ == "__main__":
    main()
