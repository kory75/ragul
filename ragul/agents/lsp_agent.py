"""
ragul/agents/lsp_agent.py — Specialist agent wrapping the Ragul LSP server.

Starts the LSP server in stdio mode.
Blocks until the editor disconnects or the server exits.
"""

from __future__ import annotations
from ragul.agents.base import BaseAgent
from ragul.agents.task import Task, TaskResult


class LspAgent(BaseAgent):

    def run(self, task: Task) -> TaskResult:
        from ragul.lsp.server import run_lsp_server
        try:
            run_lsp_server()
            return TaskResult(ok=True, exit_code=0)
        except Exception as e:
            return TaskResult(ok=False, exit_code=2,
                              ai_analysis=f"LSP server error: {e}")
