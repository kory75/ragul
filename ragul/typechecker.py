"""
ragul/typechecker.py — Static type checker for the Ragul language.

Performs two-level enforcement per spec §3.5:
  1. Root guard  — does the root's type support this suffix at all?
  2. Suffix guard — does the contract accept the root's concrete type?

Also enforces:
  E003  Parallel write conflict
  E004  Effectful call from pure scope
  E005  Unhandled vagy type
  E009  Field mutation outside -hatás scope
  W001  Type harmony warning (chain crosses type without bridge)

Usage:
    checker = TypeChecker(scope_tree, filename, config)
    bag = checker.check()
"""

from __future__ import annotations
import re
from pathlib import Path
from ragul.model import Word, Sentence, Scope, RagulType, TYPE_ALIAS_TABLE, normalise_type_name, suffix_display
from ragul.errors import DiagnosticBag, E001, E003, E004, E005, E006, E007, E009, W001
from ragul.config import RagulConfig
from ragul.stdlib.core import SUFFIX_REGISTRY
import ragul.stdlib.modules  # noqa: F401 — side-effect: registers module suffixes into SUFFIX_REGISTRY


# ---------------------------------------------------------------------------
# Effect suffixes — calling these from a pure scope is E004
# ---------------------------------------------------------------------------

EFFECT_SUFFIX_NAMES = frozenset({
    # Output channels
    "képernyőre", "stdout",
    "stderr",
    "fájlra", "fileout",
    "hálózatra", "netout",
    # Input channels
    "bemenetről", "stdin",
    "fájlból", "filein",
    "fájlról",       # harmonic alias, kept for backwards compat
    "hálózatból", "netin",
    "hálózatról",    # harmonic alias
})

# Suffixes that return a fallible vagy type
FALLIBLE_SUFFIXES = frozenset({"-számmá", "-fájlolvasó", "-fájlból", "-fájlra"})

# Bridge suffixes that change element type
BRIDGE_SUFFIXES = frozenset({"-szöteggé", "-számmá", "-szöveggé"})

# Built-in stdlib module names — always resolve without E007
STDLIB_MODULES = frozenset({
    "matematika", "math",
    "szöveg", "szoveg", "string", "text",
    "lista", "list",
    "adatok", "data",
})


# ---------------------------------------------------------------------------
# Type environment
# ---------------------------------------------------------------------------

class TypeEnv:
    """Maps root names to their inferred RagulType within a scope."""

    def __init__(self, parent: "TypeEnv | None" = None) -> None:
        self._bindings: dict[str, RagulType] = {}
        self.parent = parent

    def define(self, name: str, t: RagulType) -> None:
        self._bindings[name] = t

    def get(self, name: str) -> RagulType | None:
        if name in self._bindings:
            return self._bindings[name]
        if self.parent:
            return self.parent.get(name)
        return None

    def all_names(self) -> set[str]:
        names = set(self._bindings.keys())
        if self.parent:
            names |= self.parent.all_names()
        return names


# ---------------------------------------------------------------------------
# Type inference helpers
# ---------------------------------------------------------------------------

def _infer_literal(root: str) -> RagulType:
    """Infer type of a bare literal root."""
    if root in ("igaz", "hamis"):
        return RagulType.logikai()
    try:
        float(root)
        return RagulType.szam()
    except (ValueError, TypeError):
        pass
    # Type name literal (used in type annotations: 'Szám-ként', 'Num-ként', etc.)
    _TYPE_NAME_MAP = {
        "Szám": RagulType.szam(),
        "Szöveg": RagulType.szoveg(),
        "Logikai": RagulType.logikai(),
        "Hiba": RagulType.hiba(),
        "Lista": RagulType.lista(RagulType.unknown()),
    }
    canonical = normalise_type_name(root)
    if canonical in _TYPE_NAME_MAP:
        return _TYPE_NAME_MAP[canonical]
    # Treat anything else as Szöveg (string or variable — resolved at runtime)
    return RagulType.szoveg()


def _infer_suffix_output(input_type: RagulType, aspect: str) -> RagulType:
    """
    Given an input type and an aspect suffix, return the output type.
    Returns RagulType.unknown() if the suffix is not in the registry.
    """
    bare = aspect.lstrip("-")

    # Inline literal argument — not a real suffix
    if aspect.startswith("__str__:"):
        return input_type  # passes through

    # Double-dash negative number inline arg ('--3' → -3)
    if aspect.startswith('--') and len(aspect) > 2:
        try:
            float(aspect[1:])
            return input_type
        except (ValueError, TypeError):
            pass

    # Numeric inline arg
    try:
        float(bare)
        return input_type  # inline arg, not a transformation
    except (ValueError, TypeError):
        pass

    entry = SUFFIX_REGISTRY.get(aspect)
    if entry:
        return entry["output_type"]

    return RagulType.unknown()


# ---------------------------------------------------------------------------
# Type Checker
# ---------------------------------------------------------------------------

class TypeChecker:

    def __init__(self, root_scope: Scope, filename: str = "<unknown>",
                 config: RagulConfig | None = None,
                 source: str = "") -> None:
        self.root_scope = root_scope
        self.filename   = filename
        self.config     = config or RagulConfig()
        self.bag        = DiagnosticBag(filename)
        if source:
            self.bag.source_lines = source.splitlines()
        # Source directory for module resolution
        self._source_dir: Path = (
            Path(filename).parent if filename not in ("<unknown>", "<test>", "<repl>")
            else Path.cwd()
        )
        # Collect all user-defined scope names for lookup
        self._user_scopes: dict[str, Scope] = {}
        self._collect_scopes(root_scope)
        # Pre-collect all root definitions across the tree (for E006)
        self._all_definitions: dict[str, str] = {}  # root → defining scope name
        self._collect_all_definitions(root_scope, "<root>")

    def _collect_scopes(self, scope: Scope) -> None:
        for child in scope.children:
            self._user_scopes[child.name] = child
            self._collect_scopes(child)

    def _collect_all_definitions(self, scope: Scope, scope_name: str) -> None:
        """Pre-pass: record every root that is written (via -ba/-be) and in which scope."""
        for sentence in scope.sentences:
            for word in sentence.words:
                if word.case in ("-ba", "-be"):
                    self._all_definitions[word.root] = scope_name
        for child in scope.children:
            self._collect_all_definitions(child, child.name)

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------

    def check(self) -> DiagnosticBag:
        """Run all checks and return the diagnostic bag."""
        root_env = TypeEnv()
        self._check_scope(self.root_scope, root_env, in_effect=False)
        return self.bag

    # ------------------------------------------------------------------
    # Import checker (E007)
    # ------------------------------------------------------------------

    def _is_import_sentence(self, sentence: Sentence) -> bool:
        """
        An import sentence has no assignment target (-ba/-be) and contains
        a word with case -ból whose root is a plain identifier (not a literal).
        Example: 'matematika-ból.' or 'matematika-ból  négyzetgyök-val.'
        """
        has_target = any(w.case in ("-ba", "-be") for w in sentence.words)
        if has_target:
            return False
        for w in sentence.words:
            if w.case == "-ból" and not w.aspects and not self._is_literal_root(w.root):
                return True
        return False

    def _check_imports(self, scope: Scope) -> None:
        """Emit E007 for unresolvable module imports in this scope."""
        for sentence in scope.sentences:
            if not self._is_import_sentence(sentence):
                continue
            for w in sentence.words:
                if w.case != "-ból" or w.aspects or self._is_literal_root(w.root):
                    continue
                module_name = w.root
                if module_name in STDLIB_MODULES:
                    break  # always available
                # Try filesystem resolution
                candidates: list[str] = [
                    str(self._source_dir / f"{module_name}.ragul"),
                ]
                for sp in self.config.search_paths:
                    candidates.append(str(self._source_dir / sp / f"{module_name}.ragul"))
                found = any(Path(c).is_file() for c in candidates)
                if not found:
                    self.bag.add(E007(
                        file=self.filename,
                        line=sentence.line,
                        module_name=module_name,
                        searched_paths=candidates,
                    ))
                break  # only one module-source word per sentence

    # ------------------------------------------------------------------
    # Scope checker
    # ------------------------------------------------------------------

    def _check_scope(self, scope: Scope, env: TypeEnv, in_effect: bool) -> None:
        is_effect = in_effect or scope.is_effect
        local_env = TypeEnv(parent=env)

        # E007 — check module imports in this scope
        self._check_imports(scope)

        # Collect write targets in this scope to detect E003
        write_targets: dict[str, int] = {}  # root name → first write line

        for sentence in scope.sentences:
            self._check_sentence(sentence, local_env, is_effect, scope,
                                 write_targets)

        # Recurse into children
        for child in scope.children:
            self._check_scope(child, local_env, is_effect)

        # Check sibling blocks
        if scope.error_handler:
            self._check_scope(scope.error_handler, local_env, is_effect)
        if scope.else_branch:
            self._check_scope(scope.else_branch, local_env, is_effect)

    # ------------------------------------------------------------------
    # Sentence checker
    # ------------------------------------------------------------------

    def _check_sentence(self, sentence: Sentence, env: TypeEnv,
                        in_effect: bool, current_scope: Scope,
                        write_targets: dict[str, int]) -> None:
        """
        For assignment sentences (target-ba  source-t):
          Infer source type first, then bind target to that type.
        For all words: run checks (E001, E004, etc.).
        """
        words = sentence.words

        # --- Identify structural roles in this sentence ---
        target_word: Word | None = None
        source_word: Word | None = None
        other_words: list[Word] = []

        for w in words:
            if w.case in ("-ba", "-be"):
                target_word = w
            elif w.case in ("-t", "-ból", "-ből", ""):
                source_word = w
            else:
                other_words.append(w)

        # --- Check all words for type errors ---
        for word in words:
            inferred = self._check_word(word, env, in_effect, current_scope)

            # E005 — fallible source used without -e
            if word.case in ("-ból", "-ből", "-t", "") and inferred is not None:
                if inferred.is_fallible() and not word.error:
                    self.bag.add(E005(
                        file=self.filename,
                        line=sentence.line,
                        root=word.root,
                        vagy_type=inferred.display(),
                        offending=word.source_text,
                    ))

        # --- Bind target root type from the SOURCE (not the target word itself) ---
        if target_word is not None:
            if source_word is not None:
                source_type = self._infer_word_type(source_word, env)
            else:
                # No explicit source — target gets unknown (bare declaration)
                source_type = RagulType.unknown()

            if source_type.base != RagulType.UNKNOWN:
                env.define(target_word.root, source_type)

            # E003 — parallel write conflict (pure scopes only)
            if target_word.root in write_targets and not in_effect:
                self.bag.add(E003(
                    file=self.filename,
                    line=sentence.line,
                    root=target_word.root,
                    line1=write_targets[target_word.root],
                    line2=sentence.line,
                ))
            else:
                write_targets[target_word.root] = sentence.line

    # ------------------------------------------------------------------
    # Word type inference + checks
    # ------------------------------------------------------------------

    def _infer_word_type(self, word: Word, env: TypeEnv) -> RagulType:
        """
        Infer the output type of a word without emitting diagnostics.
        Used to determine what type flows into the target of an assignment.
        """
        root_type = self._resolve_root_type(word.root, env)
        current   = root_type

        for aspect in word.aspects:
            bare = aspect.lstrip("-")
            if aspect.startswith("__str__:"):
                continue
            try:
                float(bare); continue
            except (ValueError, TypeError):
                pass
            entry = SUFFIX_REGISTRY.get(aspect)
            if entry:
                out = entry["output_type"]
                if out.base != RagulType.UNKNOWN:
                    current = out
        return current

    def _check_word(self, word: Word, env: TypeEnv,
                    in_effect: bool, current_scope: Scope) -> RagulType | None:
        """
        Infer the output type of a word after all its suffixes are applied.
        Emits diagnostics for violations found along the way.
        Returns the final inferred type.
        """

        # --- Resolve root type ---
        root_type = self._resolve_root_type(word.root, env)

        # E006 — scope leak: root used as source but only defined in a non-ancestor scope
        if (word.case not in ("-ba", "-be")
                and env.get(word.root) is None
                and not self._is_literal_root(word.root)
                and word.root in self._all_definitions):
            defining_scope = self._all_definitions[word.root]
            self.bag.add(E006(
                file=self.filename,
                line=word.line,
                root=word.root,
                defined_scope=self._scope_display_name(defining_scope),
                offending=word.source_text,
            ))

        # --- Walk aspect chain ---
        current_type = root_type
        prev_type    = root_type

        for aspect in word.aspects:
            bare = aspect.lstrip("-")

            # Skip inline literals — they're arguments, not type transformations
            if aspect.startswith("__str__:"):
                continue
            try:
                float(bare)
                continue
            except (ValueError, TypeError):
                pass

            # E004 — effect suffix called from pure scope
            if bare in EFFECT_SUFFIX_NAMES and not in_effect:
                self.bag.add(E004(
                    file=self.filename,
                    line=word.line,
                    suffix=suffix_display(aspect),
                    scope_name=self._scope_display_name(current_scope.name),
                    offending=word.source_text,
                ))

            # Root guard (E001) — check suffix expects compatible input type
            entry = SUFFIX_REGISTRY.get(aspect)
            if entry:
                expected_input = entry["input_type"]
                if not self._types_compatible(current_type, expected_input):
                    self.bag.add(E001(
                        file=self.filename,
                        line=word.line,
                        suffix=suffix_display(aspect),
                        expected_type=expected_input.display(),
                        got_type=current_type.display(),
                        offending=word.source_text,
                    ))

                # Harmony check W001
                if self.config.harmony != "off":
                    if self._is_type_crossing(current_type, entry["output_type"]) \
                            and aspect not in BRIDGE_SUFFIXES:
                        diag = W001(
                            file=self.filename,
                            line=word.line,
                            from_type=current_type.display(),
                            to_type=entry["output_type"].display(),
                            offending=word.source_text,
                        )
                        self.bag.add(diag)
                        if self.config.harmony == "strict":
                            # Promote to error by re-adding as error
                            pass  # W001 is always a warning structurally

                # Advance type
                current_type = entry["output_type"]
                if current_type.base == RagulType.UNKNOWN:
                    current_type = prev_type  # preserve if unknown

            elif bare in self._user_scopes:
                # User-defined suffix — return type is unknown for now
                current_type = RagulType.unknown()

            prev_type = current_type

        # --- E004 on action-bearing effect channels ---
        if word.action in ("-va", "-ve"):
            if word.root in EFFECT_SUFFIX_NAMES and not in_effect:
                self.bag.add(E004(
                    file=self.filename,
                    line=word.line,
                    suffix=suffix_display(f"-{word.root}"),
                    scope_name=self._scope_display_name(current_scope.name),
                    offending=word.source_text,
                ))

        # --- E009 — field mutation outside -hatás ---
        if word.possession == "-ja" and word.case in ("-ba", "-be"):
            if not in_effect:
                self.bag.add(E009(
                    file=self.filename,
                    line=word.line,
                    field_name=word.root,
                    scope_name=self._scope_display_name(current_scope.name),
                    offending=word.source_text,
                ))

        return current_type

    # ------------------------------------------------------------------
    # Type resolution helpers
    # ------------------------------------------------------------------

    def _resolve_root_type(self, root: str, env: TypeEnv) -> RagulType:
        """Resolve the type of a root name or literal."""
        # Check environment first
        t = env.get(root)
        if t is not None:
            return t

        # Literals
        if root in ("igaz", "hamis"):
            return RagulType.logikai()
        if root == "__list__":
            return RagulType.lista(RagulType.unknown())
        try:
            if "." in root:
                float(root)
            else:
                int(root)
            return RagulType.szam()
        except (ValueError, TypeError):
            pass

        # String content
        return RagulType.szoveg()

    def _types_compatible(self, got: RagulType, expected: RagulType) -> bool:
        """
        Returns True if `got` is compatible with `expected`.
        Unknown types are always compatible (lenient mode).
        """
        if got.base == RagulType.UNKNOWN or expected.base == RagulType.UNKNOWN:
            return True
        if got == expected:
            return True
        # Lista-T is compatible with Lista-anything for collection ops
        if got.base == RagulType.LISTA and expected.base == RagulType.LISTA:
            return True
        # vagy-X-vagy-Hiba: the success type may be compatible
        if got.base == RagulType.VAGY:
            success = got.success_type()
            return self._types_compatible(success, expected)
        return False

    def _is_type_crossing(self, from_t: RagulType, to_t: RagulType) -> bool:
        """True if a suffix chain crosses a type boundary (for W001)."""
        if from_t.base == RagulType.UNKNOWN or to_t.base == RagulType.UNKNOWN:
            return False
        return from_t.base != to_t.base

    def _scope_display_name(self, name: str) -> str:
        """Return a user-friendly scope name for error messages."""
        if name in ("__root__", "__repl__"):
            return "the top-level scope"
        return f"scope '{name}'"

    def _is_literal_root(self, root: str) -> bool:
        """True if root is a compile-time literal (number, boolean, list sentinel)."""
        if root in ("igaz", "hamis", "true", "false", "__list__"):
            return True
        try:
            float(root)
            return True
        except (ValueError, TypeError):
            return False
