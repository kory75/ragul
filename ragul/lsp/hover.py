"""
ragul/lsp/hover.py — Hover provider for the Ragul LSP server.

On hover over a WORD token, shows:
  - The root name
  - The inferred type (from the type checker's annotated tree)
  - The suffix chain breakdown
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ragul.typechecker import TypeChecker

from lsprotocol.types import (
    Hover,
    MarkupContent,
    MarkupKind,
    Position,
)


def get_hover(source: str, filename: str, line: int, character: int) -> Hover | None:
    """
    Return hover information for the token at (line, character).
    line and character are 0-indexed (LSP convention).
    """
    from ragul.lexer import lex, TT
    from ragul.parser import parse
    from ragul.typechecker import TypeChecker
    from ragul.config import RagulConfig

    try:
        tokens, _ = lex(source, filename)
        tree, _   = parse(tokens, filename)
        cfg = RagulConfig.load()
        checker = TypeChecker(tree, filename, cfg)
        checker.check()

        # Find the token at the cursor position (1-indexed line in tokens)
        target_line = line + 1   # Ragul uses 1-indexed lines
        word_at_cursor = None

        for tok in tokens:
            if tok.type not in (TT.WORD, TT.SCOPE_OPEN):
                continue
            if tok.line != target_line:
                continue
            tok_end = tok.col + len(tok.value)
            if tok.col <= character <= tok_end:
                word_at_cursor = tok
                break

        if word_at_cursor is None:
            return None

        # Get the root name from the token
        root = word_at_cursor.value.split("-")[0]

        # Look up the inferred type from the checker's env
        env_type = checker._check_scope.__func__  # type: ignore[attr-defined]

        # Build a simple type summary from the token value
        parts = word_at_cursor.value.split("-")
        root_name  = parts[0]
        suffixes   = [f"-{p}" for p in parts[1:] if p]

        lines = [
            f"**`{word_at_cursor.value}`**",
            "",
            f"Root: `{root_name}`",
        ]
        if suffixes:
            lines.append(f"Suffix chain: `{'` → `'.join(suffixes)}`")

        # Try to get the type from the global env after a full check pass
        root_env = checker.check()  # re-run to get fresh state
        # Walk the type env built during check
        type_str = _lookup_type_in_checked_tree(tree, root_name, checker)
        if type_str:
            lines.append(f"Type: `{type_str}`")

        return Hover(
            contents=MarkupContent(
                kind=MarkupKind.Markdown,
                value="\n".join(lines),
            )
        )

    except Exception:
        return None


def _lookup_type_in_checked_tree(tree, root_name: str, checker: TypeChecker) -> str | None:
    """Walk the scope tree to find the inferred type of a root."""
    # Re-run check to build a fresh type env
    env = _build_type_env(tree, checker)
    t = env.get(root_name)
    return repr(t) if t else None


def _build_type_env(tree, checker: TypeChecker):
    """Build the type environment by running the type checker."""
    from ragul.typechecker import TypeEnv
    env = TypeEnv()
    checker._check_scope(tree, env, in_effect=False)
    return env
