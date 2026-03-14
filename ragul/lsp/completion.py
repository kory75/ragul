"""
ragul/lsp/completion.py — Completion provider for the Ragul LSP server.

After a '-', suggests all valid suffixes for the current root's inferred type.
Also suggests root names already defined in the current scope.
"""

from __future__ import annotations
from lsprotocol.types import (
    CompletionItem,
    CompletionItemKind,
    CompletionList,
)
from ragul.model import RagulType
from ragul.stdlib.core import SUFFIX_REGISTRY


# Human-readable descriptions for each canonical suffix
_SUFFIX_DOCS: dict[str, str] = {
    "-össze":      "Add  (Szám + Szám → Szám)",
    "-kivon":      "Subtract  (Szám - Szám → Szám)",
    "-szoroz":     "Multiply  (Szám × Szám → Szám)",
    "-oszt":       "Divide  (Szám ÷ Szám → Szám)",
    "-maradék":    "Modulo  (Szám % Szám → Szám)",
    "-felett":     "Greater than  (Szám > threshold → Logikai/Lista)",
    "-alatt":      "Less than  (Szám < threshold → Logikai/Lista)",
    "-legalább":   "≥ threshold",
    "-legfeljebb": "≤ threshold",
    "-egyenlő":    "Equal  (any == any → Logikai)",
    "-nemegyenlő": "Not equal",
    "-nem":        "Logical NOT  (Logikai → Logikai)",
    "-és":         "Logical AND",
    "-vagy":       "Logical OR",
    "-összefűz":   "Concatenate strings  (Szöveg + Szöveg → Szöveg)",
    "-négyzetgyök":"Square root  (Szám → Szám)",
    "-hatvány":    "Power  (Szám ^ n → Szám)",
    "-abszolút":   "Absolute value",
    "-kerekítve":  "Round to nearest integer",
    "-padló":      "Floor",
    "-plafon":     "Ceiling",
    "-hossz":      "Length  (Lista/Szöveg → Szám)",
    "-nagybetűs":  "Uppercase  (Szöveg → Szöveg)",
    "-kisbetűs":   "Lowercase  (Szöveg → Szöveg)",
    "-tartalmaz":  "Contains  (Szöveg/Lista → Logikai)",
    "-feloszt":    "Split string by delimiter  (Szöveg → Lista-Szöveg)",
    "-rendezve":   "Sort ascending  (Lista → Lista)",
    "-rendezve-le":"Sort descending  (Lista → Lista)",
    "-szűrve":     "Filter by condition  (Lista → Lista)",
    "-fordítva":   "Reverse  (Lista → Lista)",
    "-első":       "First element  (Lista → T)",
    "-utolsó":     "Last element  (Lista → T)",
    "-hozzáad":    "Append element  (Lista + T → Lista)",
    "-eltávolít":  "Remove first match  (Lista → Lista)",
    "-egyedi":     "Remove duplicates  (Lista → Lista)",
    "-lapítva":    "Flatten one level  (Lista-Lista → Lista)",
    "-ba":         "Case: into (assignment target)",
    "-ból":        "Case: from (source)",
    "-val":        "Case: with (instrument/argument)",
    "-t":          "Case: object/accusative",
    "-ként":       "Case: as / in the role of",
    "-va":         "Action: execute",
    "-e":          "Error propagation (after -va)",
    "-unk":        "Possession: ours / scope owner",
    "-m":          "Possession: mine / immutable",
    "-d":          "Possession: yours / parameter",
    "-ja":         "Possession: its / instance field",
}


def get_completions(source: str, filename: str,
                    line: int, character: int) -> CompletionList:
    """
    Return completion items for the position (line, character).
    Called after the user types '-'.
    """
    from ragul.lexer import lex
    from ragul.parser import parse
    from ragul.typechecker import TypeChecker, TypeEnv
    from ragul.config import RagulConfig

    items: list[CompletionItem] = []

    try:
        tokens, _ = lex(source, filename)
        tree, _   = parse(tokens, filename)
        cfg = RagulConfig.load()
        checker = TypeChecker(tree, filename, cfg)

        # Build env to find root types
        env = TypeEnv()
        checker._check_scope(tree, env, in_effect=False)

        # Find the word being typed — look at text before cursor on current line
        src_lines   = source.splitlines()
        if line < len(src_lines):
            current_line = src_lines[line][:character]
        else:
            current_line = ""

        # Extract the partial root being typed (word before last '-')
        import re
        m = re.search(r'(\w+)(-\w*)?$', current_line)
        root_name = m.group(1) if m else ""

        # Determine root's type
        root_type = env.get(root_name) or RagulType.unknown()

        # Add suffix completions filtered by type compatibility
        for suffix, entry in SUFFIX_REGISTRY.items():
            expected_input = entry["input_type"]
            compatible = (
                root_type.base == RagulType.UNKNOWN
                or expected_input.base == RagulType.UNKNOWN
                or root_type.base == expected_input.base
                or (root_type.base == RagulType.LISTA and expected_input.base == RagulType.LISTA)
            )
            if not compatible:
                continue

            doc = _SUFFIX_DOCS.get(suffix, "")
            items.append(CompletionItem(
                label=suffix,
                kind=CompletionItemKind.Function,
                detail=doc,
                insert_text=suffix.lstrip("-"),
            ))

        # Add case suffix completions always
        for suffix, doc in _SUFFIX_DOCS.items():
            if suffix.startswith("-") and suffix not in SUFFIX_REGISTRY:
                items.append(CompletionItem(
                    label=suffix,
                    kind=CompletionItemKind.Keyword,
                    detail=doc,
                    insert_text=suffix.lstrip("-"),
                ))

        # Add known root names as completions (for cross-word references)
        for name in env.all_names():
            items.append(CompletionItem(
                label=name,
                kind=CompletionItemKind.Variable,
                detail=repr(env.get(name)),
            ))

    except Exception:
        pass  # Never crash — return empty list

    return CompletionList(is_incomplete=False, items=items)
