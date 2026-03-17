"""
tools/diagnose_console.py — diagnose Win32 console handle availability.
Run this in cmd or PowerShell to see what the console API reports.
"""
import ctypes
import sys

kernel32 = ctypes.windll.kernel32

class _COORD(ctypes.Structure):
    _fields_ = [("X", ctypes.c_short), ("Y", ctypes.c_short)]

class _SMALL_RECT(ctypes.Structure):
    _fields_ = [
        ("Left", ctypes.c_short), ("Top", ctypes.c_short),
        ("Right", ctypes.c_short), ("Bottom", ctypes.c_short),
    ]

class _CSBI(ctypes.Structure):
    _fields_ = [
        ("dwSize",              _COORD),
        ("dwCursorPosition",    _COORD),
        ("wAttributes",         ctypes.c_ushort),
        ("srWindow",            _SMALL_RECT),
        ("dwMaximumWindowSize", _COORD),
    ]

print(f"sys.platform  = {sys.platform}")
print(f"sys.stdout.isatty() = {sys.stdout.isatty()}")

# --- GetStdHandle approach ---
h_std = kernel32.GetStdHandle(-11)
print(f"\nGetStdHandle(-11) = {h_std!r}")
info1 = _CSBI()
ok1 = kernel32.GetConsoleScreenBufferInfo(h_std, ctypes.byref(info1))
print(f"GetConsoleScreenBufferInfo(std) ok={ok1}")
if ok1:
    w = info1.srWindow
    print(f"  srWindow: Left={w.Left} Top={w.Top} Right={w.Right} Bottom={w.Bottom}")
    print(f"  vw={w.Right - w.Left + 1}  viewport rows={w.Bottom - w.Top + 1}")

# --- CONOUT$ approach ---
kernel32.CreateFileW.restype  = ctypes.c_void_p
kernel32.CreateFileW.argtypes = [
    ctypes.c_wchar_p, ctypes.c_uint32, ctypes.c_uint32,
    ctypes.c_void_p,  ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p,
]
_GENERIC_WRITE = 0x40000000
_OPEN_EXISTING = 3
_FILE_SHARE_RW = 0x00000003

h_con = kernel32.CreateFileW(
    "CONOUT$", _GENERIC_WRITE, _FILE_SHARE_RW,
    None, _OPEN_EXISTING, 0, None,
)
invalid = ctypes.c_void_p(-1).value
print(f"\nCreateFileW('CONOUT$') = {h_con!r}  (INVALID={invalid!r})")
print(f"  handle valid: {h_con not in (None, 0, invalid)}")

kernel32.GetConsoleScreenBufferInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
info2 = _CSBI()
ok2 = kernel32.GetConsoleScreenBufferInfo(h_con, ctypes.byref(info2))
print(f"GetConsoleScreenBufferInfo(CONOUT$) ok={ok2}")
if ok2:
    w = info2.srWindow
    print(f"  srWindow: Left={w.Left} Top={w.Top} Right={w.Right} Bottom={w.Bottom}")
    print(f"  vw={w.Right - w.Left + 1}  viewport rows={w.Bottom - w.Top + 1}")
else:
    err = kernel32.GetLastError()
    print(f"  GetLastError() = {err}")

# --- Try writing one line via WriteConsoleW using GetStdHandle (with proper argtypes) ---
print("\n--- WriteConsoleW test via GetStdHandle(-11) with argtypes ---")
kernel32.GetStdHandle.restype  = ctypes.c_void_p
kernel32.GetStdHandle.argtypes = [ctypes.c_long]
kernel32.GetConsoleScreenBufferInfo.restype  = ctypes.c_bool
kernel32.GetConsoleScreenBufferInfo.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
kernel32.SetConsoleCursorPosition.restype  = ctypes.c_bool
kernel32.SetConsoleCursorPosition.argtypes = [ctypes.c_void_p, _COORD]
kernel32.WriteConsoleW.restype  = ctypes.c_bool
kernel32.WriteConsoleW.argtypes = [
    ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_ulong,
    ctypes.POINTER(ctypes.c_ulong), ctypes.c_void_p,
]

h2 = kernel32.GetStdHandle(-11)
print(f"GetStdHandle(-11) with restype=c_void_p → {h2!r}")
info3 = _CSBI()
ok5 = kernel32.GetConsoleScreenBufferInfo(h2, ctypes.byref(info3))
print(f"GetConsoleScreenBufferInfo ok={ok5}")
if ok5:
    w = info3.srWindow
    vt = w.Top
    vb = w.Bottom
    vw = w.Right - w.Left + 1
    print(f"  vt={vt} vb={vb} vw={vw}")
    ok6 = kernel32.SetConsoleCursorPosition(h2, _COORD(0, vt))
    print(f"SetConsoleCursorPosition(0, {vt}) ok={ok6}")
    msg = "*** GetStdHandle WRITE TEST — if you see this on row 0, Win32 API works! ***"
    written = ctypes.c_ulong(0)
    ok7 = kernel32.WriteConsoleW(h2, msg, len(msg), ctypes.byref(written), None)
    print(f"WriteConsoleW ok={ok7}  written={written.value}")
