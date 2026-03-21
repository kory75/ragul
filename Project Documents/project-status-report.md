# Ragul Project — Status Report
**Date:** 2026-03-21 (updated — v0.3.x in progress)

---

## Overview

Two planning documents exist in this folder:

- **`ragul-spec.md`** — the full language specification (v1.0, WIP)
- **`ragul-toolchain-plan.md`** — an 8-phase build plan plus a Claude agent architecture (orchestrator + 7 specialist agents)

This report compares what those documents specify against what is currently implemented in the repository.

---

## Phase-by-Phase Status

| Phase | Description | Status |
|---|---|---|
| **0 — Scaffold** | `model.py`, `errors.py`, `config.py`, `pyproject.toml`, tests folder | **Done** |
| **1 — Lexer** | `lexer.py`, token types, alias normalisation at lex time | **Done** |
| **2 — Parser** | `parser.py`, two-pass → Scope tree, `-hanem`/`-hibára` siblings, list literals | **Done** |
| **3 — Type Checker** | `typechecker.py`, E001/E003/E004/E005/E006/E007/E009/W001, TypeEnv, harmony | **Done** |
| **4 — Interpreter** | `interpreter.py`, tree-walker, loops, conditionals, error propagation, user-defined scopes | **Done** |
| **5 — CLI** | `ragul/main.py` — `futtat`, `ellenőriz`, `fordít` (stub), `repl`, `lsp` | **Done** |
| **6 — REPL** | `repl/repl.py` — persistent env, `:kilep`/`:töröl`/`:mutat`/`:help` | **Done** |
| **7 — LSP** | `lsp/` — pygls server, diagnostics, hover, completion, go-to-definition | **Done (basic)** |
| **8 — Docs** | `docs/` folder, MkDocs site, GitHub Pages deployment | **Done** |

---

## Release History

| Version | Date | Highlights |
|---|---|---|
| v0.1.0 | 2026-03-15 | First public release — core toolchain, interpreter, CLI, REPL, LSP, CI/CD |
| v0.1.1 | 2026-03-15 | `ragul new project/module` scaffold commands; pygls 2.0 fix |
| **v0.2.0** | **2026-03-16** | E006/E007 type checker errors; bilingual error messages; English I/O aliases; `adatok` module (JSON/CSV); `true`/`false` root aliases; `netin`/`netout` stubs; lexer arithmetic fix; error-code example files; docs overhaul |
| **v0.2.1** | **2026-03-16** | `-val` binding resolution; fold-as-suffix call; 8 new `-val` tests; `-with`/`-val` example files + docs page |
| **v0.3.0** | **2026-03-16** | `minta` module — 5 regex suffixes (`-minta`, `-egyezés`, `-egyezések`, `-mintacsere`, `-mintafeloszt`); 5 English aliases; 16 new tests; bilingual example files |
| **v0.3.x** | **2026-03-17** | `képernyő` module (5 terminal suffixes); `idő` module (`-vár`); lista `-beállít`/`-ismét`/`-index`; szöveg `-karakterek`; 11 aliases; character-mode Téglatörő/Brickbash game (HU+EN); architecture doc |

All versions published to PyPI as `ragul-lang`.

### v0.2.1 highlights

| Change | Details |
|---|---|
| `anthropic` made optional | Moved from `dependencies` to `[ai]` extra — `pip install ragul-lang[ai]`. Plain install no longer pulls in the Anthropic SDK. |
| Orchestrator `thinking` param fixed | Removed invalid `thinking={"type": "adaptive"}` from Claude API call — would have caused silent API failures. |
| AI feature documentation | README, `docs/index.md`, and `docs/tooling.md` updated with info boxes explaining what the feature does, that it is opt-in, what an API key is, and that Ragul never stores or logs it. |
| `-val` binding resolution | `_resolve_val_args` in `parser.py` now absorbs `-val`/`-vel` case words into the preceding word's `val_args` at parse time (was a no-op stub). |
| Fold-as-suffix fixed | `_eval_word` now detects when a user scope has `loop_kind == "gyűjt"` and pulls the initial accumulator from the val_arg queue; `_exec_fold_call` added. |
| Fold scopes callable | `_collect_scopes` now registers `-gyűjt` scopes in `_user_scopes` (previously excluded as loops). |
| Fold scope header order | Correct order is `name-unk-gyűjt` (possession before modifier); `name-gyűjt-unk` emits E002. |
| Example files | `examples/hu/11_val_argumentumok.ragul` and `examples/en/11_with_arguments.ragul` — four patterns: arithmetic, string ops, user scope, fold. |
| Docs page | `docs/examples/11_with_arguments.md` added to MkDocs nav. |

---

## v0.1.0 Milestone Checklist

- [x] `Word` dataclass with full suffix layer model
- [x] All suffix aliases resolve to canonical forms
- [x] Parser handles flat sentences + 2-level nesting
- [x] Type checker catches E001, E004, E005
- [x] Interpreter runs: assignment, arithmetic, filter/sort pipeline, effect scope with console output
- [x] `ragul futtat hello.ragul` works end-to-end
- [x] `ragul ellenőriz` reports structured errors with line numbers
- [x] CI green on push (`.github/workflows/ci.yml` + `docs.yml` present)
- [x] GitHub Pages deployed (`docs/` + `mkdocs.yml` created)

---

## What Is Implemented

### Core Language Toolchain

**Model (`ragul/model.py`)**
`Word`, `Sentence`, `Scope`, and `RagulType` dataclasses are fully implemented. The alias normalisation table covers all English/symbolic aliases → canonical Hungarian suffix forms. `RagulType` supports parameterised types (`Lista-Szám`, `vagy-Szöveg-vagy-Hiba`). `RagulType.display()` produces bilingual type names (e.g. `Number (Szám)`). `suffix_display()` produces bilingual suffix names (e.g. `-felett (-above)`). `_CANONICAL_TO_EN` reverse alias lookup.

**Lexer (`ragul/lexer.py`)**
Hand-written lexer. Produces all planned token types. Alias normalisation applied at lex time. Fixed arithmetic bug: `re.findall` with priority pattern replaces `re.split` so numeric inline args (e.g. `-add-2`) do not absorb the preceding letter suffix.

**Parser (`ragul/parser.py`)**
Two-pass parser building the full `Scope` tree. Handles free word order, nested scopes at arbitrary depth, `-ha`/`-hanem` conditionals, `-hibára` error handler siblings, `-míg`/`-ig`/`-mindegyik`/`-gyűjt` loop scopes, and list literals `[...]`.

**Type Checker (`ragul/typechecker.py`)**
Implements `TypeEnv` (lexically scoped type bindings), root type inference, and the two-level enforcement from the spec. Automatically populates `source_line` context in diagnostics. Active error/warning codes:
- E001 — root guard failure (wrong type for suffix)
- E003 — parallel write conflict (pure scopes)
- E004 — effectful suffix called from pure scope; uses bilingual scope display name
- E005 — unhandled `vagy` (fallible) type; fires correctly for `-tonum` and all module-registered fallible suffixes (module import fixed in v0.2.0)
- E006 — scope leak (root referenced outside its defining scope)
- E007 — module not found (unresolvable `-from`/`-ból` import)
- E009 — field mutation outside `-hatás` (check wired, syntax not yet in parser — v0.3.0)
- W001 — harmony warning (type crossing without bridge)

**Interpreter (`ragul/interpreter.py`)**
Tree-walking interpreter with full support for:
- Assignment and arithmetic pipelines
- All loop kinds: `-míg` (while), `-ig` (until), `-mindegyik` (for-each), `-gyűjt` (fold)
- Conditionals: `-ha` + `-hanem` (else)
- Error propagation via `-va-e` and `-hibára` handler blocks
- Effect channels: `képernyőre`/`stdout`, `stderr`, `bemenetről`/`stdin`
- File I/O channels: `fájlolvasó`/`filein`, `fájlba`/`fileout`
- Network stubs: `netin`, `netout`
- User-defined scope calls as suffix functions
- `-megszakít` break signal
- **Interleaved loop bodies** — `_loop_body()` helper sorts body sentences and child scopes by source line so conditionals inside loops fire in written order (not all sentences then all scopes)
- **Per-iteration foreach write-back** — outer-scope accumulators updated after each element so subsequent iterations see the updated value

**CLI (`ragul/main.py`)**
All five subcommands wired up. Hungarian command names are primary; English aliases accepted silently. UTF-8 stdout/stderr reconfiguration at startup; `rich` legacy Windows renderer disabled to prevent Unicode crashes on non-ASCII diagnostic characters.

**REPL (`ragul/repl/repl.py`)**
Interactive REPL with persistent environment across sentences. Multi-line scope entry via continuation prompt (`...`). Special commands: `:kilep`/`:exit`, `:töröl`/`:clear`, `:mutat`/`:show`, `:help`/`:súgó`.

**LSP (`ragul/lsp/`)**
pygls-based LSP server with:
- Diagnostics on `didOpen`, `didChange`, `didSave`
- Hover (inferred type of token under cursor)
- Completion (valid suffixes triggered on `-`)
- Go-to-definition (jumps to the `-unk` scope that defines a suffix)

**Standard Library**
- `stdlib/core.py` — arithmetic, comparison, equality, logical, string concat
- `stdlib/modules.py` — matematika (9 functions), szöveg (11 functions incl. `-karakterek`), lista (polymorphic filter/compare/fold/set/repeat), adatok (`-json`/`-jsonná`/`-csv`/`-csvné`/`-mezők`), minta (5 regex suffixes)
- `stdlib/screen.py` — `képernyő` module: `-töröl`/`-clear`, `-nyomtat`/`-write`, `-kurzor`/`-cursor`, `-billentyű`/`-key`, `-rajzol`/`-render`; alternate screen buffer management (`\033[?1049h`/`l`) via `atexit`
- `stdlib/time.py` — `idő` module: `-vár`/`-sleep`

**Tests (`ragul/tests/test_ragul.py`)**
123 tests covering: lexer, parser, interpreter, stdlib, type checker (including E006/E007), error handling, `-val` argument binding (`TestValArgs`), regex/minta module (`TestMinta`), screen/time modules (`TestScreen`, `TestIdő`), list/string extensions (`TestListExtensions`, `TestSzövegExtensions`), game smoke (`TestBreakoutSmoke`), and loop-interleave correctness (`TestLoopInterleave`).

**Error-Code Example Files (`examples/error-codes/`)**
8 standalone `.ragul` files, one per diagnostic, each verified to produce the expected `ragul check` output:
- `E001_root_guard.ragul` — wrong type for suffix
- `E003_parallel_write.ragul` — parallel write in pure scope
- `E004_effect_pure_scope.ragul` — effect suffix outside `-hatás`
- `E005_unhandled_fallible.ragul` — `vagy` result without error handling
- `E006_scope_leak.ragul` — root referenced outside its defining scope
- `E007_module_not_found.ragul` — unresolvable `-from` import
- `E009_field_mutation.ragul` — documents planned v0.3.0 behaviour
- `W001_harmony.ragul` — type boundary crossed without bridge

**Documentation (`docs/`)**
Full MkDocs Material site deployed to GitHub Pages. Includes:
- Language reference (syntax, types, functions, control, effects, errors, modules)
- Standard library reference
- Tooling & CLI guide (all commands, error codes, editor integration)
- `error-codes.md` — one-page summary with code sample, expected output, and fix for every error code
- Glossary (Hungarian ↔ English suffix/keyword map)
- 12 bilingual example pages (English alias / Hungarian tabs), including `-with`/`-val` arguments, regex patterns, and terminal/game features (képernyő, idő, framebuffer grid)

**Agent Architecture (`ragul/agents/`)**
- `task.py`, `base.py`, `orchestrator.py` — pipeline with optional Claude Opus 4.6 AI analysis
- 7 specialist agents: `lexer_agent.py`, `parser_agent.py`, `typecheck_agent.py`, `interpreter_agent.py`, `repl_agent.py`, `lsp_agent.py`, `docs_agent.py`

**GitHub Actions (`/.github/workflows/`)**
- `ci.yml` — pytest + mypy on every push/PR
- `docs.yml` — MkDocs deploy to GitHub Pages on merge to main
- PyPI publish workflow triggered on GitHub Release (publishes `ragul-lang` to PyPI)

---

## What Is Missing / Known Issues

| Issue | Location | Impact |
|---|---|---|
| Dependency graph / topological sort not implemented | `interpreter.py` | Sentences execute in written order, not DAG order; the spec's implicit parallelism is not enforced |
| E009 trigger unreachable | `typechecker.py` | Field mutation check exists but `word.possession == "-ja"` can never be True with current parser — needs OOP syntax (v0.3.0) |

### Implemented Differently from the Plan

| Plan | Reality |
|---|---|
| Entry point at `cli/main.py` | Lives at `ragul/main.py` (entry point `ragul.main:main`) |
| `agents/` at repo root | Lives at `ragul/agents/` |
| Separate `stdlib/matematika.py`, `stdlib/szoveg.py`, `stdlib/lista.py` | All merged into `stdlib/modules.py` |
| Tests at top-level `tests/` | Tests at `ragul/tests/` |

---

## Bug Fixes Log

### v0.3.x (2026-03-17)

| Bug | Fix |
|---|---|
| `-mindegyik` foreach write-back only ran after the full loop from the last `loop_env` | Write-back moved inside the iteration loop so outer-scope accumulators (e.g. `rács` during level loading) are updated after every element and subsequent iterations see the current value |
| `run()` double-executed all top-level loops and conditionals | Removed the outer `for child in root_scope.children` loop in `run()`; `_exec_scope(root_scope)` already processes all children via `_interleave` |
| Pure/function scope branch silently skipped `is_effect` children | Extended the dispatch condition from `is_conditional or is_loop` to `is_effect or is_conditional or is_loop`; top-level effect scopes (e.g. `program-nk-hatás`) are now handled by `_exec_scope` rather than the now-removed outer loop |
| `-rajzol` drew to the scroll-back buffer, not the visible viewport | `_rajzol` now enters the **alternate screen buffer** (`\033[?1049h`) on first call; `\033[H` in the alt-screen always addresses the visible top-left; `atexit` restores the normal screen; `-töröl` exits the alt-screen back to the normal terminal |
| `-töröl` used `os.system("cls")` (subprocess, unreliable in PowerShell) | Replaced with `\033[2J\033[H` ANSI sequence throughout; in game context, `-töröl` now exits the alternate screen which implicitly restores the previous terminal content |

### v0.2.1 (2026-03-16)

| Bug | Fix |
|---|---|
| `-val`/`-vel` words not absorbed into preceding word at parse time | `_resolve_val_args` in `parser.py` implemented (was a no-op stub); absorbs instrument-case words into `val_args` left-to-right |
| Fold scopes not callable as suffixes | `_collect_scopes` guard narrowed: only non-fold loops are excluded from `_user_scopes`; fold scopes are now registered |
| Fold initial accumulator hard-coded to 0 | `_exec_fold_call` added to interpreter; initial value consumed from val_arg queue (first `-val` argument) |
| `_fileout` mypy error | Return type changed from `-> None` to `-> Any`; explicit `return None` on success path added |

### v0.2.0 (2026-03-16)

| Bug | Fix |
|---|---|
| `-tonum` (and all module suffixes) not type-checked | Added `import ragul.stdlib.modules` to `typechecker.py` — module suffixes now registered in `SUFFIX_REGISTRY` at check time; E005 fires correctly |
| E006 false positive on valid programs | `_check_sentence` now treats `case=""` as a source word so a root used in an action-only sentence is properly recorded in `local_env` |
| Rich Unicode crash on Windows | `sys.stdout.reconfigure(encoding='utf-8')` at startup; `Console(legacy_windows=False)`; `_markup_escape()` on diagnostic output |
| `ValueError: mutable default dict` in `RagulType` | Moved `_EN_NAMES` dict to module level as `_TYPE_EN_NAMES` |
| Double-quote in E006 messages (`''name''`) | `_scope_display_name()` returns `"scope 'name'"` directly; message templates no longer add their own quotes |
| Lexer arithmetic bug (`x-3-add-2-mul` → 30 instead of 26) | Replaced `re.split` with `re.findall` using priority pattern: double-dash negative → letter suffix → digit literal |

### v0.1.x (2026-03-14–15)

| Bug | Fix |
|---|---|
| Conditionals inside `-hatás` execute unconditionally | Added `_interleave()` to sort sentences and child scopes by line; fixed `current_line` reset in parser |
| Custom scope calls return input unchanged | Fixed user-scope lookup to use `bare` name (no leading dash) |
| `-mindegyik` crashes on empty list | Initialised `loop_env` before the loop body |
| `"42"` string literal coerced to int | Parser re-adds quotes around STRING token values |

---

## Recommended Next Steps

### v0.3.0 — Released

- [x] `minta` module — regex pattern matching (`-minta`, `-egyezés`, `-egyezések`, `-mintacsere`, `-mintafeloszt`)

### v0.3.x — In Progress

- [x] `képernyő` module — 5 terminal I/O suffixes (`-töröl`, `-nyomtat`, `-kurzor`, `-billentyű`, `-rajzol`) with EN aliases
- [x] `idő` module — `-vár` / `-sleep` timing suffix
- [x] lista extensions — `-beállít` (set-at-index) and `-ismét` (repeat-value)
- [x] szöveg extension — `-karakterek` / `-chars` (split string to char list)
- [x] 9 new English aliases added to `ALIAS_TABLE`
- [x] lista `-index` (element-at-index; works on strings too)
- [x] Character-mode Téglatörő/Brickbash — `examples/games/téglatörő.ragul` (HU) + `examples/games/en/brickbash.ragul` (EN) + `level1.txt`
- [x] Architecture documentation — `Project Documents/ragul-game-architecture.md`
- [x] Fix typo: `pozitív-e-nk-ha` / `pozitív-e-ours-if` in `docs/control.md` and `ragul-spec.md` — stray `-e` (error-propagation suffix) removed from scope name; correct form is `pozitív-nk-ha` / `pozitív-ours-if`
- [x] Fix typo: `-szöteggé` → `-szöveggé` throughout — renamed in `stdlib/modules.py`, `model.py`, `typechecker.py`, `errors.py`, `docs/stdlib.md`, `docs/glossary.md`, `docs/types.md`, `ragul-spec.md`, and example files
- [ ] `dátum` module — date/time operations
- [ ] OOP / record-update syntax for E009 to become triggerable
- [ ] `ragul formáz` formatter command (auto-indent, canonical suffix casing)
- [ ] Split `stdlib/modules.py` into separate per-module files (`stdlib/matematika.py`, `stdlib/szoveg.py`, `stdlib/lista.py`, `stdlib/minta.py`, etc.) — easier to maintain and extend
- [ ] English aliases for module names — add entries to `ROOT_ALIASES` in `model.py` so `pattern-from.` works as an alias for `minta-ból.`, `math-from.` for `matematika-ból.`, etc.

---

*End of report.*
