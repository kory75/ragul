"""
ragul/agents/repl_agent.py — Specialist agent wrapping the Ragul REPL.

Ignores task.source — the REPL reads from stdin interactively.
Returns when the session ends.
"""

from __future__ import annotations
from ragul.agents.base import BaseAgent
from ragul.agents.task import Task, TaskResult


class ReplAgent(BaseAgent):

    def run(self, task: Task) -> TaskResult:
        from ragul.repl.repl import run_repl

        exit_code = run_repl()
        return TaskResult(ok=exit_code == 0, exit_code=exit_code)
