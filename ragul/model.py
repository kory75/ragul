"""
ragul/model.py — Core data model for the Ragul language compiler.

Word: flat vector representation of a suffix-chained word.
Sentence: a list of Words terminated by a full stop.
Scope: a named indentation block (function, module, class, effect, etc.)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


# ---------------------------------------------------------------------------
# Alias normalisation table
# Maps every alias (English / symbolic) → canonical Hungarian suffix
# ---------------------------------------------------------------------------

ALIAS_TABLE: dict[str, str] = {
    # Case suffixes
    "-from":        "-ból",
    "-<":           "-ból",
    "-into":        "-ba",
    "->":           "-ba",
    "-with":        "-val",
    "-&":           "-val",
    "-at":          "-nál",
    "-@":           "-nál",
    "-as":          "-ként",
    "-:":           "-ként",
    "-it":          "-t",
    "-*":           "-t",
    "-doing":       "-va",
    "-!":           "-va",
    "-else-fail":   "-e",
    "-?":           "-e",
    # Possession suffixes
    "-ours":        "-unk",
    "-mine":        "-m",
    "-yours":       "-d",
    "-its":         "-ja",
    # Loop / control aliases
    "-while":       "-míg",
    "-until":       "-ig",
    "-each":        "-mindegyik",
    "-every":       "-mindegyik",
    "-fold":        "-gyűjt",
    "-reduce":      "-gyűjt",
    "-break":       "-megszakít",
    # Harmonic variants (keep as canonical targets too)
    "-be":          "-ba",     # front-vowel variant of -ba (into)
    "-ből":         "-ból",    # front-vowel variant of -ból (from)
    "-vel":         "-val",    # front-vowel variant of -val (with)
    "-nél":         "-nál",    # front-vowel variant of -nál (at)
    "-ről":         "-ról",    # already canonical (from surface)
    "-ve":          "-va",     # front-vowel variant of -va (action)
    "-re":          "-ra",     # front-vowel variant of -ra (onto)
    "-je":          "-ja",     # front-vowel variant of -ja (its)
    "-nk":          "-unk",    # short form of -unk
    "-em":          "-m",      # variant of -m
    "-ed":          "-d",      # variant of -d
    # Scope modifier aliases
    "-effect":      "-hatás",
    "-if":          "-ha",
    "-else":        "-hanem",
    "-elif":        "-különben",
    "-catch":       "-hibára",
    "-module":      "-modul",
    # Arithmetic suffix aliases
    "-add":         "-össze",
    "-sub":         "-kivon",
    "-mul":         "-szoroz",
    "-div":         "-oszt",
    "-rem":         "-maradék",
    # Comparison suffix aliases
    "-above":       "-felett",
    "-below":       "-alatt",
    "-atleast":     "-legalább",
    "-atmost":      "-legfeljebb",
    "-eq":          "-egyenlő",
    "-neq":         "-nemegyenlő",
    # Logical suffix aliases
    "-not":         "-nem",
    "-and":         "-és",
    "-or":          "-vagy",
    # String suffix aliases (core)
    "-concat":      "-összefűz",
    # String suffix aliases (szöveg module)
    "-len":         "-hossz",
    "-upper":       "-nagybetűs",
    "-lower":       "-kisbetűs",
    "-contains":    "-tartalmaz",
    "-startswith":  "-kezdődik",
    "-endswith":    "-végződik",
    "-split":       "-feloszt",
    "-format":      "-formáz",
    "-slice":       "-szelet",
    "-replace":     "-csere",
    "-tonum":       "-számmá",
    # Math suffix aliases (matematika module)
    "-sqrt":        "-négyzetgyök",
    "-pow":         "-hatvány",
    "-abs":         "-abszolút",
    "-round":       "-kerekítve",
    "-floor":       "-padló",
    "-ceil":        "-plafon",
    "-tostr":       "-szöteggé",
    # List suffix aliases (lista module)
    "-sorted":      "-rendezve",
    "-reversed":    "-fordítva",
    "-first":       "-első",
    "-last":        "-utolsó",
    "-unique":      "-egyedi",
    "-flat":        "-lapítva",
    "-filter":      "-szűrve",
    "-append":      "-hozzáad",
    "-remove":      "-eltávolít",
    # Effect channel aliases
    "-print":       "-képernyőre",
}

# Canonical case suffixes (outermost layer)
CASE_SUFFIXES = frozenset({
    "-ból", "-ból",   # from / source
    "-ba",            # into / target
    "-val",           # with / instrument
    "-nál",           # at / context
    "-ként",          # as / role
    "-t",             # object / accusative
    "-ra",            # onto (write direction, embedded in channel names)
    "-ról",           # from-surface (read direction)
    "-e",             # error propagation (special: after action)
})

# Canonical possession suffixes (innermost layer, after root)
POSSESSION_SUFFIXES = frozenset({
    "-unk",   # ours / this scope
    "-m",     # mine / immutable
    "-d",     # yours / parameter
    "-ja",    # its / instance field
})

# Canonical action suffixes
ACTION_SUFFIXES = frozenset({"-va", "-ve"})

# Control / scope modifier suffixes (part of scope name, not word chain)
SCOPE_MODIFIERS = frozenset({
    "-hatás",    # effect scope
    "-modul",    # module scope
    "-ha",       # conditional scope
    "-hanem",    # else branch
    "-különben", # else-if
    "-míg",      # while loop
    "-ig",       # until loop
    "-mindegyik",# for-each
    "-gyűjt",    # fold/reduce
    "-megszakít",# break
    "-szerződés",# contract definition
    "-új",       # instantiation
})


def normalise_suffix(suffix: str) -> str:
    """Return the canonical form of a suffix, applying alias table."""
    return ALIAS_TABLE.get(suffix, suffix)


# Root-level keyword aliases — resolved at lex time so the parser and
# interpreter only ever see the canonical Hungarian keyword.
ROOT_ALIASES: dict[str, str] = {
    "true":  "igaz",
    "false": "hamis",
}


# Type name alias table — English → canonical Hungarian type names
TYPE_ALIAS_TABLE: dict[str, str] = {
    "Num":    "Szám",
    "Number": "Szám",
    "Str":    "Szöveg",
    "Text":   "Szöveg",
    "String": "Szöveg",
    "List":   "Lista",
    "Bool":   "Logikai",
    "Err":    "Hiba",
    "Error":  "Hiba",
    "or":     "vagy",
}


def normalise_type_name(name: str) -> str:
    """Return the canonical Hungarian type name, applying the alias table."""
    return TYPE_ALIAS_TABLE.get(name, name)


# ---------------------------------------------------------------------------
# Word — the fundamental unit
# ---------------------------------------------------------------------------

@dataclass
class Word:
    """
    Flat vector representation of a Ragul word.

    Structure:  root - [possession] - [aspect(s)] - [action] - [error] - case

    val_args: ordered list of -val / -vel bound arguments for this word's aspects.
    source_text: the original token text (for error messages).
    line: source line number.
    """
    root:        str
    possession:  str | None          = None
    aspects:     list[str]           = field(default_factory=list)
    action:      str | None          = None
    error:       bool                = False
    case:        str                 = ""
    val_args:    list["Word"]        = field(default_factory=list)
    source_text: str                 = ""
    line:        int                 = 0

    def __repr__(self) -> str:
        parts = [self.root]
        if self.possession:
            parts.append(self.possession.lstrip("-"))
        parts.extend(a.lstrip("-") for a in self.aspects)
        if self.action:
            parts.append(self.action.lstrip("-"))
        if self.error:
            parts.append("e")
        if self.case:
            parts.append(self.case.lstrip("-"))
        return "-".join(parts)


# ---------------------------------------------------------------------------
# Type representation
# ---------------------------------------------------------------------------

@dataclass
class RagulType:
    """
    Recursive type representation.

    Examples:
        Szám                → RagulType("Szám")
        Lista-Szám          → RagulType("Lista", [RagulType("Szám")])
        vagy-Szöveg-vagy-Hiba
                            → RagulType("vagy", [RagulType("Szöveg"), RagulType("Hiba")])
        Lista-Lista-Szám    → RagulType("Lista", [RagulType("Lista", [RagulType("Szám")])])
    """
    base:   str
    params: list["RagulType"] = field(default_factory=list)

    # Canonical base type names
    SZAM    = "Szám"
    SZOVEG  = "Szöveg"
    LISTA   = "Lista"
    LOGIKAI = "Logikai"
    HIBA    = "Hiba"
    VAGY    = "vagy"
    UNKNOWN = "?"

    def __repr__(self) -> str:
        if not self.params:
            return self.base
        if self.base == "Lista":
            return "Lista-" + repr(self.params[0])
        if self.base == "vagy":
            return "-vagy-".join(repr(p) for p in self.params)
        return self.base + "-" + "-".join(repr(p) for p in self.params)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RagulType):
            return False
        return self.base == other.base and self.params == other.params

    def __hash__(self) -> int:
        return hash((self.base, tuple(self.params)))

    @classmethod
    def szam(cls) -> "RagulType":
        return cls(cls.SZAM)

    @classmethod
    def szoveg(cls) -> "RagulType":
        return cls(cls.SZOVEG)

    @classmethod
    def logikai(cls) -> "RagulType":
        return cls(cls.LOGIKAI)

    @classmethod
    def hiba(cls) -> "RagulType":
        return cls(cls.HIBA)

    @classmethod
    def lista(cls, elem: "RagulType") -> "RagulType":
        return cls(cls.LISTA, [elem])

    @classmethod
    def vagy(cls, *types: "RagulType") -> "RagulType":
        return cls(cls.VAGY, list(types))

    @classmethod
    def unknown(cls) -> "RagulType":
        return cls(cls.UNKNOWN)

    def is_fallible(self) -> bool:
        """True if this is a vagy-X-vagy-Hiba type."""
        return self.base == self.VAGY and any(p.base == self.HIBA for p in self.params)

    def success_type(self) -> "RagulType":
        """For a vagy type, return the non-Hiba branch."""
        if self.base != self.VAGY:
            return self
        for p in self.params:
            if p.base != self.HIBA:
                return p
        return self


# ---------------------------------------------------------------------------
# Sentence
# ---------------------------------------------------------------------------

@dataclass
class Sentence:
    """A complete Ragul sentence — list of Words terminated by '.'"""
    words: list[Word]
    line:  int = 0


# ---------------------------------------------------------------------------
# Scope
# ---------------------------------------------------------------------------

@dataclass
class Scope:
    """
    A named indentation block.

    A Scope is simultaneously:
      - a function definition
      - a module
      - a class
      - a conditional branch
      - an effect context

    The kind is determined by the suffix_modifiers on the scope's own name word.
    """
    name:            str
    possession:      str | None        = None   # -unk, -m, -d, -ja
    is_effect:       bool              = False   # -hatás
    is_module:       bool              = False   # -modul
    is_conditional:  bool              = False   # -ha
    is_loop:         bool              = False   # -míg / -ig / -mindegyik / -gyűjt
    loop_kind:       str | None        = None    # "míg" | "ig" | "mindegyik" | "gyűjt"
    condition_word:  "Word | None"     = None        # -ha condition expression (root+aspects of scope opener)
    is_contract:     bool              = False   # -szerződés
    sentences:       list[Sentence]    = field(default_factory=list)
    children:        list["Scope"]     = field(default_factory=list)
    parent:          "Scope | None"    = field(default=None, repr=False)
    error_handler:   "Scope | None"    = None    # -hibára sibling block
    else_branch:     "Scope | None"    = None    # -hanem sibling
    elif_branches:   list["Scope"]     = field(default_factory=list)  # -különben-ha
    # Type annotations collected from -ként sentences inside the scope
    param_types:     dict[str, RagulType] = field(default_factory=dict)
    return_type:     RagulType | None  = None
    # Resolved inferred types for roots defined in this scope
    root_types:      dict[str, RagulType] = field(default_factory=dict)
    # Source line of the scope opener (SCOPE_OPEN token line)
    line:            int                  = 0

    def add_child(self, child: "Scope") -> None:
        child.parent = self
        self.children.append(child)

    def is_pure(self) -> bool:
        """True if this scope (and no ancestor) is an effect scope."""
        scope: Scope | None = self
        while scope is not None:
            if scope.is_effect:
                return False
            scope = scope.parent
        return True

    def lookup_child_scope(self, name: str) -> "Scope | None":
        for child in self.children:
            if child.name == name:
                return child
        return None

    def __repr__(self) -> str:
        modifiers = []
        if self.is_effect:    modifiers.append("hatás")
        if self.is_module:    modifiers.append("modul")
        if self.is_conditional: modifiers.append("ha")
        if self.loop_kind:    modifiers.append(self.loop_kind)
        mod_str = f"[{','.join(modifiers)}]" if modifiers else ""
        return f"Scope({self.name!r}{mod_str}, sentences={len(self.sentences)}, children={len(self.children)})"
