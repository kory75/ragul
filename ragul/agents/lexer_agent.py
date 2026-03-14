"""
ragul/agents/lexer_agent.py — Specialist agent wrapping the Ragul lexer.

Input:  task.source  (str)
Output: TaskResult.payload = list[Token]
"""

from __future__ import annotations
from ragul.agents.base import BaseAgent
from ragul.agents.task import Task, TaskResult


class LexerAgent(BaseAgent):

    def run(self, task: Task) -> TaskResult:
        from ragul.lexer import lex

        if not task.source:
            return TaskResult(ok=False, exit_code=1)

        tokens, bag = lex(task.source, task.filename)

        return TaskResult(
            ok=not bag.has_errors,
            payload=tokens,
            errors=list(bag.errors),
            warnings=list(bag.warnings),
            exit_code=0 if not bag.has_errors else 1,
        )
