"""
ragul/agents/parser_agent.py — Specialist agent wrapping the Ragul parser.

Input:  task.tokens  (list[Token])  — must be pre-lexed
Output: TaskResult.payload = Scope (root)
"""

from __future__ import annotations
from ragul.agents.base import BaseAgent
from ragul.agents.task import Task, TaskResult


class ParserAgent(BaseAgent):

    def run(self, task: Task) -> TaskResult:
        from ragul.parser import parse

        if task.tokens is None:
            return TaskResult(ok=False, exit_code=1)

        tree, bag = parse(task.tokens, task.filename)

        return TaskResult(
            ok=not bag.has_errors,
            payload=tree,
            errors=list(bag.errors),
            warnings=list(bag.warnings),
            exit_code=0 if not bag.has_errors else 1,
        )
