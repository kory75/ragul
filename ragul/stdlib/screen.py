"""
ragul/stdlib/screen.py — képernyő module (terminal I/O primitives).

Suffixes:
    -töröl   / -clear    — clear the terminal screen
    -nyomtat / -write    — write to stdout without newline
    -kurzor  / -cursor   — move cursor to (row, col) via ANSI escape
    -billentyű / -key    — non-blocking keypress; '' if none pressed
    -rajzol  / -render   — render List[List[str]] framebuffer to terminal

Imported via:
    képernyő-ből.
"""

from __future__ import annotations
import atexit
import sys
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
        "module": "képernyő",
    }


_any   = RagulType.unknown()
_szam  = RagulType.szam()
_lista = RagulType.lista(_any)


# ---------------------------------------------------------------------------
# Windows Console API setup
#
# GetStdHandle(-11) in PowerShell returns a PSHost pipe, NOT a console handle.
# GetConsoleScreenBufferInfo on a pipe handle silently returns 0 (failure),
# leaving the CSBI struct all-zeros: vt=0, vb=0, vw=1 → only 1 char/row.
#
# Solution: open "CONOUT$" via CreateFileW — this always returns the real
# console output handle, even when stdout is redirected.
# ---------------------------------------------------------------------------

if sys.platform == "win32":
    import ctypes

    _kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]

    # Best-effort: enable VT processing (Windows Terminal / modern conhost)
    try:
        _ENABLE_VT = 0x0004
        _h = _kernel32.GetStdHandle(-11)
        _m = ctypes.c_ulong(0)
        _kernel32.GetConsoleMode(_h, ctypes.byref(_m))
        _kernel32.SetConsoleMode(_h, _m.value | _ENABLE_VT)
    except Exception:
        pass

    class _COORD(ctypes.Structure):
        _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

    class _SMALL_RECT(ctypes.Structure):
        _fields_ = [
            ("Left",   ctypes.c_short), ("Top",    ctypes.c_short),
            ("Right",  ctypes.c_short), ("Bottom", ctypes.c_short),
        ]

    class _CSBI(ctypes.Structure):
        """CONSOLE_SCREEN_BUFFER_INFO"""
        _fields_ = [
            ("dwSize",              _COORD),
            ("dwCursorPosition",    _COORD),
            ("wAttributes",         ctypes.c_ushort),
            ("srWindow",            _SMALL_RECT),
            ("dwMaximumWindowSize", _COORD),
        ]

    # Set proper return type and argtypes for all console functions.
    # Without this, handles are truncated to c_int (32-bit) on 64-bit Windows,
    # causing SetConsoleCursorPosition / WriteConsoleW to silently fail.
    _kernel32.GetStdHandle.restype  = ctypes.c_void_p
    _kernel32.GetStdHandle.argtypes = [ctypes.c_long]

    _kernel32.GetConsoleScreenBufferInfo.restype  = ctypes.c_bool
    _kernel32.GetConsoleScreenBufferInfo.argtypes = [
        ctypes.c_void_p, ctypes.c_void_p,
    ]
    _kernel32.SetConsoleCursorPosition.restype  = ctypes.c_bool
    _kernel32.SetConsoleCursorPosition.argtypes = [ctypes.c_void_p, _COORD]

    _kernel32.WriteConsoleW.restype  = ctypes.c_bool
    _kernel32.WriteConsoleW.argtypes = [
        ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_ulong,
        ctypes.POINTER(ctypes.c_ulong), ctypes.c_void_p,
    ]

    _kernel32.FillConsoleOutputCharacterW.restype  = ctypes.c_bool
    _kernel32.FillConsoleOutputCharacterW.argtypes = [
        ctypes.c_void_p, ctypes.c_wchar, ctypes.c_ulong,
        _COORD, ctypes.POINTER(ctypes.c_ulong),
    ]

    def _get_handle() -> Any:
        return _kernel32.GetStdHandle(-11)

    def _csbi() -> _CSBI | None:
        """Return screen buffer info, or None if we have no real console."""
        if not sys.stdout.isatty():
            return None
        h = _get_handle()
        if h in (None, 0):
            return None
        info = _CSBI()
        ok = _kernel32.GetConsoleScreenBufferInfo(h, ctypes.byref(info))
        if not ok:
            return None
        # A zeroed struct means the call silently returned garbage
        if info.srWindow.Right == 0 and info.srWindow.Bottom == 0:
            return None
        return info

    def _win_render(lines: list[str]) -> None:
        """
        Render *lines* at the visible viewport top using Win32 Console API only.
        No ANSI escape sequences — works even when VT processing is disabled.
        Falls back to plain sys.stdout for piped output / pytest capture.
        """
        info = _csbi()
        if info is None:
            sys.stdout.write("\n".join(lines) + "\n")
            sys.stdout.flush()
            return

        h  = _get_handle()
        vt = info.srWindow.Top
        vb = info.srWindow.Bottom
        vw = info.srWindow.Right - info.srWindow.Left + 1

        written = ctypes.c_ulong(0)
        for i, line in enumerate(lines):
            if vt + i > vb:
                break
            _kernel32.SetConsoleCursorPosition(h, _COORD(0, vt + i))
            text = line[:vw].ljust(vw)
            _kernel32.WriteConsoleW(h, text, len(text),
                                    ctypes.byref(written), None)

        # Park cursor just below the grid so _nyomtat writes the score there
        park = _COORD(0, min(vt + len(lines), vb))
        _kernel32.SetConsoleCursorPosition(h, park)

    def _win_clear() -> None:
        """Clear the visible viewport using Win32 Console API."""
        info = _csbi()
        if info is None:
            return
        h  = _get_handle()
        vt = info.srWindow.Top
        vb = info.srWindow.Bottom
        vw = info.srWindow.Right - info.srWindow.Left + 1
        blank   = " " * vw
        written = ctypes.c_ulong(0)
        for row in range(vt, vb + 1):
            _kernel32.SetConsoleCursorPosition(h, _COORD(0, row))
            _kernel32.WriteConsoleW(h, blank, vw,
                                    ctypes.byref(written), None)
        _kernel32.SetConsoleCursorPosition(h, _COORD(0, vt))


# ---------------------------------------------------------------------------
# Alternate screen buffer (Unix / macOS / Windows Terminal)
# ---------------------------------------------------------------------------

_in_alt_screen: bool = False


def _enter_alt_screen() -> None:
    global _in_alt_screen
    if not _in_alt_screen:
        sys.stdout.write("\033[?1049h")
        sys.stdout.flush()
        _in_alt_screen = True
        atexit.register(_exit_alt_screen)


def _exit_alt_screen() -> None:
    global _in_alt_screen
    if _in_alt_screen:
        sys.stdout.write("\033[?1049l")
        sys.stdout.flush()
        _in_alt_screen = False


# ---------------------------------------------------------------------------
# -töröl / -clear
# ---------------------------------------------------------------------------

def _töröl(v: Any) -> Any:
    if sys.platform == "win32":
        _win_clear()
    elif _in_alt_screen:
        _exit_alt_screen()
    else:
        sys.stdout.write("\033[2J\033[H")
        sys.stdout.flush()
    return v


# ---------------------------------------------------------------------------
# -nyomtat / -write
# ---------------------------------------------------------------------------

def _nyomtat(v: Any) -> Any:
    sys.stdout.write(str(v))
    sys.stdout.flush()
    return v


# ---------------------------------------------------------------------------
# -kurzor / -cursor
# ---------------------------------------------------------------------------

def _kurzor(v: Any, row: Any, col: Any) -> Any:
    if sys.platform == "win32":
        info = _csbi()
        if info is not None:
            vt  = info.srWindow.Top
            pos = _COORD(int(col) - 1, vt + int(row) - 1)
            _kernel32.SetConsoleCursorPosition(_get_handle(), pos)
            return v
    sys.stdout.write(f"\033[{int(row)};{int(col)}H")
    sys.stdout.flush()
    return v


# ---------------------------------------------------------------------------
# -billentyű / -key
# ---------------------------------------------------------------------------

def _billentyű(v: Any) -> Any:
    if sys.platform == "win32":
        return _key_win()
    return _key_unix()


def _key_win() -> str:
    try:
        import msvcrt
        if msvcrt.kbhit():  # type: ignore[attr-defined]
            ch = msvcrt.getwch()  # type: ignore[attr-defined]
            if ch in ("\x00", "\xe0"):
                ch2 = msvcrt.getwch()  # type: ignore[attr-defined]
                return {"H": "UP", "P": "DOWN", "K": "LEFT", "M": "RIGHT"}.get(ch2, ch + ch2)
            return ch
    except Exception:
        pass
    return ""


def _key_unix() -> str:
    try:
        import tty
        import termios
        import select
        fd  = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ready, _, _ = select.select([fd], [], [], 0)
            if ready:
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    r2, _, _ = select.select([fd], [], [], 0.05)
                    if r2:
                        ch2 = sys.stdin.read(1)
                        if ch2 == "[":
                            r3, _, _ = select.select([fd], [], [], 0.05)
                            if r3:
                                ch3 = sys.stdin.read(1)
                                return {"A": "UP", "B": "DOWN",
                                        "C": "RIGHT", "D": "LEFT"}.get(ch3, ch + ch2 + ch3)
                return ch
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)
    except Exception:
        pass
    return ""


# ---------------------------------------------------------------------------
# -rajzol / -render
# ---------------------------------------------------------------------------

def _rajzol(v: Any) -> Any:
    """
    Render a List[List[str]] framebuffer to the terminal.

    Windows: CONOUT$ handle + SetConsoleCursorPosition + WriteConsoleW.
             No ANSI/VT sequences — works in cmd and PowerShell.
    Other:   Alternate screen buffer + ANSI clear.
    """
    lines: list[str] = []
    if isinstance(v, list):
        for row in v:
            if isinstance(row, list):
                lines.append("".join(str(c) for c in row))
            else:
                lines.append(str(row))

    if sys.platform == "win32":
        _win_render(lines)
    else:
        _enter_alt_screen()
        sys.stdout.write("\033[H\033[J")
        sys.stdout.write("\n".join(lines) + "\n")
        sys.stdout.flush()

    return v


# ---------------------------------------------------------------------------
# Register suffixes
# ---------------------------------------------------------------------------

_reg("-töröl",     _töröl,     _any,   _any)
_reg("-nyomtat",   _nyomtat,   _any,   _any)
_reg("-kurzor",    _kurzor,    _any,   _any,  [_szam, _szam])
_reg("-billentyű", _billentyű, _any,   _any)
_reg("-rajzol",    _rajzol,    _lista, _lista)
