# Ragul Project — Status Report
**Date:** 2026-03-15 (updated)

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
| **3 — Type Checker** | `typechecker.py`, E001/E003/E004/E005/E009/W001, TypeEnv, harmony | **Done** |
| **4 — Interpreter** | `interpreter.py`, tree-walker, loops, conditionals, error propagation, user-defined scopes | **Done** |
| **5 — CLI** | `ragul/main.py` — `futtat`, `ellenőriz`, `fordít` (stub), `repl`, `lsp` | **Done** |
| **6 — REPL** | `repl/repl.py` — persistent env, `:kilep`/`:töröl`/`:mutat`/`:help` | **Done** |
| **7 — LSP** | `lsp/` — pygls server, diagnostics, hover, completion, go-to-definition | **Done (basic)** |
| **8 — Docs** | `docs/` folder, MkDocs site, GitHub Pages deployment | **Done (initial)** |

---

## v0.1.0 Milestone Checklist

From the build plan's "First Milestone Checklist":

- [x] `Word` dataclass with full suffix layer model
- [x] All suffix aliases resolve to canonical forms
- [x] Parser handles flat sentences + 2-level nesting
- [x] Type checker catches E001, E004, E005
- [x] Interpreter runs: assignment, arithmetic, filter/sort pipeline, effect scope with console output
- [x] `ragul futtat hello.ragul` works end-to-end
- [x] `ragul ellenőriz` reports structured errors with line numbers
- [x] CI green on push (`.github/workflows/ci.yml` + `docs.yml` present)
- [x] GitHub Pages deployed (`docs/` + `mkdocs.yml` created; deploys on next merge to main)

---

## What Is Implemented

### Core Language Toolchain

**Model (`ragul/model.py`)**
`Word`, `Sentence`, `Scope`, and `RagulType` dataclasses are fully implemented. The alias normalisation table covers all English/symbolic aliases → canonical Hungarian suffix forms. `RagulType` supports parameterised types (`Lista-Szám`, `vagy-Szöveg-vagy-Hiba`).

**Lexer (`ragul/lexer.py`)**
Hand-written lexer. Produces all planned token types: `WORD`, `SCOPE_OPEN`, `NUMBER`, `STRING`, `LIST_OPEN`/`CLOSE`, `FULLSTOP`, `INDENT`/`DEDENT`, `COMMENT`, `MINUS_HANEM`, `MINUS_HIBARA`, `EOF`. Alias normalisation applied at lex time so the parser only sees canonical forms.

**Parser (`ragul/parser.py`)**
Two-pass parser building the full `Scope` tree. Handles free word order, nested scopes at arbitrary depth, `-ha`/`-hanem` conditionals, `-hibára` error handler siblings, `-míg`/`-ig`/`-mindegyik`/`-gyűjt` loop scopes, and list literals `[...]`.

**Type Checker (`ragul/typechecker.py`)**
Implements `TypeEnv` (lexically scoped type bindings), root type inference, and the two-level enforcement from the spec. Active error/warning codes:
- E001 — root guard failure (wrong type for suffix)
- E003 — parallel write conflict (pure scopes)
- E004 — effectful suffix called from pure scope
- E005 — unhandled `vagy` (fallible) type
- E009 — field mutation outside `-hatás`
- W001 — harmony warning (type crossing without bridge)

**Interpreter (`ragul/interpreter.py`)**
Tree-walking interpreter with full support for:
- Assignment and arithmetic pipelines
- All loop kinds: `-míg` (while), `-ig` (until), `-mindegyik` (for-each), `-gyűjt` (fold)
- Conditionals: `-ha` + `-hanem` (else)
- Error propagation via `-va-e` and `-hibára` handler blocks
- Effect channels: `képernyőre`, `stderr`, `bemenetről`
- User-defined scope calls as suffix functions
- `-megszakít` break signal

**CLI (`ragul/main.py`)**
All five subcommands wired up. Hungarian command names are primary; English aliases (`run`, `check`, `compile`) accepted silently for convenience.

**REPL (`ragul/repl/repl.py`)**
Interactive REPL with persistent environment across sentences. Multi-line scope entry via continuation prompt (`...`). Special commands: `:kilep`/`:exit`, `:töröl`/`:clear`, `:mutat`/`:show`, `:help`/`:súgó`.

**LSP (`ragul/lsp/`)**
pygls-based LSP server with:
- Diagnostics on `didOpen`, `didChange`, `didSave`
- Hover (inferred type of token under cursor)
- Completion (valid suffixes triggered on `-`)
- Go-to-definition (jumps to the `-unk` scope that defines a suffix)

**Standard Library**
- `stdlib/core.py` — arithmetic (`-össze`, `-kivon`, `-szoroz`, `-oszt`, `-maradék`), comparison (`-felett`, `-alatt`, `-legalább`, `-legfeljebb`), equality, logical (`-nem`, `-és`, `-vagy`), string concat (`-összefűz`)
- `stdlib/modules.py` — matematika (`-négyzetgyök`, `-hatvány`, `-abszolút`, `-kerekítve`, `-padló`, `-plafon`, `-log`, `-sin`, `-cos`), szöveg (`-hossz`, `-nagybetűs`, `-kisbetűs`, `-tartalmaz`, `-kezdődik`, `-végződik`, `-feloszt`, `-formáz`, `-szelet`, `-csere`, `-számmá`), lista (`-rendezve`, `-fordítva`, `-első`, `-utolsó`, `-egyedi`, `-lapítva`, `-szűrve`, `-hozzáad`, `-eltávolít`, polymorphic filter/compare)

**Tests (`ragul/tests/test_ragul.py`)**
Comprehensive test suite covering: lexer (9 tests), parser (5 tests), interpreter (16 tests), stdlib (14 tests), type checker (7 tests), error handling (2 tests).

**Fixtures**
- `tests/fixtures/hello.ragul`
- `tests/fixtures/arithmetic.ragul`
- `tests/fixtures/pipeline.ragul`

**Agent Architecture (`ragul/agents/`)**
Full agent layer implemented at `ragul/agents/`:
- `task.py` — `Task` / `TaskResult` typed message protocol
- `base.py` — `BaseAgent` abstract class
- `orchestrator.py` — `OrchestratorAgent`; reads `ragul.config`, builds task pipelines, delegates to specialist agents. On compiler errors/warnings, optionally calls **Claude Opus 4.6** (streaming) to generate a plain-English explanation with fix suggestions (requires `ANTHROPIC_API_KEY`; gracefully skipped if absent)
- `lexer_agent.py`, `parser_agent.py`, `typecheck_agent.py`, `interpreter_agent.py`, `repl_agent.py`, `lsp_agent.py`, `docs_agent.py` — all 7 specialist agents

**GitHub Actions (`/.github/workflows/`)**
- `ci.yml` — runs pytest + mypy on every push/PR; uploads JSON test report as artifact
- `docs.yml` — deploys MkDocs site to GitHub Pages on merge to main

**`ragul.config`**
Project config file at repo root (dogfooding). Hungarian TOML keys: `[projekt]`, `[fordito]`, `[modulok]`, `[ellenorzes]`, `[hibak]`.

---

## What Is Missing

### Entirely Absent

*(All major gaps resolved. See Known Issues below for remaining smaller items.)*

### Implemented Differently from the Plan

| Plan | Reality |
|---|---|
| Entry point at `cli/main.py` | Lives at `ragul/main.py` (entry point `ragul.main:main`) |
| `agents/` at repo root | Lives at `ragul/agents/` |
| Separate `stdlib/matematika.py`, `stdlib/szoveg.py`, `stdlib/lista.py` | All merged into `stdlib/modules.py` |
| Tests at top-level `tests/` | Tests at `ragul/tests/` |

### Known Issues

| Issue | Location | Impact |
|---|---|---|
| `-val` binding resolution is stubbed | `parser.py` `_resolve_val_args()` | `-val` argument passing between words may not work in all cases |
| Dependency graph / topological sort not implemented | `interpreter.py` | Sentences execute in written order, not DAG order; the spec's implicit parallelism is not enforced |
| E006 (scope leak) not enforced | `typechecker.py` | Variables can be referenced outside their defining scope without an error |
| E007 (module resolution) not enforced | `typechecker.py` | Bad module imports produce no diagnostic |
| `anthropic` missing from `pyproject.toml` | `pyproject.toml` | AI analysis in orchestrator requires manual `pip install anthropic` |

### Interpreter Bugs (fixed 2026-03-14)

All 4 interpreter bugs identified during examples authoring have been resolved:

| Bug | Fix | Files Changed |
|---|---|---|
| Conditionals inside `-hatás` execute unconditionally | Added `_interleave()` to execute sentences and child scopes in source order (by line number); fixed parser to reset `current_line = 0` after SCOPE_OPEN so subsequent sentences get their correct line | `interpreter.py`, `parser.py`, `model.py` |
| Custom scope calls return input unchanged | Fixed `_eval_word` user-scope lookup to use `bare` (without leading dash) instead of full `aspect` string | `interpreter.py` |
| `-mindegyik` (for-each) loop crashes | Initialised `loop_env` before the loop body to handle empty iterables | `interpreter.py` |
| `"42"` string literal coerced to int | Parser now re-adds quotes around STRING token values so `_resolve_root` distinguishes `"42"` (str) from `42` (int) | `parser.py` |

Root causes of the conditional bug (two intertwined parser issues):
- `current_line` was set to the SCOPE_OPEN token's line after a child scope, causing subsequent sentences to inherit the wrong line number and sort before the conditional in `_interleave`
- Effect scope body ran all `sentences` before all `children`, violating source sequential order

---

## Recommended Next Steps

### v0.1.1 — Patch + First New Feature

- [x] Publish to PyPI as `ragul-lang` (done 2026-03-15)
- [x] Fix pygls 2.0 compatibility in LSP server (done 2026-03-15)
- [x] **`ragul új projekt <name>` / `ragul new project <name>`** — scaffold a new project folder (`ragul.config`, `main.ragul`, `.gitignore`, `README.md`) (done 2026-03-15)
- [x] **`ragul új modul <name>` / `ragul new module <name>`** — scaffold a new module file inside an existing project (done 2026-03-15)
- [ ] Publish v0.1.1 to PyPI via GitHub Release
- [ ] Create VS Code Marketplace publisher account
- [ ] Publish `ragul-lang` VS Code extension to Marketplace

### v0.2.0 — To Be Planned

*(Candidates: `ragul formáz`, `ragul teszt`, E006/E007 type checker errors, `-val` binding, topological sort. Scope to be decided.)*

---

## Planned Initiative — Bilingual Documentation (2026-03-14)

### Approach

Docs stay in **English prose** throughout. Code examples get **two tabs** (Hungarian / English aliases) using the `pymdownx.tabbed` extension already configured in `mkdocs.yml`. No separate site, no i18n plugin, no duplicate pages.

Example of what tabbed blocks look like in MkDocs Material:

```
=== "Hungarian"
    x-ba  3-t.
    y-ba  x-3-össze-t.

=== "English aliases"
    x-into  3-it.
    y-into  x-3-add-it.
```

### Implementation order

1. **Audit the alias table** — identify which suffixes have no English alias (e.g. `-össze` → `-add`, `-felett` → `-above`). Some stdlib suffixes may need new aliases added to the ALIAS_TABLE and registered in the stdlib.
2. **Add missing English aliases** — update `ragul/model.py` ALIAS_TABLE and `ragul/stdlib/` so every suffix is callable by its English name.
3. **Add a glossary page** (`docs/glossary.md`) — single reference mapping every Hungarian suffix and keyword to its English alias, with a pronunciation guide. Add to MkDocs nav.
4. **Retrofit the 7 example pages** — replace bare code blocks with tabbed blocks. Highest traffic, biggest reader impact.
5. **Retrofit the language reference pages** — syntax, types, functions, control, effects, errors, modules. Work through gradually.

### Status

Complete. All docs pages updated; glossary added. English alias examples verified correct after interpreter bug fixes.

### PyPI readiness note

Fix the 4 interpreter bugs → then publish to PyPI. The package infrastructure (`pyproject.toml`, entry point, README) is already correct. Only remaining PyPI prep work: add classifiers (`Development Status :: 3 - Alpha`, `Programming Language :: Python`, `Topic :: Software Development :: Compilers`) to `pyproject.toml`.

---

*End of report.*
