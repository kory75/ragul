"""
ragul/agents/typecheck_agent.py — Specialist agent wrapping the Ragul type checker.

Input:  task.scope_tree (Scope)  — must be pre-parsed
Output: TaskResult.payload = Scope (annotated in-place)
        TaskResult.errors / warnings = type diagnostics
"""

from __future__ import annotations
from ragul.agents.base import BaseAgent
from ragul.agents.task import Task, TaskResult


class TypeAgent(BaseAgent):

    def run(self, task: Task) -> TaskResult:
        from ragul.typechecker import TypeChecker

        if task.scope_tree is None:
            return TaskResult(ok=False, exit_code=1)

        checker = TypeChecker(task.scope_tree, task.filename, task.config)
        bag     = checker.check()

        return TaskResult(
            ok=not bag.has_errors,
            payload=task.scope_tree,        # annotated in-place
            errors=list(bag.errors),
            warnings=list(bag.warnings),
            exit_code=0 if not bag.has_errors else 1,
        )
