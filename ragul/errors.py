"""
ragul/errors.py — Structured error and warning types for the Ragul compiler.

Error codes:
  E001  Type        Root guard failure — wrong type for suffix
  E002  Syntax      Suffix layer order violation
  E003  Concurrency Parallel write conflict
  E004  Effect      Effectful call from pure scope
  E005  Type        Unhandled vagy type
  E006  Scope       Root referenced outside its scope
  E007  Module      Module name cannot be resolved
  E008  Type        Suffix contract violation — argument type mismatch
  E009  OOP         Field mutation outside -hatás scope

Warning codes:
  W001  Harmony     Type harmony warning — chain crosses types without bridge
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR   = "ERROR"
    WARNING = "WARN"


@dataclass
class RagulDiagnostic:
    """Base class for errors and warnings."""
    code:       str          # "E001" … "E009", "W001"
    severity:   Severity
    file:       str
    line:       int
    message:    str          # one-sentence description
    offending:  str = ""     # the offending token / word / sentence
    detail:     str = ""     # expected vs found
    suggestion: str = ""     # actionable fix hint

    @property
    def is_error(self) -> bool:
        return self.severity == Severity.ERROR

    def format(self) -> str:
        lines = [
            f"{self.severity.value}  {self.file}:{self.line}  {self.code}",
            f"  {self.message}",
        ]
        if self.offending:
            lines.append(f"    {self.offending}")
        if self.detail:
            lines.append(f"  {self.detail}")
        if self.suggestion:
            lines.append(f"  → {self.suggestion}")
        return "\n".join(lines)

    def __str__(self) -> str:
        return self.format()


class RagulError(RagulDiagnostic):
    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(severity=Severity.ERROR, **kwargs)


class RagulWarning(RagulDiagnostic):
    def __init__(self, **kwargs):  # type: ignore[no-untyped-def]
        super().__init__(severity=Severity.WARNING, **kwargs)


# ---------------------------------------------------------------------------
# Factory functions — one per error / warning code
# ---------------------------------------------------------------------------

def E001(file: str, line: int, suffix: str, expected_type: str, got_type: str,
         offending: str = "") -> RagulError:
    """Root guard failure — suffix expects a different type."""
    return RagulError(
        code="E001",
        file=file, line=line,
        message=f"Suffix {suffix} expects {expected_type}, but root is {got_type}.",
        offending=offending,
        detail=f"Expected root type: {expected_type}  |  Got: {got_type}",
        suggestion=(
            f"Use a {expected_type} root, or add a bridge suffix to convert "
            f"{got_type} → {expected_type} first."
        ),
    )


def E002(file: str, line: int, suffix: str, position: str, offending: str = "") -> RagulError:
    """Suffix layer order violation."""
    return RagulError(
        code="E002",
        file=file, line=line,
        message=f"Suffix {suffix} appears in wrong position ({position}) in chain.",
        offending=offending,
        detail="Expected order: root - [possession] - [aspect(s)] - [action] - [error] - case",
        suggestion="Reorder the suffix chain to match the required layer hierarchy.",
    )


def E003(file: str, line: int, root: str, line1: int, line2: int) -> RagulError:
    """Parallel write conflict — same root written by two independent sentences."""
    return RagulError(
        code="E003",
        file=file, line=line,
        message=f"Root '{root}' is written by two independent sentences — parallel write conflict.",
        offending=f"  {root}-ba ... (line {line1})\n    {root}-ba ... (line {line2})",
        detail="Two independent branches cannot write to the same root.",
        suggestion=(
            f"Rename one target root, or create a dependency between the two sentences "
            f"so they are sequenced rather than parallel."
        ),
    )


def E004(file: str, line: int, suffix: str, scope_name: str, offending: str = "") -> RagulError:
    """Effectful call from pure scope."""
    return RagulError(
        code="E004",
        file=file, line=line,
        message=f"Effectful suffix {suffix} called from pure scope '{scope_name}'.",
        offending=offending,
        detail="Effect suffixes can only be called from -hatás scopes.",
        suggestion=(
            f"Wrap scope '{scope_name}' with -nk-hatás, or remove the effectful call."
        ),
    )


def E005(file: str, line: int, root: str, vagy_type: str, offending: str = "") -> RagulError:
    """Unhandled vagy (fallible) type."""
    return RagulError(
        code="E005",
        file=file, line=line,
        message=f"Root '{root}' is {vagy_type} — both cases must be handled.",
        offending=offending,
        detail="A vagy type requires explicit error handling before use.",
        suggestion=(
            "Add -va-e to propagate the error upward, or add a -hibára block "
            "to handle it explicitly."
        ),
    )


def E006(file: str, line: int, root: str, defined_scope: str, offending: str = "") -> RagulError:
    """Root referenced outside its scope."""
    return RagulError(
        code="E006",
        file=file, line=line,
        message=f"Root '{root}' is referenced outside its defining scope '{defined_scope}'.",
        offending=offending,
        detail=f"'{root}' was defined inside '{defined_scope}' and does not exist here.",
        suggestion=(
            f"Move the reference inside '{defined_scope}', or return the value "
            f"from '{defined_scope}' and bind it to a new root in the outer scope."
        ),
    )


def E007(file: str, line: int, module_name: str, searched_paths: list[str]) -> RagulError:
    """Module name cannot be resolved."""
    paths_str = ", ".join(f"'{p}'" for p in searched_paths) if searched_paths else "(none configured)"
    return RagulError(
        code="E007",
        file=file, line=line,
        message=f"Module '{module_name}' cannot be resolved.",
        detail=f"Searched: {paths_str}",
        suggestion=(
            f"Ensure '{module_name}.ragul' exists in a directory listed in "
            f"modulok.utvonalak in ragul.config, or check the module name spelling."
        ),
    )


def E008(file: str, line: int, suffix: str, arg_pos: int,
         expected_type: str, got_type: str, offending: str = "") -> RagulError:
    """Suffix contract violation — argument type mismatch."""
    return RagulError(
        code="E008",
        file=file, line=line,
        message=(
            f"Suffix {suffix} argument {arg_pos} expects {expected_type}, "
            f"but got {got_type}."
        ),
        offending=offending,
        detail=f"Argument {arg_pos} type: expected {expected_type}  |  got {got_type}",
        suggestion=f"Pass a {expected_type} value as argument {arg_pos} to {suffix}.",
    )


def E009(file: str, line: int, field_name: str, scope_name: str,
         offending: str = "") -> RagulError:
    """Field mutation outside -hatás scope."""
    return RagulError(
        code="E009",
        file=file, line=line,
        message=(
            f"Field '{field_name}' is mutated outside a -hatás scope "
            f"(in '{scope_name}')."
        ),
        offending=offending,
        detail="Direct field mutation is only permitted inside -hatás scopes.",
        suggestion=(
            f"Move the mutation into a -hatás scope, or return a new instance "
            f"with the updated field value instead."
        ),
    )


def W001(file: str, line: int, from_type: str, to_type: str, offending: str = "") -> RagulWarning:
    """Type harmony warning — chain crosses type boundary without a bridge suffix."""
    return RagulWarning(
        code="W001",
        file=file, line=line,
        message=(
            f"Suffix chain crosses type boundary from {from_type} to {to_type} "
            f"without a bridge suffix."
        ),
        offending=offending,
        detail=f"Type transition: {from_type} → {to_type}",
        suggestion=(
            f"Add a bridge suffix (e.g. -szöteggé, -számmá) to make the "
            f"type conversion explicit."
        ),
    )


# ---------------------------------------------------------------------------
# Compile-time error collection
# ---------------------------------------------------------------------------

class DiagnosticBag:
    """Collects all diagnostics during a compilation phase."""

    def __init__(self, file: str = "<unknown>") -> None:
        self.file = file
        self._items: list[RagulDiagnostic] = []

    def add(self, d: RagulDiagnostic) -> None:
        self._items.append(d)

    @property
    def errors(self) -> list[RagulDiagnostic]:
        return [d for d in self._items if d.is_error]

    @property
    def warnings(self) -> list[RagulDiagnostic]:
        return [d for d in self._items if not d.is_error]

    @property
    def has_errors(self) -> bool:
        return any(d.is_error for d in self._items)

    def format_all(self) -> str:
        return "\n\n".join(d.format() for d in self._items)

    def __len__(self) -> int:
        return len(self._items)

    def __iter__(self):  # type: ignore[override]
        return iter(self._items)
