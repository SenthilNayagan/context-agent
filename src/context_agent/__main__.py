"""
Application execution entry point for ContextAgent.

This module is invoked when running:
    python -m context_agent

It acts as the execution hook and delegates control
to the main application logic defined in main.py.
"""

from context_agent.main import main


if __name__ == "__main__":
    main()
