"""
ragul/agents/interpreter_agent.py — Specialist agent wrapping the Ragul interpreter.

Input:  task.scope_tree (Scope)  — must be pre-parsed
Output: TaskResult.payload = final environment bindings (dict)
        TaskResult.exit_code   = 0 | 2 | 3
"""

from __future__ import annotations
from ragul.agents.base import BaseAgent
from ragul.agents.task import Task, TaskResult


class InterpAgent(BaseAgent):

    def run(self, task: Task) -> TaskResult:
        from ragul.interpreter import Interpreter

        if task.scope_tree is None:
            return TaskResult(ok=False, exit_code=2)

        interp    = Interpreter(task.scope_tree, task.filename)
        exit_code = interp.run()

        return TaskResult(
            ok=exit_code == 0,
            payload=interp.global_env.all_bindings(),
            exit_code=exit_code,
        )
