"""
ragul/agents/base.py — Abstract base class for all Ragul specialist agents.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from ragul.agents.task import Task, TaskResult


class BaseAgent(ABC):
    """
    All specialist agents implement this interface.
    The orchestrator uses only this interface to delegate work.
    """

    @abstractmethod
    def run(self, task: Task) -> TaskResult:
        """Execute the task and return a result."""
        ...

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"
