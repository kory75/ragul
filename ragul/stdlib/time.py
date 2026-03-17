"""
ragul/stdlib/time.py — idő module (timing).

Suffixes:
    -vár / -sleep — sleep for N milliseconds; pass-through

Imported via:
    idő-ből.
"""

from __future__ import annotations
import time as _time
from typing import Any

from ragul.model import RagulType
from ragul.stdlib.core import SUFFIX_REGISTRY


def _reg(suffix: str, fn, input_type: RagulType, output_type: RagulType,
         arg_types: list[RagulType] | None = None) -> None:
    SUFFIX_REGISTRY[suffix] = {
        "fn": fn,
        "input_type": input_type,
        "output_type": output_type,
        "arg_types": arg_types or [],
        "module": "idő",
    }


_any  = RagulType.unknown()
_szam = RagulType.szam()


# ---------------------------------------------------------------------------
# -vár / -sleep
# ---------------------------------------------------------------------------

def _vár(v: Any, ms: Any) -> Any:
    """Sleep for *ms* milliseconds. Pass-through: returns v."""
    _time.sleep(float(ms) / 1000.0)
    return v


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

_reg("-vár", _vár, _any, _any, [_szam])
