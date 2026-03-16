# Ragul Project — Status Report
**Date:** 2026-03-16 (updated twice)

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

All three versions published to PyPI as `ragul-lang`.

### Post-v0.2.0 changes (unreleased, on master)

| Change | Details |
|---|---|
| `anthropic` made optional | Moved from `dependencies` to `[ai]` extra — `pip install ragul-lang[ai]`. Plain install no longer pulls in the Anthropic SDK. |
| Orchestrator `thinking` param fixed | Removed invalid `thinking={"type": "adaptive"}` from Claude API call — would have caused silent API failures. |
| AI feature documentation | README, `docs/index.md`, and `docs/tooling.md` updated with info boxes explaining what the feature does, that it is opt-in, what an API key is, and that Ragul never stores or logs it. |

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
- `stdlib/modules.py` — matematika (9 functions), szöveg (10 functions including `-számmá`/`-tonum`), lista (polymorphic filter/compare/fold), adatok (`-json`/`-jsonná`/`-csv`/`-csvné`/`-mezők`)

**Tests (`ragul/tests/test_ragul.py`)**
64 tests covering: lexer, parser, interpreter, stdlib, type checker (including E006/E007), error handling.

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
- 9 bilingual example pages (English alias / Hungarian tabs)

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
| `-val` binding resolution is stubbed | `parser.py` `_resolve_val_args()` | `-val` argument passing between words may not work in all cases |
| Dependency graph / topological sort not implemented | `interpreter.py` | Sentences execute in written order, not DAG order; the spec's implicit parallelism is not enforced |
| E009 trigger unreachable | `typechecker.py` | Field mutation check exists but `word.possession == "-ja"` can never be True with current parser — needs OOP syntax (v0.3.0) |
| `anthropic` optional extra | `pyproject.toml` | Install with `pip install ragul-lang[ai]` — resolved, no longer a hidden manual step |

### Implemented Differently from the Plan

| Plan | Reality |
|---|---|
| Entry point at `cli/main.py` | Lives at `ragul/main.py` (entry point `ragul.main:main`) |
| `agents/` at repo root | Lives at `ragul/agents/` |
| Separate `stdlib/matematika.py`, `stdlib/szoveg.py`, `stdlib/lista.py` | All merged into `stdlib/modules.py` |
| Tests at top-level `tests/` | Tests at `ragul/tests/` |

---

## Bug Fixes Log

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

### v0.3.0 — Planned

- [ ] `minta` module — regex pattern matching (`-minta`, `-egyezés`, `-csere-minta`)
- [ ] `dátum` module — date/time operations
- [ ] OOP / record-update syntax for E009 to become triggerable
- [ ] `-val` binding resolution (currently stubbed in `parser.py`)
- [ ] `ragul formáz` formatter command (auto-indent, canonical suffix casing)
- [ ] Add `anthropic` as optional dependency in `pyproject.toml` (`pip install ragul-lang[ai]`)

---

*End of report.*
