"""
tools/run_headless.py — Run a Ragul game headlessly via the pyte VT100 emulator.

Every frame rendered by -rajzol is captured as plain text so Claude can inspect
exactly what would appear on the player's screen without needing a real terminal.

Usage
-----
    python tools/run_headless.py [options]

Options
-------
    --game   FILE    path to .ragul file  (default: examples/games/breakout.ragul)
    --frames N       frames to capture before auto-quitting  (default: 20)
    --keys   STR     comma-separated per-frame key inputs, e.g. ",,d,d,,a,,"
                     (empty string = no key that frame; trailing frames get '')
    --cols   N       virtual terminal width   (default: 80)
    --rows   N       virtual terminal height  (default: 30)
    --out    FILE    output file  (default: tools/game_frames.txt)

Example
-------
    # 30 silent frames, then move paddle right 5 times
    python tools/run_headless.py --frames 35 --keys ",,,,,,,,,,d,d,d,d,d"

Output
------
    tools/game_frames.txt — numbered frames, each showing the pyte-rendered screen.
    Claude can Read this file to see exactly what the game looks like.
"""

from __future__ import annotations
import argparse
import os
import sys

# Ensure the repo root is on the path so 'ragul' is importable from any CWD.
_repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import pyte


# ---------------------------------------------------------------------------
# pyte virtual screen
# ---------------------------------------------------------------------------

def _make_screen(cols: int, rows: int) -> tuple[pyte.Screen, pyte.ByteStream]:
    screen = pyte.Screen(cols, rows)
    stream = pyte.ByteStream(screen)
    return screen, stream


def _snapshot(screen: pyte.Screen) -> str:
    """Return the current screen content as a plain-text string."""
    lines = []
    for row in range(screen.lines):
        line = "".join(
            screen.buffer[row][col].data for col in range(screen.columns)
        ).rstrip()
        lines.append(line)
    # Drop trailing blank lines
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Headless runner
# ---------------------------------------------------------------------------

def run(
    game_path: str,
    max_frames: int,
    keys: list[str],
    cols: int,
    rows: int,
) -> list[str]:
    """
    Run the game and return a list of captured frame strings (one per -rajzol call).
    """
    screen, stream = _make_screen(cols, rows)

    captured_frames: list[str] = []
    frame_idx: list[int] = [0]

    # ------------------------------------------------------------------
    # stdout proxy — everything the game writes to sys.stdout goes here.
    # This captures -nyomtat (score), -kurzor, and any other raw writes.
    # ------------------------------------------------------------------
    class PyteWriter:
        def write(self, text: str) -> int:
            stream.feed(text.encode("utf-8", errors="replace"))
            return len(text)

        def flush(self) -> None:
            pass

        # Some code checks sys.stdout.fileno(); raise the right error.
        def fileno(self) -> int:
            raise OSError("pyte writer has no fileno")

    old_stdout = sys.stdout
    sys.stdout = PyteWriter()  # type: ignore[assignment]

    try:
        # Import here so suffix registration happens after stdout is patched
        # (some modules print warnings on import — those go to pyte, harmlessly).
        from ragul.stdlib.core import SUFFIX_REGISTRY
        import ragul.stdlib.modules  # noqa: F401 — registers all suffixes

        # ------------------------------------------------------------------
        # Patch -vár: no sleeping
        # ------------------------------------------------------------------
        SUFFIX_REGISTRY["-vár"]["fn"] = lambda v, ms: v

        # ------------------------------------------------------------------
        # Patch -töröl: feed an ANSI clear to pyte instead of touching the
        # real terminal or toggling the alternate-screen flag.
        # ------------------------------------------------------------------
        def _mock_töröl(v):
            stream.feed(b"\033[2J\033[H")
            return v

        SUFFIX_REGISTRY["-töröl"]["fn"] = _mock_töröl

        # ------------------------------------------------------------------
        # Patch -billentyű: return keys[frame] while frames remain,
        # then 'q' to quit so the game exits cleanly.
        # ------------------------------------------------------------------
        def _mock_billentyű(v):
            idx = frame_idx[0]
            if idx >= max_frames:
                return "q"
            if idx < len(keys):
                return keys[idx]
            return ""

        SUFFIX_REGISTRY["-billentyű"]["fn"] = _mock_billentyű

        # ------------------------------------------------------------------
        # Patch -rajzol: write grid to pyte (bypassing alternate-screen
        # switching) then snapshot the virtual screen.
        # ------------------------------------------------------------------
        def _mock_rajzol(v):
            # Build the same byte sequence the real renderer would emit,
            # but without the \033[?1049h alternate-screen switch.
            # Use \r\n so pyte resets to column 0 after each row (pyte does
            # not enable LNM by default, so bare \n only moves the cursor down).
            parts = ["\033[H\033[2J\033[H"]
            if isinstance(v, list):
                for row_data in v:
                    if isinstance(row_data, list):
                        parts.append("".join(str(c) for c in row_data) + "\r\n")
                    else:
                        parts.append(str(row_data) + "\r\n")
            stream.feed("".join(parts).encode("utf-8"))
            captured_frames.append(_snapshot(screen))
            frame_idx[0] += 1
            return v

        SUFFIX_REGISTRY["-rajzol"]["fn"] = _mock_rajzol

        # ------------------------------------------------------------------
        # Parse and run the game
        # ------------------------------------------------------------------
        from ragul.lexer import Lexer
        from ragul.parser import Parser
        from ragul.interpreter import Interpreter

        code = open(game_path, encoding="utf-8").read()
        tokens = Lexer(code, game_path).tokenise()
        scope = Parser(tokens, game_path).parse()
        interp = Interpreter(scope, game_path)
        interp.run()

    finally:
        sys.stdout = old_stdout

    return captured_frames


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run a Ragul game headlessly and capture frames via pyte."
    )
    ap.add_argument(
        "--game",
        default="examples/games/breakout.ragul",
        help="path to the .ragul game file",
    )
    ap.add_argument(
        "--frames",
        type=int,
        default=20,
        help="number of frames to capture before auto-quitting",
    )
    ap.add_argument(
        "--keys",
        default="",
        help='comma-separated per-frame key inputs, e.g. ",,d,d,,a"',
    )
    ap.add_argument(
        "--cols",
        type=int,
        default=80,
        help="virtual terminal width (default 80)",
    )
    ap.add_argument(
        "--rows",
        type=int,
        default=30,
        help="virtual terminal height (default 30)",
    )
    ap.add_argument(
        "--out",
        default="tools/game_frames.txt",
        help="output file path",
    )
    args = ap.parse_args()

    keys = args.keys.split(",") if args.keys else []

    os.chdir(_repo_root)  # run from repo root so relative file paths work

    print(f"Game   : {args.game}")
    print(f"Frames : {args.frames}")
    print(f"Keys   : {keys or '(none)'}")
    print(f"Output : {args.out}")
    print()

    frames = run(args.game, args.frames, keys, args.cols, args.rows)

    os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        for i, frame in enumerate(frames):
            f.write(f"{'=' * 40}\n")
            f.write(f"Frame {i + 1:3d}\n")
            f.write(f"{'=' * 40}\n")
            f.write(frame)
            f.write("\n\n")

    print(f"Captured {len(frames)} frame(s) -> {args.out}")


if __name__ == "__main__":
    main()
