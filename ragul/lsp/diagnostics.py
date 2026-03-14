"""
ragul/lsp/diagnostics.py — Convert RagulDiagnostic objects to LSP Diagnostics.

The RagulError/RagulWarning dataclasses already carry file, line, code,
and message — almost no translation needed.
"""

from __future__ import annotations
from lsprotocol.types import (
    Diagnostic,
    DiagnosticSeverity,
    Position,
    Range,
)
from ragul.errors import RagulDiagnostic, Severity


def ragul_to_lsp(diag: RagulDiagnostic) -> Diagnostic:
    """Convert a RagulDiagnostic to an LSP Diagnostic."""
    severity = (
        DiagnosticSeverity.Error
        if diag.severity == Severity.ERROR
        else DiagnosticSeverity.Warning
    )

    # LSP lines are 0-indexed; Ragul lines are 1-indexed
    line = max(0, diag.line - 1)

    return Diagnostic(
        range=Range(
            start=Position(line=line, character=0),
            end=Position(line=line, character=999),
        ),
        message=diag.message
        + (f"\n{diag.detail}" if diag.detail else "")
        + (f"\n→ {diag.suggestion}" if diag.suggestion else ""),
        severity=severity,
        code=diag.code,
        source="ragul",
    )


def build_diagnostics(source: str, filename: str) -> list[Diagnostic]:
    """
    Run the full Ragul pipeline on source and return LSP diagnostics.
    Called on every textDocument/didChange event.
    """
    from ragul.lexer import lex
    from ragul.parser import parse
    from ragul.typechecker import TypeChecker
    from ragul.config import RagulConfig

    lsp_diags: list[Diagnostic] = []

    try:
        tokens, lex_bag = lex(source, filename)
        for d in lex_bag:
            lsp_diags.append(ragul_to_lsp(d))

        tree, parse_bag = parse(tokens, filename)
        for d in parse_bag:
            lsp_diags.append(ragul_to_lsp(d))

        if not lex_bag.has_errors and not parse_bag.has_errors:
            cfg = RagulConfig.load()
            checker = TypeChecker(tree, filename, cfg)
            type_bag = checker.check()
            for d in type_bag:
                lsp_diags.append(ragul_to_lsp(d))

    except Exception as e:
        # Never crash the LSP server on malformed input
        lsp_diags.append(
            Diagnostic(
                range=Range(
                    start=Position(line=0, character=0),
                    end=Position(line=0, character=0),
                ),
                message=f"Internal compiler error: {e}",
                severity=DiagnosticSeverity.Error,
                code="E000",
                source="ragul",
            )
        )

    return lsp_diags
