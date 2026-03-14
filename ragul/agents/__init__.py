"""
ragul/agents — Orchestrator + specialist agent architecture for the Ragul toolchain.

Public API:
    Task, TaskResult     — typed message protocol
    OrchestratorAgent    — main coordinator (use this from the CLI)
    DocsAgent            — Claude-powered example program generator
"""

from ragul.agents.task import Task, TaskResult
from ragul.agents.orchestrator import OrchestratorAgent
from ragul.agents.docs_agent import DocsAgent

__all__ = ["Task", "TaskResult", "OrchestratorAgent", "DocsAgent"]
