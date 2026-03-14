"""
ragul/parser.py — Two-pass parser for the Ragul language.

Pass 1 — Word construction:
    For each WORD/SCOPE_OPEN token, split at suffix boundaries and populate
    a Word dataclass. Validate suffix layer order and raise E002 on violation.

Pass 2 — Sentence and Scope assembly:
    Group Words into Sentences (delimited by FULLSTOP).
    Build the Scope tree from INDENT/DEDENT and SCOPE_OPEN tokens.
"""

from __future__ import annotations
import re
from ragul.model import (
    Word, Sentence, Scope, RagulType,
    CASE_SUFFIXES, POSSESSION_SUFFIXES, ACTION_SUFFIXES, SCOPE_MODIFIERS,
    normalise_suffix,
)
from ragul.lexer import Token, TT
from ragul.errors import DiagnosticBag, E002


# ---------------------------------------------------------------------------
# Suffix layer classification
# ---------------------------------------------------------------------------

def _classify_suffix(s: str) -> str:
    """Return the layer name for a suffix string."""
    if s in POSSESSION_SUFFIXES:        return "possession"
    if s in ACTION_SUFFIXES:            return "action"
    if s == "-e":                       return "error"
    if s in CASE_SUFFIXES:              return "case"
    if s in SCOPE_MODIFIERS:            return "scope_modifier"
    return "aspect"


# Layer ordering: each layer must follow only layers earlier in this list
_LAYER_ORDER = ["possession", "aspect", "action", "error", "case", "scope_modifier"]

def _layer_index(layer: str) -> int:
    try:
        return _LAYER_ORDER.index(layer)
    except ValueError:
        return 1   # treat unknown as aspect


# ---------------------------------------------------------------------------
# Word builder (Pass 1)
# ---------------------------------------------------------------------------

def _build_word(token: Token, bag: DiagnosticBag) -> Word:
    """
    Parse a WORD/SCOPE_OPEN token value into a Word dataclass.
    Validates suffix layer ordering; emits E002 on violation.
    """
    value = token.value

    # Split into root + suffix list
    parts = re.split(r'(?=-)', value)   # split before each '-'
    root = parts[0]
    raw_suffixes = [p for p in parts[1:] if p]

    # Collect layers
    possession: str | None  = None
    aspects:    list[str]   = []
    action:     str | None  = None
    error:      bool        = False
    case:       str         = ""
    scope_mods: list[str]   = []

    last_layer_idx = -1

    for suf in raw_suffixes:
        layer = _classify_suffix(suf)
        idx   = _layer_index(layer)

        # Allow repeated aspects
        if layer == "aspect" and last_layer_idx == _layer_index("aspect"):
            aspects.append(suf)
            continue

        if idx < last_layer_idx and layer not in ("scope_modifier",):
            # Layer order violation
            bag.add(E002(
                file=bag.file, line=token.line,
                suffix=suf,
                position=f"{layer} after {_LAYER_ORDER[last_layer_idx]}",
                offending=value,
            ))
            # Continue parsing best-effort
        last_layer_idx = max(last_layer_idx, idx)

        if layer == "possession":
            possession = suf
        elif layer == "aspect":
            aspects.append(suf)
        elif layer == "action":
            action = suf
        elif layer == "error":
            error = True
        elif layer == "case":
            case = suf
        elif layer == "scope_modifier":
            scope_mods.append(suf)

    return Word(
        root=root,
        possession=possession,
        aspects=aspects,
        action=action,
        error=error,
        case=case,
        source_text=value,
        line=token.line,
    )


# ---------------------------------------------------------------------------
# Scope metadata extraction
# ---------------------------------------------------------------------------

def _scope_from_word(word: Word, token: Token) -> Scope:
    """Build a Scope from a SCOPE_OPEN word."""
    # The scope name is the root (possibly with possession suffix as part of name)
    name = word.root

    # Determine scope kind from aspects / action / case used as scope modifiers
    full = token.value
    is_effect      = "-hatás"     in full
    is_module      = "-modul"     in full
    # Must be exact -ha, not -hatás or -hanem etc.
    import re as _re
    is_conditional = bool(_re.search(r'-ha(?!tás|nem|tvány|szn|jtó)', full))
    is_contract    = "-szerződés" in full

    loop_kind: str | None = None
    is_loop = False
    for lk in ("míg", "ig", "mindegyik", "gyűjt"):
        if f"-{lk}" in full:
            loop_kind = lk
            is_loop   = True
            break

    possession = word.possession

    # Build condition_word for -ha scopes: the scope opener's root+aspects
    # encode the condition expression (e.g. "szám-0-felett" from szám-0-felett-ha).
    condition_word = None
    if is_conditional:
        condition_word = Word(
            root=word.root,
            aspects=list(word.aspects),
            source_text=token.value,
            line=token.line,
        )

    return Scope(
        name=name,
        possession=possession,
        is_effect=is_effect,
        is_module=is_module,
        is_conditional=is_conditional,
        is_loop=is_loop,
        loop_kind=loop_kind,
        is_contract=is_contract,
        condition_word=condition_word,
        line=token.line,
    )


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------

class Parser:
    """
    Converts a token stream into a Scope tree.

    Usage:
        parser = Parser(tokens, filename="main.ragul")
        root_scope = parser.parse()
    """

    def __init__(self, tokens: list[Token], filename: str = "<string>") -> None:
        self.tokens   = tokens
        self.filename = filename
        self.bag      = DiagnosticBag(filename)
        self._pos     = 0

    # ------------------------------------------------------------------
    # Token navigation helpers
    # ------------------------------------------------------------------

    def _peek(self) -> Token:
        if self._pos < len(self.tokens):
            return self.tokens[self._pos]
        return Token(TT.EOF, "", 0, 0)

    def _advance(self) -> Token:
        tok = self._peek()
        self._pos += 1
        return tok

    def _at(self, *tts: TT) -> bool:
        return self._peek().type in tts

    # ------------------------------------------------------------------
    # Main parse entry
    # ------------------------------------------------------------------

    def parse(self) -> Scope:
        """Parse the full token stream and return the root Scope."""
        root = Scope(name="__root__")
        self._parse_scope_body(root)
        return root

    # ------------------------------------------------------------------
    # Scope body parser
    # ------------------------------------------------------------------

    def _parse_scope_body(self, scope: Scope) -> None:
        """
        Parse sentences and child scopes until we hit a DEDENT, EOF,
        or a standalone branch opener (-hanem, -hibára).
        """
        current_words: list[Word] = []
        current_line:  int        = 0

        while not self._at(TT.EOF, TT.DEDENT, TT.MINUS_HANEM, TT.MINUS_HIBARA):
            tok = self._peek()

            # ---- INDENT → child scope begins ----
            if tok.type == TT.INDENT:
                self._advance()  # consume INDENT
                if scope.children:
                    child = scope.children[-1]
                    self._parse_scope_body(child)
                # Consume matching DEDENT first, THEN look for siblings.
                # Siblings (-hanem, -hibára) appear at the same indent level
                # as the parent scope opener, AFTER the DEDENT token.
                if self._at(TT.DEDENT):
                    self._advance()
                if scope.children:
                    self._parse_siblings(scope.children[-1])
                continue

            # ---- FULLSTOP → end of sentence ----
            if tok.type == TT.FULLSTOP:
                self._advance()
                if current_words:
                    # Resolve -val bindings before storing
                    resolved = _resolve_val_args(current_words)
                    scope.sentences.append(Sentence(resolved, current_line))
                    current_words = []
                    current_line  = 0
                continue

            # ---- SCOPE_OPEN word → new child scope ----
            if tok.type == TT.SCOPE_OPEN:
                self._advance()
                word  = _build_word(tok, self.bag)
                child = _scope_from_word(word, tok)
                scope.add_child(child)
                current_words = []  # scope opener is not part of a sentence
                current_line  = 0   # reset so next sentence picks up its own line
                # Do NOT consume INDENT here — the main loop will see it
                continue

            # ---- LIST literal ----
            if tok.type == TT.LIST_OPEN:
                list_word = self._parse_list_literal(tok.line)
                if current_line == 0:
                    current_line = tok.line
                # Absorb a trailing suffix token (e.g. [1,2,3]-t → __list__ with case -t)
                nxt = self._peek()
                if nxt.type == TT.WORD:
                    trial = _build_word(nxt, DiagnosticBag(self.filename))
                    if trial.root == "" and (trial.case or trial.aspects or trial.action):
                        self._advance()
                        list_word.case    = trial.case
                        list_word.aspects = trial.aspects
                        list_word.action  = trial.action
                        list_word.error   = trial.error
                current_words.append(list_word)
                continue

            # ---- Regular WORD ----
            if tok.type == TT.WORD:
                self._advance()
                word = _build_word(tok, self.bag)
                if current_line == 0:
                    current_line = tok.line
                # If the word has a trailing empty aspect '-', the next
                # STRING/NUMBER/LIST is an inline argument — merge it.
                while word.aspects and word.aspects[-1] == "-":
                    word.aspects.pop()  # remove the dangling -
                    nxt = self._peek()
                    if nxt.type == TT.STRING:
                        self._advance()
                        # String literal becomes an inline aspect arg placeholder
                        # Store as a special aspect: __str__:<value>
                        inline_aspect = f"__str__:{nxt.value}"
                        word.aspects.append(inline_aspect)
                    elif nxt.type == TT.NUMBER:
                        self._advance()
                        word.aspects.append(nxt.value)  # numeric inline arg
                    elif nxt.type == TT.LIST_OPEN:
                        list_word = self._parse_list_literal(nxt.line)
                        word.val_args.append(list_word)
                    else:
                        break  # nothing to absorb
                    # Now absorb any following suffix token that continues the chain
                    nxt2 = self._peek()
                    if nxt2.type == TT.WORD:
                        trial = _build_word(nxt2, DiagnosticBag(self.filename))
                        if trial.root == "" and (trial.case or trial.aspects or trial.action):
                            self._advance()
                            word.aspects.extend(trial.aspects)
                            if trial.action: word.action = trial.action
                            if trial.error:  word.error  = True
                            if trial.case:   word.case   = trial.case
                current_words.append(word)
                continue

            # ---- NUMBER / STRING literals → synthesise Words, absorb trailing suffix ----
            if tok.type in (TT.NUMBER, TT.STRING):
                self._advance()
                # STRING tokens have quotes stripped by the lexer; re-add them
                # so _resolve_root can distinguish "42" (str) from 42 (num).
                root_val = f'"{tok.value}"' if tok.type == TT.STRING else tok.value
                # Peek: if next token is a bare suffix word (empty root + case),
                # absorb it so "hello"-t becomes one Word, not two.
                nxt = self._peek()
                absorbed_case = ""
                absorbed_aspects: list[str] = []
                absorbed_action = None
                absorbed_error = False
                if nxt.type == TT.WORD:
                    # Build a trial word to see if it has an empty root
                    trial = _build_word(nxt, DiagnosticBag(self.filename))
                    if trial.root == "" and (trial.case or trial.aspects or trial.action):
                        self._advance()  # consume the suffix token
                        absorbed_case    = trial.case
                        absorbed_aspects = trial.aspects
                        absorbed_action  = trial.action
                        absorbed_error   = trial.error
                lit_word = Word(
                    root=root_val,
                    aspects=absorbed_aspects,
                    action=absorbed_action,
                    error=absorbed_error,
                    case=absorbed_case,
                    source_text=root_val + absorbed_case,
                    line=tok.line,
                )
                if current_line == 0:
                    current_line = tok.line
                current_words.append(lit_word)
                continue

            # ---- Skip bare NEWLINEs / unknown ----
            self._advance()

        # Any leftover words without a fullstop (lenient parse)
        if current_words:
            scope.sentences.append(Sentence(current_words, current_line))

    def _parse_siblings(self, scope: Scope) -> None:
        """
        After a scope body, check for -hanem / -hibára / -különben-ha
        sibling blocks and attach them to the scope.
        """
        while self._at(TT.MINUS_HANEM, TT.MINUS_HIBARA):
            tok = self._advance()

            sibling = Scope(name=tok.value.lstrip("-"))
            if self._at(TT.INDENT):
                self._advance()
                self._parse_scope_body(sibling)
                if self._at(TT.DEDENT):
                    self._advance()

            if tok.type == TT.MINUS_HANEM:
                scope.else_branch = sibling
            elif tok.type == TT.MINUS_HIBARA:
                scope.error_handler = sibling

    def _parse_list_literal(self, line: int) -> Word:
        """Consume a list literal [...] and return a synthetic Word."""
        self._advance()  # consume [
        elements: list[Word] = []

        while not self._at(TT.LIST_CLOSE, TT.EOF):
            tok = self._peek()
            if tok.type == TT.LIST_OPEN:
                elements.append(self._parse_list_literal(tok.line))
            elif tok.type in (TT.NUMBER, TT.STRING):
                self._advance()
                elements.append(Word(root=tok.value, source_text=tok.value, line=tok.line))
            elif tok.type == TT.WORD:
                self._advance()
                elements.append(_build_word(tok, self.bag))
            else:
                self._advance()  # skip commas, spaces

        if self._at(TT.LIST_CLOSE):
            self._advance()  # consume ]

        # Represent as a synthetic Word with root "__list__" and val_args = elements
        return Word(
            root="__list__",
            val_args=elements,
            source_text="[...]",
            line=line,
        )


# ---------------------------------------------------------------------------
# -val argument resolution
# ---------------------------------------------------------------------------

def _resolve_val_args(words: list[Word]) -> list[Word]:
    """
    Assign -val argument words to the preceding word that needs them.
    A word with aspects needs -val args; they are consumed left-to-right.

    Heuristic: a word whose case is -val with no aspects is an argument,
    not a standalone root.
    """
    # For now: return words as-is; full resolution happens in the interpreter
    # where the dependency graph provides more context.
    return words


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def parse(tokens: list[Token], filename: str = "<string>") -> tuple[Scope, DiagnosticBag]:
    """Convenience function: parse token list and return (root_scope, diagnostics)."""
    p = Parser(tokens, filename)
    tree = p.parse()
    return tree, p.bag
