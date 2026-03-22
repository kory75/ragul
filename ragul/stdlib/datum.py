"""
ragul/stdlib/datum.py — dátum module (date/time).

Suffixes:
    -most           / -now          — current local datetime
    -dátumformáz    / -dateformat   — PHP-style format string → Szöveg
    -dátumértelmez  / -parse        — parse Szöveg → datetime | Hiba
    -év             / -year         — year (int)
    -hónap          / -month        — month 1–12
    -nap            / -day          — day 1–31
    -óra            / -hour         — hour 0–23
    -perc           / -minute       — minute 0–59
    -másodperc      / -second       — second 0–59
    -hétfőnap       / -weekday      — ISO weekday Mon=1…Sun=7
    -időbélyeg      / -timestamp    — Unix timestamp (float)
    -időpontból     / -fromseconds  — local datetime from Unix timestamp
    -napok          / -adddays      — add N days (negative = subtract)
    -órák           / -addhours     — add N hours
    -különbség      / -diffseconds  — (arg − self) in seconds

Imported via:
    dátum-ból.
"""

from __future__ import annotations
import calendar
from datetime import datetime as _datetime, timedelta
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
        "module": "dátum",
    }


_any  = RagulType.unknown()
_szam = RagulType.szam()
_szov = RagulType.szoveg()
_hiba = RagulType.hiba()
_vagy = RagulType.vagy(_any, _hiba)


# ---------------------------------------------------------------------------
# PHP-style format character dispatch
# ---------------------------------------------------------------------------

_PHP_CHARS: dict[str, Any] = {
    'Y': lambda dt: f"{dt.year:04d}",
    'y': lambda dt: f"{dt.year % 100:02d}",
    'm': lambda dt: f"{dt.month:02d}",
    'n': lambda dt: str(dt.month),
    'd': lambda dt: f"{dt.day:02d}",
    'j': lambda dt: str(dt.day),
    'H': lambda dt: f"{dt.hour:02d}",
    'G': lambda dt: str(dt.hour),
    'h': lambda dt: f"{(dt.hour % 12) or 12:02d}",
    'g': lambda dt: str((dt.hour % 12) or 12),
    'i': lambda dt: f"{dt.minute:02d}",
    's': lambda dt: f"{dt.second:02d}",
    'A': lambda dt: "AM" if dt.hour < 12 else "PM",
    'a': lambda dt: "am" if dt.hour < 12 else "pm",
    'D': lambda dt: dt.strftime("%a"),
    'l': lambda dt: dt.strftime("%A"),
    'M': lambda dt: dt.strftime("%b"),
    'F': lambda dt: dt.strftime("%B"),
    'N': lambda dt: str(dt.isoweekday()),
    'w': lambda dt: str(dt.isoweekday() % 7),
    'W': lambda dt: f"{dt.isocalendar()[1]:02d}",
    'z': lambda dt: str(dt.timetuple().tm_yday - 1),
    'U': lambda dt: str(int(dt.timestamp())),
    't': lambda dt: str(calendar.monthrange(dt.year, dt.month)[1]),
    'L': lambda dt: "1" if calendar.isleap(dt.year) else "0",
}

# PHP chars that can be translated to strptime directives for -dátumértelmez
_PHP_TO_STRPTIME: dict[str, str] = {
    'Y': '%Y', 'y': '%y',
    'm': '%m', 'd': '%d',
    'H': '%H', 'h': '%I',
    'i': '%M', 's': '%S',
    'A': '%p', 'a': '%p',
    'D': '%a', 'l': '%A',
    'M': '%b', 'F': '%B',
}

# PHP chars not supported for parsing (MVP limitation)
_PHP_PARSE_UNSUPPORTED = frozenset('nGjwWzUtL')


def _format_dt(dt: _datetime, fmt: str) -> str:
    """Walk *fmt* char-by-char, expanding PHP format codes."""
    out: list[str] = []
    i = 0
    while i < len(fmt):
        ch = fmt[i]
        if ch == '\\' and i + 1 < len(fmt):
            out.append(fmt[i + 1])
            i += 2
        elif ch in _PHP_CHARS:
            out.append(_PHP_CHARS[ch](dt))
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _php_fmt_to_strptime(fmt: str) -> str | None:
    """Convert a PHP format string to a strptime pattern.

    Returns None if the format contains unsupported parse chars.
    """
    out: list[str] = []
    i = 0
    while i < len(fmt):
        ch = fmt[i]
        if ch == '\\' and i + 1 < len(fmt):
            out.append(_re_escape(fmt[i + 1]))
            i += 2
        elif ch in _PHP_PARSE_UNSUPPORTED:
            return None
        elif ch in _PHP_TO_STRPTIME:
            out.append(_PHP_TO_STRPTIME[ch])
            i += 1
        else:
            out.append(ch)
            i += 1
    return "".join(out)


def _re_escape(ch: str) -> str:
    """Escape a literal character for a strptime pattern (minimal)."""
    return ch  # strptime doesn't need regex escaping


# ---------------------------------------------------------------------------
# Suffix implementations
# ---------------------------------------------------------------------------

def _most(v: Any) -> _datetime:
    """Return the current local datetime (input ignored)."""
    return _datetime.now()


def _dátumformáz(v: Any, fmt: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-dátumformáz expects datetime, got {type(v).__name__}")
    return _format_dt(v, str(fmt))


def _dátumértelmez(v: Any, fmt: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    strptime_fmt = _php_fmt_to_strptime(str(fmt))
    if strptime_fmt is None:
        return RagulHiba(
            f"-dátumértelmez: format '{fmt}' contains unsupported parse characters"
        )
    try:
        return _datetime.strptime(str(v), strptime_fmt)
    except ValueError as e:
        return RagulHiba(f"-dátumértelmez: {e}")


def _év(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-év expects datetime, got {type(v).__name__}")
    return v.year


def _hónap(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-hónap expects datetime, got {type(v).__name__}")
    return v.month


def _nap(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-nap expects datetime, got {type(v).__name__}")
    return v.day


def _óra(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-óra expects datetime, got {type(v).__name__}")
    return v.hour


def _perc(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-perc expects datetime, got {type(v).__name__}")
    return v.minute


def _másodperc(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-másodperc expects datetime, got {type(v).__name__}")
    return v.second


def _hétfőnap(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-hétfőnap expects datetime, got {type(v).__name__}")
    return v.isoweekday()


def _időbélyeg(v: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-időbélyeg expects datetime, got {type(v).__name__}")
    return v.timestamp()


def _időpontból(v: Any) -> _datetime:
    return _datetime.fromtimestamp(float(v))


def _napok(v: Any, n: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-napok expects datetime, got {type(v).__name__}")
    return v + timedelta(days=float(n))


def _órák(v: Any, n: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-órák expects datetime, got {type(v).__name__}")
    return v + timedelta(hours=float(n))


def _különbség(v: Any, other: Any) -> Any:
    from ragul.stdlib.modules import RagulHiba
    if not isinstance(v, _datetime):
        return RagulHiba(f"-különbség expects datetime self, got {type(v).__name__}")
    if not isinstance(other, _datetime):
        return RagulHiba(f"-különbség expects datetime arg, got {type(other).__name__}")
    return (other - v).total_seconds()


# ---------------------------------------------------------------------------
# Register
# ---------------------------------------------------------------------------

_reg("-most",          _most,          _any,  _any,  [])
_reg("-dátumformáz",   _dátumformáz,   _any,  _szov, [_szov])
_reg("-dátumértelmez", _dátumértelmez, _szov, _vagy, [_szov])
_reg("-év",            _év,            _any,  _szam, [])
_reg("-hónap",         _hónap,         _any,  _szam, [])
_reg("-nap",           _nap,           _any,  _szam, [])
_reg("-óra",           _óra,           _any,  _szam, [])
_reg("-perc",          _perc,          _any,  _szam, [])
_reg("-másodperc",     _másodperc,     _any,  _szam, [])
_reg("-hétfőnap",      _hétfőnap,      _any,  _szam, [])
_reg("-időbélyeg",     _időbélyeg,     _any,  _szam, [])
_reg("-időpontból",    _időpontból,    _szam, _any,  [])
_reg("-napok",         _napok,         _any,  _any,  [_szam])
_reg("-órák",          _órák,          _any,  _any,  [_szam])
_reg("-különbség",     _különbség,     _any,  _szam, [_any])
