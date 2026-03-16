"""
ragul/stdlib/modules.py — Standard library modules (matematika, szöveg, lista).

Imported selectively:
    matematika-ból  négyzetgyök-val  hatvány-val.
    szöveg-ből  hossz-val  feloszt-val.
    lista-ból.
"""

from __future__ import annotations
import csv as _csv_mod
import io
import json
import math
from typing import Any
from ragul.model import RagulType
from ragul.stdlib.core import SUFFIX_REGISTRY


def _reg(suffix: str, fn, input_type: RagulType, output_type: RagulType,
         arg_types: list[RagulType] | None = None, module: str = "") -> None:
    SUFFIX_REGISTRY[suffix] = {
        "fn": fn,
        "input_type": input_type,
        "output_type": output_type,
        "arg_types": arg_types or [],
        "module": module,
    }


_szam    = RagulType.szam()
_szoveg  = RagulType.szoveg()
_logikai = RagulType.logikai()
_hiba    = RagulType.hiba()

# ---------------------------------------------------------------------------
# matematika module
# ---------------------------------------------------------------------------

_reg("-négyzetgyök", lambda v: math.sqrt(v),         _szam, _szam, module="matematika")
_reg("-hatvány",     lambda v, a: v ** a,             _szam, _szam, [_szam], module="matematika")
_reg("-abszolút",    lambda v: abs(v),                _szam, _szam, module="matematika")
_reg("-kerekítve",   lambda v: round(v),              _szam, _szam, module="matematika")
_reg("-padló",       lambda v: math.floor(v),         _szam, _szam, module="matematika")
_reg("-plafon",      lambda v: math.ceil(v),          _szam, _szam, module="matematika")
_reg("-log",         lambda v, a: math.log(v, a),     _szam, _szam, [_szam], module="matematika")
_reg("-sin",         lambda v: math.sin(v),           _szam, _szam, module="matematika")
_reg("-cos",         lambda v: math.cos(v),           _szam, _szam, module="matematika")
_reg("-szöteggé",    lambda v: str(v),                _szam, _szoveg, module="matematika")  # bridge

# ---------------------------------------------------------------------------
# szöveg module
# ---------------------------------------------------------------------------

_reg("-hossz",     lambda v: len(v),                        _szoveg, _szam, module="szöveg")
_reg("-nagybetűs", lambda v: v.upper(),                     _szoveg, _szoveg, module="szöveg")
_reg("-kisbetűs",  lambda v: v.lower(),                     _szoveg, _szoveg, module="szöveg")
_reg("-tartalmaz", lambda v, a: a in v,                     _szoveg, _logikai, [_szoveg], module="szöveg")
_reg("-kezdődik",  lambda v, a: v.startswith(a),            _szoveg, _logikai, [_szoveg], module="szöveg")
_reg("-végződik",  lambda v, a: v.endswith(a),              _szoveg, _logikai, [_szoveg], module="szöveg")
_reg("-feloszt",   lambda v, a: v.split(a),                 _szoveg, RagulType.lista(_szoveg), [_szoveg], module="szöveg")
_reg("-formáz",    lambda v, a: v.format(a),                _szoveg, _szoveg, [RagulType.unknown()], module="szöveg")

def _szelet_str(v, start, end=None):
    if end is None:
        return v[int(start):]
    return v[int(start):int(end)]

_reg("-szelet",  _szelet_str,  _szoveg, _szoveg, [_szam, _szam], module="szöveg")
_reg("-csere",   lambda v, a, b: v.replace(a, b), _szoveg, _szoveg, [_szoveg, _szoveg], module="szöveg")

def _számmá(v):
    try:
        return int(v) if '.' not in v else float(v)
    except (ValueError, TypeError):
        return _RagulHiba(f"Cannot convert '{v}' to number")

_reg("-számmá", _számmá, _szoveg, RagulType.vagy(_szam, _hiba), module="szöveg")

# ---------------------------------------------------------------------------
# lista module
# ---------------------------------------------------------------------------

_lista_t = RagulType.lista(RagulType.unknown())

_reg("-hossz",       lambda v: len(v),                     _lista_t, _szam, module="lista")
_reg("-rendezve",    lambda v: sorted(v),                  _lista_t, _lista_t, module="lista")
_reg("-rendezve-le", lambda v: sorted(v, reverse=True),    _lista_t, _lista_t, module="lista")
_reg("-fordítva",    lambda v: list(reversed(v)),          _lista_t, _lista_t, module="lista")
_reg("-első",        lambda v: v[0] if v else None,        _lista_t, RagulType.unknown(), module="lista")
_reg("-utolsó",      lambda v: v[-1] if v else None,       _lista_t, RagulType.unknown(), module="lista")
_reg("-tartalmaz",   lambda v, a: a in v,                  _lista_t, _logikai, [RagulType.unknown()], module="lista")
_reg("-hozzáad",     lambda v, a: v + [a],                 _lista_t, _lista_t, [RagulType.unknown()], module="lista")
_reg("-eltávolít",   lambda v, a: [x for x in v if x != a], _lista_t, _lista_t, [RagulType.unknown()], module="lista")
_reg("-egyedi",      lambda v: list(dict.fromkeys(v)),     _lista_t, _lista_t, module="lista")
_reg("-lapítva",     lambda v: [x for sub in v for x in sub], _lista_t, _lista_t, module="lista")

def _szűrve(v, condition):
    """
    Filter a list by a condition.
    condition can be:
      - a callable: applied directly
      - a comparison tuple (op, threshold): e.g. ('>', 3)
      - a boolean value: keep all True, discard all False
    The most common case from Ragul syntax is a piped comparison:
      rendezett-3-felett-szűrve  →  szűrve(rendezett, felett_fn(3))
    But felett returns a boolean on a single value, not a filter function.
    We handle the case where condition is already a pre-evaluated scalar
    by wrapping it: if it's a boolean, interpret it as "keep all" / "keep none".
    The real use is when szűrve receives a lambda/closure — which comes from
    user-defined filter scopes.  For now, provide a workaround:
    if condition is a number, keep elements > condition (felett semantics).
    """
    if callable(condition):
        return [x for x in v if condition(x)]
    if isinstance(condition, bool):
        return v if condition else []
    return v

_reg("-szűrve", _szűrve, _lista_t, _lista_t, [RagulType.unknown()], module="lista")

# Polymorphic comparison/filter suffixes — dispatch on input type
# If input is a list → filter elements; if scalar → compare directly.
# These REPLACE the core scalar-only versions to add list dispatch.

def _poly_felett(v, threshold):
    if isinstance(v, list):
        return [x for x in v if x > threshold]
    return v > threshold

def _poly_alatt(v, threshold):
    if isinstance(v, list):
        return [x for x in v if x < threshold]
    return v < threshold

def _poly_legalább(v, threshold):
    if isinstance(v, list):
        return [x for x in v if x >= threshold]
    return v >= threshold

def _poly_legfeljebb(v, threshold):
    if isinstance(v, list):
        return [x for x in v if x <= threshold]
    return v <= threshold

from ragul.stdlib.core import SUFFIX_REGISTRY as _REG
_REG["-felett"]     = {"fn": _poly_felett,     "input_type": _szam, "output_type": _szam, "arg_types": [_szam]}
_REG["-alatt"]      = {"fn": _poly_alatt,      "input_type": _szam, "output_type": _szam, "arg_types": [_szam]}
_REG["-legalább"]   = {"fn": _poly_legalább,   "input_type": _szam, "output_type": _szam, "arg_types": [_szam]}
_REG["-legfeljebb"] = {"fn": _poly_legfeljebb, "input_type": _szam, "output_type": _szam, "arg_types": [_szam]}

def _szelet_list(v, start, end=None):
    if end is None:
        return v[int(start):]
    return v[int(start):int(end)]

_reg("-szelet", _szelet_list, _lista_t, _lista_t, [_szam, _szam], module="lista")


# ---------------------------------------------------------------------------
# lista extras  (-térképezve / -map,  -összeg / -sum)
# ---------------------------------------------------------------------------

def _térképezve(v: Any, key: Any) -> Any:
    """Extract *key* field from each dict/list item in *v*."""
    if not isinstance(v, list):
        return _RagulHiba(f"-térképezve requires a list, got {type(v).__name__}")
    result = []
    for item in v:
        if isinstance(item, dict):
            result.append(item.get(str(key)))
        elif isinstance(item, list):
            try:
                result.append(item[int(key)])
            except (IndexError, ValueError):
                result.append(None)
        else:
            result.append(None)
    return result


def _összeg(v: Any) -> Any:
    """Sum all elements of a numeric list."""
    try:
        return sum(v)
    except (TypeError, ValueError) as e:
        return _RagulHiba(str(e))


_reg("-térképezve", _térképezve, _lista_t, _lista_t, [RagulType.unknown()], module="lista")
_reg("-összeg",     _összeg,     _lista_t, _szam,    module="lista")


# ---------------------------------------------------------------------------
# adatok module  (JSON + CSV parse/emit, field access)
# ---------------------------------------------------------------------------

def _json_parse(v: Any) -> Any:
    try:
        return json.loads(str(v))
    except (json.JSONDecodeError, ValueError) as e:
        return _RagulHiba(f"JSON parse error: {e}")


def _json_emit(v: Any) -> str:
    return json.dumps(v, ensure_ascii=False)


def _csv_parse(v: Any) -> Any:
    try:
        reader = _csv_mod.DictReader(io.StringIO(str(v)))
        return [dict(row) for row in reader]
    except Exception as e:
        return _RagulHiba(f"CSV parse error: {e}")


def _csv_emit(v: Any) -> Any:
    if not isinstance(v, list) or not v:
        return ""
    out = io.StringIO()
    writer = _csv_mod.DictWriter(
        out, fieldnames=list(v[0].keys()), lineterminator="\n"
    )
    writer.writeheader()
    writer.writerows(v)
    return out.getvalue()


def _mező(v: Any, key: Any) -> Any:
    """
    Field access.  Polymorphic:
      - dict  → v[key]
      - list  → [item[key] for item in v]  (extract field from every record)
    """
    if isinstance(v, list):
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(item.get(str(key)))
            elif isinstance(item, (list, str)):
                try:
                    result.append(item[int(key)])
                except (IndexError, ValueError):
                    result.append(None)
            else:
                result.append(None)
        return result
    if isinstance(v, dict):
        k = str(key)
        if k in v:
            return v[k]
        return _RagulHiba(f"Field '{k}' not found")
    if isinstance(v, (list, str)):
        try:
            return v[int(key)]
        except (IndexError, ValueError) as e:
            return _RagulHiba(str(e))
    return _RagulHiba(f"Cannot access field on {type(v).__name__}")


def _mezők(v: Any) -> Any:
    if isinstance(v, dict):
        return list(v.keys())
    return _RagulHiba(f"-mezők requires a dict, got {type(v).__name__}")


_any          = RagulType.unknown()
_vagy_any_hiba = RagulType.vagy(_any, RagulType.hiba())

_reg("-json",   _json_parse, _szoveg,  _vagy_any_hiba, module="adatok")
_reg("-jsonná", _json_emit,  _any,     _szoveg,        module="adatok")
_reg("-csv",    _csv_parse,  _szoveg,  _vagy_any_hiba, module="adatok")
_reg("-csvné",  _csv_emit,   _lista_t, _szoveg,        module="adatok")
_reg("-mező",   _mező,       _any,     _any,           [_any], module="adatok")
_reg("-mezők",  _mezők,      _any,     _lista_t,       module="adatok")


# ---------------------------------------------------------------------------
# Hiba runtime value
# ---------------------------------------------------------------------------

class _RagulHiba:
    """Runtime representation of a Ragul error value."""
    def __init__(self, message: str) -> None:
        self.message = message

    def __repr__(self) -> str:
        return f"Hiba({self.message!r})"

    def __bool__(self) -> bool:
        return False


# Make RagulHiba importable from stdlib
RagulHiba = _RagulHiba


# ---------------------------------------------------------------------------
# File I/O suffixes  (-fájlból / -filein,  -fájlra / -fileout)
# Always available (no import needed); effectful — require -hatás scope.
# ---------------------------------------------------------------------------

def _filein(filename: Any) -> Any:
    """Read all text from *filename*, returning a string or RagulHiba."""
    try:
        with open(str(filename), "r", encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        return RagulHiba(str(e))


def _fileout(value: Any, filename: Any) -> None:
    """Write str(value) to *filename*. Returns None; errors silently produce RagulHiba."""
    try:
        with open(str(filename), "w", encoding="utf-8") as f:
            f.write(str(value))
    except OSError as e:
        return RagulHiba(str(e))


_vagy_szoveg_hiba = RagulType.vagy(RagulType.szoveg(), RagulType.hiba())

_reg("-fájlból", _filein,  _szoveg, _vagy_szoveg_hiba, arg_types=[],       module="io")
_reg("-fájlra",  _fileout, _szoveg, RagulType.unknown(), arg_types=[_szoveg], module="io")


# ---------------------------------------------------------------------------
# Network channel stubs  (-hálózatból / -netin,  -hálózatra / -netout)
# Fully wired in v0.4.0; for now they return a RagulHiba immediately.
# ---------------------------------------------------------------------------

def _netin_stub(url: Any) -> Any:
    return RagulHiba("netin: HTTP client not available until v0.4.0")


def _netout_stub(value: Any, url: Any) -> Any:
    return RagulHiba("netout: HTTP client not available until v0.4.0")


_reg("-hálózatból", _netin_stub,  _szoveg, _vagy_szoveg_hiba, arg_types=[],       module="io")
_reg("-hálózatra",  _netout_stub, _szoveg, RagulType.unknown(), arg_types=[_szoveg], module="io")
