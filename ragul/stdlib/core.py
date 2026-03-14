"""
ragul/stdlib/core.py — Core suffix implementations (always available, no import needed).

Registers:
  Arithmetic  : -össze, -kivon, -szoroz, -oszt, -maradék
  Comparison  : -felett, -alatt, -legalább, -legfeljebb
  Equality    : -egyenlő, -nemegyenlő
  Logical     : -nem, -és, -vagy
  String      : -összefűz
  Collection  : -hossz (shared with szoveg)
"""

from __future__ import annotations
from ragul.model import RagulType

# ---------------------------------------------------------------------------
# Suffix registry
# A dict mapping canonical suffix name → (python_fn, input_type_hint, output_type_hint)
# python_fn(root_value, *val_args) → result_value
# ---------------------------------------------------------------------------

SUFFIX_REGISTRY: dict[str, dict] = {}


def _reg(suffix: str, fn, input_type: RagulType, output_type: RagulType,
         arg_types: list[RagulType] | None = None) -> None:
    SUFFIX_REGISTRY[suffix] = {
        "fn": fn,
        "input_type": input_type,
        "output_type": output_type,
        "arg_types": arg_types or [],
    }


# ---------------------------------------------------------------------------
# Arithmetic — Szám → Szám
# ---------------------------------------------------------------------------

_reg("-össze",   lambda v, a: v + a,   RagulType.szam(), RagulType.szam(), [RagulType.szam()])
_reg("-kivon",   lambda v, a: v - a,   RagulType.szam(), RagulType.szam(), [RagulType.szam()])
_reg("-szoroz",  lambda v, a: v * a,   RagulType.szam(), RagulType.szam(), [RagulType.szam()])
_reg("-oszt",    lambda v, a: v / a,   RagulType.szam(), RagulType.szam(), [RagulType.szam()])
_reg("-maradék", lambda v, a: v % a,   RagulType.szam(), RagulType.szam(), [RagulType.szam()])

# ---------------------------------------------------------------------------
# Comparison — Szám → Logikai
# ---------------------------------------------------------------------------

_reg("-felett",    lambda v, a: v > a,  RagulType.szam(), RagulType.logikai(), [RagulType.szam()])
_reg("-alatt",     lambda v, a: v < a,  RagulType.szam(), RagulType.logikai(), [RagulType.szam()])
_reg("-legalább",  lambda v, a: v >= a, RagulType.szam(), RagulType.logikai(), [RagulType.szam()])
_reg("-legfeljebb",lambda v, a: v <= a, RagulType.szam(), RagulType.logikai(), [RagulType.szam()])

# ---------------------------------------------------------------------------
# Equality — any → Logikai
# ---------------------------------------------------------------------------

_ANY = RagulType.unknown()
_reg("-egyenlő",    lambda v, a: v == a, _ANY, RagulType.logikai(), [_ANY])
_reg("-nemegyenlő", lambda v, a: v != a, _ANY, RagulType.logikai(), [_ANY])

# ---------------------------------------------------------------------------
# Logical — Logikai → Logikai
# ---------------------------------------------------------------------------

_reg("-nem",  lambda v: not v,      RagulType.logikai(), RagulType.logikai())
_reg("-és",   lambda v, a: v and a, RagulType.logikai(), RagulType.logikai(), [RagulType.logikai()])
_reg("-vagy", lambda v, a: v or a,  RagulType.logikai(), RagulType.logikai(), [RagulType.logikai()])

# ---------------------------------------------------------------------------
# String concatenation
# ---------------------------------------------------------------------------

_reg("-összefűz", lambda v, a: str(v) + str(a),
     RagulType.szoveg(), RagulType.szoveg(), [RagulType.szoveg()])
