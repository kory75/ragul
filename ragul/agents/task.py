"""
ragul/agents/task.py — Typed message protocol for the Ragul agent architecture.

All agents communicate via Task / TaskResult objects.
The orchestrator never calls the compiler pipeline directly — it constructs
Task objects and calls agent.run(task).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any

from ragul.config import RagulConfig


@dataclass
class Task:
    """
    A unit of work dispatched to a specialist agent.

    kind:       "lex" | "parse" | "typecheck" | "interpret" | "repl" | "lsp" | "docs"
    source:     raw source text (required for lex/parse/typecheck/interpret)
    filename:   used in error messages and diagnostics
    tokens:     pre-lexed token list (skips the lex phase when provided)
    scope_tree: pre-parsed Scope tree (skips lex+parse phases when provided)
    config:     RagulConfig loaded from ragul.config
    flags:      phase-specific options, e.g. {"strict": True, "topic": "loops"}
    """
    kind:       str
    filename:   str         = "<unknown>"
    source:     str | None  = None
    tokens:     list | None = None
    scope_tree: Any         = None          # Scope | None — avoid circular import
    config:     RagulConfig = field(default_factory=RagulConfig)
    flags:      dict        = field(default_factory=dict)


@dataclass
class TaskResult:
    """
    The result returned by a specialist agent after running a Task.

    ok:          True if the phase completed without errors
    payload:     phase-specific output:
                   LexerAgent   → list[Token]
                   ParserAgent  → Scope
                   TypeAgent    → Scope (annotated in-place) + diagnostics
                   InterpAgent  → dict of final environment bindings
                   DocsAgent    → str (generated Ragul source)
    errors:      error diagnostics collected during this phase
    warnings:    warning diagnostics collected during this phase
    exit_code:   0 success | 1 compile error | 2 runtime error | 3 unhandled Hiba
    ai_analysis: optional Claude-generated error explanation (set by Orchestrator)
    """
    ok:          bool
    payload:     Any   = None
    errors:      list  = field(default_factory=list)
    warnings:    list  = field(default_factory=list)
    exit_code:   int   = 0
    ai_analysis: str | None = None
