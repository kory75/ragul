# Ragul Game Architecture — Character-mode Téglatörő / Brickbash

**Date:** 2026-03-17 (updated)
**Version:** v0.3.x (in progress)

---

## Overview

The first tradition program in any new language is a character-mode Téglatörő / Brickbash. For Ragul, this serves two purposes:

1. **Showcase** — demonstrates that Ragul can express real, stateful, interactive programs.
2. **Stress test** — exercises loops, conditionals, list mutation, file I/O, terminal I/O, and timing in a single program.

Three new stdlib modules were designed and added. All additions are general-purpose language primitives — nothing game-specific belongs in the stdlib.

---

## New Modules

### `képernyő` — Terminal I/O (`ragul/stdlib/screen.py`)

Five suffixes for terminal interaction:

| Suffix (HU)    | Alias (EN)  | Args       | Effect |
|---|---|---|---|
| `-töröl`       | `-clear`    | —          | Exit the alternate screen buffer (restoring the normal terminal); or `\033[2J\033[H` if not in alt-screen |
| `-nyomtat`     | `-write`    | —          | `sys.stdout.write(str(v))` — no newline |
| `-kurzor`      | `-cursor`   | row, col   | ANSI cursor-move escape `\033[row;colH` |
| `-billentyű`   | `-key`      | —          | Non-blocking keypress; `''` if none pressed |
| `-rajzol`      | `-render`   | —          | Enter alternate screen buffer (first call), then render `List[List[str]]` framebuffer |

All suffixes are pass-through: they return their input value unchanged so they can appear anywhere in a pipeline without disrupting the data flow.

**Platform notes:**
- Windows: VT processing enabled at import via `SetConsoleMode`; `msvcrt.kbhit()` + `msvcrt.getwch()` for non-blocking key reads; arrow keys decoded from two-byte sequences (`\x00`/`\xe0` + scan code).
- Unix: `tty` + `termios` raw mode entered and restored in `finally` on every `-billentyű` call; `select(timeout=0)` for non-blocking reads; ESC sequences decoded for arrow keys.

**`-rajzol` design:**
```python
def _rajzol(grid):
    _enter_alt_screen()          # first call: \033[?1049h  (no-op thereafter)
    sys.stdout.write("\033[H\033[J")  # cursor home + clear to end of screen
    for row in grid:
        sys.stdout.write("".join(str(c) for c in row) + "\n")
    sys.stdout.flush()
    return grid
```
The framebuffer is a `List[List[str]]` — a 2D grid of single characters. This is the idiomatic Ragul representation because each cell can be individually updated with `-beállít` without replacing the entire row string.

**Alternate screen buffer (`\033[?1049h` / `\033[?1049l`):**
The normal terminal has a scroll-back buffer. `\033[H` (cursor home) addresses the *top of that buffer*, not the top of the visible viewport. After even a few lines of prior output the grid renders above the visible area — the user sees only the score line scrolling at the bottom. The alternate screen has no scroll-back; `\033[H` always hits the visible top-left. `-rajzol` enters the alternate screen on its first call and registers an `atexit` handler so the normal screen is always restored when the interpreter exits. `-töröl` explicitly exits the alternate screen so the game-over message appears in the normal shell history.

---

### `idő` — Timing (`ragul/stdlib/time.py`)

One suffix:

| Suffix (HU) | Alias (EN) | Args | Effect |
|---|---|---|---|
| `-vár`      | `-sleep`   | ms   | `time.sleep(float(ms) / 1000)` |

Separated into its own module (not merged into `képernyő`) because timing is conceptually independent of terminal rendering and useful in non-terminal programs (e.g. network polling, scheduled tasks).

---

### Lista and Szöveg Extensions (`ragul/stdlib/modules.py`)

Four new suffixes added to existing modules:

| Module  | Suffix (HU)   | Alias (EN)  | Semantics |
|---|---|---|---|
| `lista` | `-beállít`    | `-set`      | Return new list with element at index replaced (non-mutating) |
| `lista` | `-ismét`      | `-repeat`   | Return list of N copies of a value |
| `szöveg`| `-karakterek` | `-chars`    | Split string into list of single characters |

**`-beállít` is non-mutating** — it returns a new list. This is essential for Ragul's functional-by-default model. The game loop replaces the entire row reference in `rács` rather than mutating in place:

```ragul
sor_lista-ba   sor_lista-beállít-t  lc-val  " "-val.
rács-ba        rács-beállít-t  gr_sor-val  sor_lista-val.
```

**`-karakterek`** bridges the gap between file I/O (which delivers strings) and the framebuffer model (which requires `List[str]` rows). Level loading in `téglatörő.ragul / brickbash.ragul`:

```ragul
sorok-ba     szoveg-feloszt-t  "\n"-val.   // List[str]
// then per-row:
betuk-ba     sor-karakterek-t.             // List[str] → List[List[str]]
```

---

## Grid / Framebuffer Model

The game grid is a `List[List[str]]` — 17 rows × 22 columns. Each cell is a single string character.

Updating a cell requires two `-beállít` operations (because lists are not mutable in Ragul):

1. Get the row list from the grid.
2. Replace the target column: `sor-beállít-t  col-val  char-val.`
3. Replace the row in the grid: `rács-beállít-t  row-val  sor-val.`

This is verbose but explicit and safe. The pattern repeats throughout the frame-building section of the game loop.

---

## Level Loading from File

Level data lives in a plain text file (`examples/games/level1.txt`). The file is the initial grid — no code constructs it:

```
+--------------------+
|[][][][][][][][]    |
...
+--------------------+
```

Loading sequence:

```ragul
szoveg-ba    "examples/games/level1.txt"-fájlból-t.  // read whole file
sorok-ba     szoveg-feloszt-t  "\n"-val.              // split to lines
// build rács: each line → List[str] via -karakterek
rács-ba      []-t.
sorok-mindegyik-unk
    sor-d.
    betuk-ba  sor-karakterek-t.
    rács-ba   rács-betuk-hozzáad-t.
```

This pattern generalises to any structured text format where each line maps to a row.

---

## Interpreter Bugs Found and Fixed During Development

The Téglatörő / Brickbash game served as the stress test that exposed three interpreter bugs.

### 1. Foreach write-back: accumulator pattern broken

**Problem:** `-mindegyik` (for-each) write-back to the outer environment only ran *after the entire loop* from the last `loop_env`. For accumulator patterns — a list variable in the outer scope that each iteration appends to — every iteration read the *original* empty value from the outer env (because `loop_env.get()` traverses the parent chain, but the outer env was never updated mid-loop). The final write-back copied only the last iteration's single-element list.

This directly caused the level-loading loop (`sorok-unk-mindegyik`) to build a `rács` grid with only the final row instead of all 17 rows.

**Fix:** Write-back moved inside the iteration loop (executed after every element). Outer-scope variables now reflect each iteration's mutations before the next element runs.

### 2. Double-execution of top-level loops and conditionals

**Problem:** `run()` called `_exec_scope(root_scope)` and then iterated `root_scope.children` again, re-executing every top-level loop and conditional scope a second time. The pure/function scope branch in `_exec_scope` already processed children via `_interleave`, but then `run()` ran them again. Effect scopes (`-hatás`) were only run by the outer loop (the pure branch silently skipped them), so effects ran once while loops/conditionals ran twice.

**Fix:** Removed the outer loop from `run()`. The pure/function scope branch now also dispatches `is_effect` children so `_exec_scope(root_scope)` handles everything in one pass.

### 3. Conditionals inside loops fired out of order (discovered earlier, fixed in same session)

**Problem:** `_exec_while` / `_exec_until` / `_exec_foreach` ran all body *sentences* first, then all child *scopes* (the `-ha` conditionals). A conditional that depended on a sentence computed later in the body would always read the *previous* iteration's value.

**Fix:** `_loop_body()` helper (parallel to `_interleave`) sorts body sentences and child scopes together by source line number. The loop body now executes items in written order.

---

## Workarounds Discovered During Implementation

| Problem | Solution |
|---|---|
| Negate velocity | `dy-ba  dy-szoroz-t  -1-val.` — multiply by −1 |
| Integer division | `oszlop-ba  oszlop_raw-padló-t  2-val.` — use `-padló` (floor) with divisor as `-val` arg |
| ~~Index-get from a list~~ | ~~`el-ba  lista-idx-szelet-t  i-val.` then `-első` (no direct index suffix)~~ — **DONE:** `-index` suffix added (e.g. `rács-index-t  3-val.`) |
| Compound AND | Pre-compute each boolean into a named root, then chain with `-és` |
| No in-place mutation | Every cell update requires: get row → `-beállít` → put row back into grid |
| Game state reset on ball loss | Re-assign `sx`, `sy`, `dy` individually — no struct/record update yet |
| Scoreline display | Concatenate score + lives strings with `-összefűz`, then `-nyomtat` |

---

## File Layout

```
ragul/stdlib/screen.py          — képernyő module (5 terminal suffixes)
ragul/stdlib/time.py            — idő module (1 timing suffix)
ragul/stdlib/modules.py         — lista: -beállít, -ismét; szöveg: -karakterek
ragul/model.py                  — 9 new aliases (clear, write, cursor, key, render,
                                  sleep, set, repeat, chars)
examples/games/level1.txt       — level asset (plain text, 17 × 22)
examples/games/téglatörő.ragul / brickbash.ragul   — the game
ragul/tests/test_ragul.py       — TestScreen, TestIdő, TestListExtensions,
                                  TestSzövegExtensions, TestTéglatörő / BrickbashSmoke,
                                  TestLoopInterleave (3 ordering correctness tests)
```

---

*End of document.*
