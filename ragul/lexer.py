"""
ragul/lexer.py — Hand-written lexer for the Ragul language.

Produces a flat token stream from source text.
Alias normalisation is applied at lex time — the parser only ever sees
canonical Hungarian suffix forms.
"""

from __future__ import annotations
import re
from dataclasses import dataclass
from enum import Enum, auto
from ragul.model import normalise_suffix, ALIAS_TABLE, ROOT_ALIASES
from ragul.errors import DiagnosticBag, E002


class TT(Enum):
    """Token types."""
    WORD        = auto()   # root-suffix chain, e.g. "x-ból", "data-szűrve-ból"
    SCOPE_OPEN  = auto()   # a WORD whose last suffix is a scope-defining modifier
    NUMBER      = auto()   # integer or float literal
    STRING      = auto()   # "..." literal
    LIST_OPEN   = auto()   # [
    LIST_CLOSE  = auto()   # ]
    FULLSTOP    = auto()   # .
    INDENT      = auto()   # indentation increase
    DEDENT      = auto()   # indentation decrease
    COMMENT     = auto()   # // ...
    NEWLINE     = auto()   # bare newline (informational, mostly filtered)
    MINUS_HANEM = auto()   # -hanem (standalone else branch opener)
    MINUS_HIBARA= auto()   # -hibára (standalone error handler opener)
    EOF         = auto()


@dataclass
class Token:
    type:  TT
    value: str     # normalised text
    line:  int
    col:   int
    raw:   str = ""   # original text before normalisation


# ---------------------------------------------------------------------------
# Suffix chain normalisation
# ---------------------------------------------------------------------------

# All known aliases in one set for fast lookup during chain splitting
_ALL_ALIAS_KEYS: frozenset[str] = frozenset(ALIAS_TABLE.keys())

# Regex to split a raw word into root + suffix chain
# Suffixes begin with a '-' followed by non-'-' characters
_WORD_RE = re.compile(r'^(-?\d+(?:\.\d+)?|[^-]+)((?:-[^-]+)*)$')


def _split_and_normalise(raw_word: str) -> tuple[str, list[str]]:
    """
    Split 'root-suf1-suf2-suf3' into (root, ['-suf1', '-suf2', '-suf3']).
    Each suffix is normalised via the alias table.
    Returns (root, suffixes).

    Trailing dash (e.g. 'records-tojson-') is preserved at the end of the
    suffix list as a bare '-' so the parser can detect it as a string-absorb
    marker.  Without this, the WORD_RE match fails on the trailing '-' and
    the preceding suffixes would not be normalised.
    """
    trailing_dash = raw_word.endswith("-") and len(raw_word) > 1
    word = raw_word[:-1] if trailing_dash else raw_word
    m = _WORD_RE.match(word)
    if not m:
        return raw_word, []
    root = m.group(1)
    suf_str = m.group(2)
    if not suf_str:
        return root, ["-"] if trailing_dash else []
    # split on '-' keeping the dash
    parts = re.split(r'(?=-[A-Za-z\u0080-\uFFFF])', suf_str)  # split only before letter suffixes
    parts = [p for p in parts if p]
    normalised = [normalise_suffix(p) for p in parts]
    if trailing_dash:
        normalised.append("-")
    return root, normalised


# ---------------------------------------------------------------------------
# Lexer
# ---------------------------------------------------------------------------

class Lexer:
    """
    Tokenises a Ragul source string.

    Usage:
        lexer = Lexer(source, filename="main.ragul")
        tokens = lexer.tokenise()
    """

    # Scope-defining terminal suffixes (make a WORD into a SCOPE_OPEN)
    SCOPE_SUFFIXES = frozenset({
        "-unk", "-nk",
        "-hatás",       # effect scope (combined: -nk-hatás)
        "-modul",       # module (combined: -nk-modul)
        "-ha",          # conditional scope
        "-hanem",       # else branch
        "-különben",    # else-if (combined: -különben-ha)
        "-míg",         # while loop scope
        "-ig",          # until loop scope
        "-mindegyik",   # for-each scope
        "-gyűjt",       # fold scope
        "-szerződés",   # contract scope
    })

    def __init__(self, source: str, filename: str = "<string>") -> None:
        self.source   = source
        self.filename = filename
        self.bag      = DiagnosticBag(filename)
        self._tokens: list[Token] = []

    def tokenise(self) -> list[Token]:
        """Run the lexer and return the full token stream."""
        lines = self.source.splitlines(keepends=True)
        indent_stack = [0]

        for lineno, raw_line in enumerate(lines, start=1):
            line = raw_line.rstrip('\n').rstrip('\r')
            stripped = line.lstrip('\t')
            current_indent = len(line) - len(stripped)

            # Skip blank lines and comment-only lines
            content = stripped.strip()
            if not content or content.startswith('//'):
                continue

            # Emit INDENT / DEDENT tokens
            prev_indent = indent_stack[-1]
            if current_indent > prev_indent:
                indent_stack.append(current_indent)
                self._tokens.append(Token(TT.INDENT, "", lineno, 0))
            elif current_indent < prev_indent:
                while indent_stack and indent_stack[-1] > current_indent:
                    indent_stack.pop()
                    self._tokens.append(Token(TT.DEDENT, "", lineno, 0))

            # Tokenise the content of the line
            self._tokenise_line(content, lineno)

        # Close any remaining open indents
        while len(indent_stack) > 1:
            indent_stack.pop()
            self._tokens.append(Token(TT.DEDENT, "", len(lines) + 1, 0))

        self._tokens.append(Token(TT.EOF, "", len(lines) + 1, 0))
        return self._tokens

    def _tokenise_line(self, line: str, lineno: int) -> None:
        """Tokenise a single pre-stripped line."""
        pos = 0
        n   = len(line)

        # Strip inline comment
        comment_idx = line.find('//')
        if comment_idx != -1:
            line = line[:comment_idx].rstrip()
            n = len(line)

        while pos < n:
            # Skip spaces
            if line[pos] == ' ':
                pos += 1
                continue

            # Full stop (sentence terminator)
            if line[pos] == '.':
                self._tokens.append(Token(TT.FULLSTOP, ".", lineno, pos))
                pos += 1
                continue

            # List brackets
            if line[pos] == '[':
                self._tokens.append(Token(TT.LIST_OPEN, "[", lineno, pos))
                pos += 1
                continue
            if line[pos] == ']':
                self._tokens.append(Token(TT.LIST_CLOSE, "]", lineno, pos))
                pos += 1
                continue

            # String literal
            if line[pos] == '"':
                end = pos + 1
                while end < n and line[end] != '"':
                    if line[end] == '\\':
                        end += 1   # skip escaped char
                    end += 1
                raw = line[pos:end+1]
                value = raw[1:-1].replace('\\"', '"').replace('\\n', '\n').replace('\\t', '\t')
                self._tokens.append(Token(TT.STRING, value, lineno, pos, raw))
                pos = end + 1
                continue

            # Standalone branch openers: -hanem/-else, -hibára/-catch (line-leading -)
            if line[pos] == '-' and line[:pos].strip() == '':
                branch_m = re.match(
                    r'(-hanem|-hibára|-catch|-else|-különben-ha|-különben|-elif)\b',
                    line[pos:],
                )
                if branch_m:
                    raw = branch_m.group(0)
                    canonical = normalise_suffix(raw)
                    if canonical in ("-hanem",):
                        self._tokens.append(Token(TT.MINUS_HANEM, raw, lineno, pos))
                    elif canonical in ("-hibára",):
                        self._tokens.append(Token(TT.MINUS_HIBARA, raw, lineno, pos))
                    # -különben / -különben-ha fall through to word handler
                    pos += len(raw)
                    continue

            # Float literal (e.g. "3.14-t") — must precede word_m because
            # '.' in a float would otherwise be consumed as FULLSTOP.
            if line[pos].isdigit() or (
                    line[pos] == '-' and pos + 1 < n and line[pos + 1].isdigit()):
                float_m = re.match(r'-?\d+\.\d+', line[pos:])
                if float_m:
                    num_str = float_m.group(0)
                    rest = pos + len(num_str)
                    if rest < n and line[rest] == '-':
                        suf_m = re.match(r'[^\s.\[\]",]+', line[rest:])
                        if suf_m:
                            raw = num_str + suf_m.group(0)
                            self._tokens.append(self._make_word_token(raw, lineno, pos))
                            pos = rest + len(suf_m.group(0))
                            continue
                    self._tokens.append(Token(TT.NUMBER, num_str, lineno, pos, num_str))
                    pos += len(num_str)
                    continue

            # Word token — MUST come before pure-number check.
            # Matches "3-t", "x-ba", "lista-rendezve-ból", "10-felett", etc.
            # A pure number with no suffixes is emitted as NUMBER; everything
            # else (root + suffixes) is emitted as WORD / SCOPE_OPEN.
            word_m = re.match(r'[^\s.\[\]",]+', line[pos:])
            if word_m:
                raw = word_m.group(0)
                if re.fullmatch(r'-?\d+(?:\.\d+)?', raw):
                    # Pure number literal
                    self._tokens.append(Token(TT.NUMBER, raw, lineno, pos, raw))
                else:
                    token = self._make_word_token(raw, lineno, pos)
                    self._tokens.append(token)
                pos += len(raw)
                continue

            # Unknown character — skip with warning
            pos += 1

    def _make_word_token(self, raw: str, line: int, col: int) -> Token:
        """Build a WORD (or SCOPE_OPEN) token, applying alias normalisation."""
        root, suffixes = _split_and_normalise(raw)
        # Standalone suffix-chain token with no root (e.g. "-it", "-contains-it"
        # after a string or number literal).  _split_and_normalise returns
        # (raw, []) because the regex requires a non-dash root.  Detect this
        # case: split the token into individual suffixes and normalise each.
        if not suffixes and root.startswith("-"):
            parts = re.findall(r'-[^-]+', root)
            if parts:
                suffixes = [normalise_suffix(p) for p in parts]
                root = ""
        # Normalise root-level keyword aliases (e.g. "true" → "igaz")
        root = ROOT_ALIASES.get(root, root)
        normalised_value = root + "".join(suffixes)

        # Determine if this is a scope-opening word
        is_scope = bool(suffixes) and any(s in self.SCOPE_SUFFIXES for s in suffixes)

        tt = TT.SCOPE_OPEN if is_scope else TT.WORD
        return Token(tt, normalised_value, line, col, raw)


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def lex(source: str, filename: str = "<string>") -> tuple[list[Token], DiagnosticBag]:
    """Convenience function: lex source and return (tokens, diagnostics)."""
    lexer = Lexer(source, filename)
    tokens = lexer.tokenise()
    return tokens, lexer.bag
