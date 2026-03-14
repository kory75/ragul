# Ragul Toolchain — Build Plan
**Language:** Python 3.11+ | **Structure:** Orchestrator + Specialist Agents  
**Delivery:** CLI (`ragul`), GitHub CI reporting, GitHub Pages docs

---

## 1. Repository Layout

```
ragul/
├── ragul/                        # core library
│   ├── __init__.py
│   ├── model.py                  # Word dataclass, Sentence, ScopeTree
│   ├── lexer.py
│   ├── parser.py
│   ├── typechecker.py
│   ├── interpreter.py
│   ├── errors.py                 # E001–E009, W001 + formatting
│   ├── config.py                 # ragul.config TOML loader
│   └── stdlib/
│       ├── __init__.py
│       ├── core.py               # arithmetic, comparison, logical
│       ├── matematika.py
│       ├── szoveg.py
│       └── lista.py
├── ragul/repl/
│   └── repl.py                   # REPL loop
├── ragul/lsp/
│   ├── server.py                 # pygls-based LSP server
│   ├── hover.py
│   ├── diagnostics.py
│   └── completion.py
├── agents/
│   ├── orchestrator.py           # top-level Claude agent
│   ├── lexer_agent.py
│   ├── parser_agent.py
│   ├── typecheck_agent.py
│   ├── interpreter_agent.py
│   ├── repl_agent.py
│   ├── lsp_agent.py
│   └── docs_agent.py
├── cli/
│   └── main.py                   # `ragul futtat`, `ellenőriz`, `fordít`
├── tests/
│   ├── test_lexer.py
│   ├── test_parser.py
│   ├── test_typechecker.py
│   ├── test_interpreter.py
│   └── fixtures/                 # .ragul test programs
├── docs/                         # GitHub Pages source (MkDocs)
│   ├── index.md
│   ├── syntax.md
│   ├── types.md
│   ├── stdlib.md
│   └── mkdocs.yml
├── .github/
│   └── workflows/
│       ├── ci.yml                # test + type-check on every push/PR
│       └── docs.yml              # deploy GitHub Pages on main merge
├── pyproject.toml
├── ragul.config                  # project's own config (dogfooding)
└── README.md
```

---

## 2. Core Data Model  (`ragul/model.py`)

This is the foundation everything else builds on. Must be done before any agent starts.

```python
@dataclass
class Word:
    root:       str
    possession: str | None        # -unk, -m, -d, -ja, etc.
    aspects:    list[str]         # ordered, left-to-right
    action:     str | None        # -va / -ve
    error:      bool              # -e present
    case:       str               # -ból, -ba, -val, -t, -ként, etc.
    val_args:   list['Word']      # -val bindings resolved at parse time

@dataclass
class Sentence:
    words:      list[Word]
    line:       int

@dataclass
class Scope:
    name:       str
    possession: str | None
    is_effect:  bool              # -hatás
    is_module:  bool              # -modul
    sentences:  list[Sentence]
    children:   list['Scope']
    parent:     'Scope | None'
```

Alias normalisation lives here too — a lookup table maps `-from` → `-ból`, `->` → `-ba`, `-&` → `-val`, etc. Both the lexer and parser operate on canonical forms only.

---

## 3. Agent Architecture

```
┌─────────────────────────────────────────────┐
│              OrchestratorAgent              │
│  • reads ragul.config                       │
│  • receives user command (futtat / ellenőriz│
│    / fordít / repl / lsp)                   │
│  • builds task graph                        │
│  • delegates to specialist agents           │
│  • collects results, formats final output   │
└────────┬───────────────────────────────────-┘
         │  delegates via typed task messages
    ┌────┴──────────────────────────────────┐
    │  LexerAgent   →  token stream         │
    │  ParserAgent  →  Scope tree           │
    │  TypeAgent    →  annotated tree +     │
    │                  error list           │
    │  InterpAgent  →  execution result     │
    │  ReplAgent    →  interactive session  │
    │  LspAgent     →  JSON-RPC server      │
    │  DocsAgent    →  HTML/MD site         │
    └───────────────────────────────────────┘
```

### Task message protocol (all agents speak this)

```python
@dataclass
class Task:
    kind: str                     # "lex", "parse", "typecheck", etc.
    source: str | None            # raw source text
    scope_tree: Scope | None      # parsed result when already available
    config: RagulConfig
    flags: dict                   # e.g. {"strict": True}

@dataclass
class TaskResult:
    ok: bool
    payload: Any                  # tokens / scope tree / value / diagnostics
    errors: list[RagulError]
    warnings: list[RagulWarning]
```

The orchestrator never calls the compiler pipeline directly — it only constructs `Task` objects and calls `agent.run(task)`. Each agent returns a `TaskResult`. This makes every stage independently testable and replaceable.

---

## 4. Build Phases

### Phase 0 — Scaffold  *(~1 day)*
- `pyproject.toml` with `[project.scripts] ragul = "cli.main:main"`
- `ragul/model.py` — `Word`, `Sentence`, `Scope`, alias table
- `ragul/errors.py` — `RagulError` dataclass, E001–E009 formatters
- `ragul/config.py` — TOML loader for `ragul.config`
- Stub `agents/orchestrator.py` with routing logic but no-op agents
- `tests/` folder with pytest config
- GitHub Actions `ci.yml` — runs pytest on push

**Milestone:** `ragul --help` works. Every agent returns a stub result. CI green.

---

### Phase 1 — Lexer  *(~2 days)*

**Responsibility:** `LexerAgent` + `ragul/lexer.py`

The lexer's only job is splitting source into tokens, each carrying type and position. Ragul's surface syntax is regular enough that a hand-written lexer is appropriate.

**Token types:**
```
WORD        # root-suffix chain (e.g. "x-ból", "data-szűrve-rendezve-ból")
NUMBER      # integer or float literal
STRING      # "..." literal
LIST_OPEN   # [
LIST_CLOSE  # ]
FULLSTOP    # .
NEWLINE     # significant for scope dedent
INDENT
DEDENT
COMMENT     # // ...
EOF
```

**Key decision — alias normalisation at lex time.** The lexer resolves all suffix aliases to their canonical Hungarian form before the token leaves the lexer. The alias table in `model.py` is the single source of truth. The parser never sees `-from`, `->`, or `-&`.

**Output:** `list[Token]`  
**Error:** `E002` for unrecognised suffix in a chain

**Tests to write:**
- All suffix aliases resolve to canonical
- String with escaped quotes
- Nested list literal `[[1,2],[3,4]]`
- Mixed indentation produces correct INDENT/DEDENT stream
- Comment lines produce no tokens

---

### Phase 2 — Parser  *(~3 days)*

**Responsibility:** `ParserAgent` + `ragul/parser.py`

The parser consumes the token stream and produces the `Scope` tree. Because word order is free, the parser does **not** determine meaning — it only validates structural well-formedness.

**Two-pass strategy:**

*Pass 1 — Word construction:* For each `WORD` token, split at `-` boundaries and populate a `Word` dataclass. Validate suffix layer order (possession → aspects → action → error → case) and raise `E002` immediately on violation.

*Pass 2 — Sentence assembly:* Group consecutive `Word` tokens within the same indent level into `Sentence` objects. A `FULLSTOP` terminates the current sentence. Indentation changes open/close `Scope` nodes.

**Scope name extraction:** A sentence whose only word ends in `-unk`/`-nk`, `-nk-hatás`, or `-nk-modul` at outermost indent opens a named child scope.

**Output:** `Scope` (the root scope, with all children)  
**Errors:** `E002` (layer order), structural parse errors

**Tests to write:**
- Free word order — all permutations of a 3-word sentence produce identical `Sentence`
- Nested scopes at 1, 2, 3 levels
- `-unk` scope correctly creates child
- `-hatás` flag set on effect scopes
- `-val` bindings attached to correct `Word`

---

### Phase 3 — Type Checker  *(~4 days)*

**Responsibility:** `TypeAgent` + `ragul/typechecker.py`

This is the most complex phase. The checker walks the `Scope` tree and annotates every `Word` with its inferred type, then validates each suffix chain against the suffix type contracts in `model.py`.

**Two-level enforcement (spec §3.5):**

1. **Root guard** — does the root's type support this suffix at all?
2. **Suffix guard** — does the suffix's contract accept the root's concrete type, including element types for `Lista-T`?

**Type representation:**

```python
@dataclass
class RagulType:
    base: str                     # "Szám", "Szöveg", "Lista", "vagy", "Logikai", "Hiba"
    params: list['RagulType']     # Lista-Szám → base="Lista", params=[Szám]
                                  # vagy-Szöveg-vagy-Hiba → base="vagy", params=[Szöveg, Hiba]
```

**Harmony checker:** After type annotation is complete, walk every suffix chain and flag chains that cross type boundaries without a bridge suffix. Behaviour controlled by `ragul.config harmonia:`.

**`vagy` enforcement:** Any root with a `vagy` type must be consumed via `-va-e` (propagate) or handled in a `-hibára` block before its value is used. Violation is `E005`.

**Effect boundary:** Walking the scope tree, track whether the current scope is under a `-hatás` ancestor. Flag any effectful suffix call (`képernyőre`, `fájlra`, etc.) in a pure scope as `E004`.

**Parallel write detection:** Within a scope's sentence list, find any two sentences that both write to the same root name via `-ba`/`-be`. Raise `E003`.

**Output:** annotated `Scope` tree + `list[RagulError | RagulWarning]`  
**Config flags:** `harmonia`, `tipus`

**Tests to write (one per error code):**
- E001: `"hello"-felett` → root guard fail
- E003: same root written twice in scope
- E004: effectful suffix in pure scope
- E005: unhandled `vagy` type
- W001: chain crossing types without bridge (harmony warn)
- Type preservation through `-rendezve`, `-szűrve`, `-fordítva`
- `Lista-Lista-Szám` inferred from `[[1,2],[3,4]]`

---

### Phase 4 — Interpreter  *(~4 days)*

**Responsibility:** `InterpAgent` + `ragul/interpreter.py`

Receives an annotated `Scope` tree. Builds a dependency graph from case roles, then evaluates in dependency order.

**Dependency graph construction:**

For each sentence, identify the "writer" word (the one with `-ba`/`-be` case) and the "reader" words (all others). The writer depends on all readers. This graph is a DAG by construction — cycles are caught here as a structural error.

**Evaluation engine (MVP = eager within pure scopes):**

```
evaluate(scope):
    sort sentences by dependency order (topological sort)
    for each sentence in order:
        resolve each word's value by walking its aspect chain
        bind result to the target root
```

**Aspect chain evaluation:**

```
eval_word(word, env):
    value = env.lookup(word.root)
    for aspect in word.aspects:
        suffix_fn = stdlib.lookup(aspect) or user_scope.lookup(aspect)
        val_arg = eval_word(next_val_arg)   # consume -val args left-to-right
        value = suffix_fn(value, val_arg)
    if word.action:
        value = execute(value)
    if word.error and isinstance(value, Hiba):
        raise PropagateError(value)
    return coerce_case(value, word.case)
```

**Effect scope execution:** Inside `-hatás`, sentences execute sequentially top-to-bottom. I/O channel suffixes are implemented as Python functions registered in the stdlib table.

**`-hibára` boundary:** Wrap effect scope execution in a try/except for `PropagateError`. On catch, execute the sibling `-hibára` block with `hiba` bound to the error value.

**Standard library wiring:** Each stdlib module (`core.py`, `matematika.py`, etc.) registers suffix functions into a global registry keyed by canonical suffix name. The interpreter looks up suffixes here first, then in user-defined scopes.

**Output:** Python value (or `None` for effect programs) + any runtime errors  
**Exit codes:** 0 success, 2 runtime error, 3 unhandled `Hiba`

**Tests to write:**
- Hello world
- Arithmetic pipeline: `x-3-össze-2-szoroz-t`
- Filter + sort pipeline from spec §2.3
- Nested scope call as suffix
- `-va-e` propagation reaching `-hibára`
- Factorial via `-míg` loop
- `-mindegyik` mapping doubles list
- `-gyűjt` summing a list

---

### Phase 5 — CLI  *(~1 day)*

**Responsibility:** `cli/main.py` wiring the orchestrator

```bash
ragul futtat   <file>   [--config ragul.config]
ragul ellenőriz <file>  [--strict]
ragul fordít   <file>   [--out ./build]
```

The CLI constructs a `Task`, calls `OrchestratorAgent.run(task)`, and formats the `TaskResult` to stdout. Error output goes to stderr. Exit codes match spec §14.5.

Hungarian command names are primary; English aliases (`run`, `check`, `compile`) are accepted silently for convenience.

---

### Phase 6 — REPL  *(~2 days)*

**Responsibility:** `ReplAgent` + `ragul/repl/repl.py`

```
ragul repl
>>> x-be  3-t.
>>> x-kétszeres-ből  kimenet-be  ír-va.
6
>>>
```

**Design:** The REPL maintains a persistent root environment across sentences. Each sentence is lexed, parsed, type-checked, and interpreted in the context of the accumulated scope. The REPL agent wraps the full pipeline, passing the live scope as context on each round trip.

**Continuation detection:** If a sentence is incomplete (no `.` yet), the REPL prompts with `...` for continuation rather than attempting to evaluate. This makes multi-line scope definitions work naturally.

**Special REPL commands:**

| Command | Action |
|---|---|
| `:kilep` / `:exit` | Quit |
| `:töröl` / `:clear` | Reset scope |
| `:mutat` / `:show` | Print all bound roots and their types |
| `:help` | Usage |

---

### Phase 7 — LSP Server  *(~5 days)*

**Responsibility:** `LspAgent` + `ragul/lsp/`

Built on [pygls](https://github.com/openlawlibrary/pygls). The LSP agent wraps the full lexer → parser → type-checker pipeline and exposes diagnostics, hover, and completion over JSON-RPC.

**Features for v1:**

| LSP Feature | Implementation |
|---|---|
| Diagnostics | Run type-checker on every `textDocument/didChange`; map `RagulError` → LSP `Diagnostic` |
| Hover | On hover over a `WORD` token, show inferred type from annotated tree |
| Completion | After a `-`, suggest valid suffixes for the current root's type |
| Go-to-definition | For a scope-defined suffix, jump to its `-unk` declaration |

**`ragul/lsp/diagnostics.py`:** converts `RagulError` objects (which already carry file, line, code, message) directly to LSP `Diagnostic` objects. Almost no translation needed because the error format was designed to be structured.

**Editor integration (documented in GitHub Pages):**
- VS Code: point to `ragul lsp` as the server command in a simple extension manifest
- Neovim: `nvim-lspconfig` entry pointing to `ragul lsp`

---

### Phase 8 — Docs Site  *(~2 days)*

**Responsibility:** `DocsAgent` + `docs/` + GitHub Pages

**Stack:** MkDocs + Material theme. Source is Markdown in `docs/`. Deployed automatically to GitHub Pages via `docs.yml` workflow on every merge to `main`.

**Site structure:**

```
docs/
├── index.md          → Language overview + design philosophy (from spec §1)
├── syntax.md         → Words, sentences, suffix stacking (§2)
├── types.md          → Type system, or-types, harmony (§3–4)
├── functions.md      → Scopes, parameters, return (§5–6)
├── control.md        → Conditionals, loops (§8)
├── effects.md        → I/O, -hatás model (§9)
├── errors.md         → Error handling, -hibára (§10)
├── modules.md        → Module system (§11)
├── stdlib.md         → Standard library reference (§12)
├── oop.md            → Object model (§17)
├── concurrency.md    → Implicit parallelism (§13)
├── tooling.md        → CLI, config, error codes (§14)
└── examples/
    ├── hello.md
    ├── pipeline.md
    └── file-io.md
```

**DocsAgent's role:** The `DocsAgent` is a Claude-powered sub-agent that can auto-generate example programs for the docs site. Given a section topic, it calls the Anthropic API with the spec as context and asks it to produce a worked Ragul example. Each example is then run through `ragul ellenőriz` to verify it type-checks before being committed to `docs/`.

---

## 5. GitHub Workflows

### `ci.yml` — runs on every push and PR

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e ".[dev]"
      - run: pytest tests/ --tb=short --json-report --json-report-file=report.json
      - run: python -m mypy ragul/
      - uses: actions/upload-artifact@v4
        with: { name: test-report, path: report.json }
```

The JSON test report becomes the source of truth for the GitHub PR comment — a small action script reads it and posts a pass/fail summary as a PR check.

### `docs.yml` — runs on merge to main

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install mkdocs-material
      - run: mkdocs gh-deploy --force
```

GitHub Pages serves from the `gh-pages` branch. No separate hosting needed.

---

## 6. Dependency Stack

```toml
# pyproject.toml
[project]
requires-python = ">=3.11"
dependencies = [
    "tomllib",          # ragul.config parsing (stdlib in 3.11+)
    "pygls>=1.3",       # LSP server
    "prompt_toolkit",   # REPL line editing, history, syntax highlighting
    "anthropic",        # DocsAgent + OrchestratorAgent Claude calls
    "rich",             # CLI error formatting (colours, panels)
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-json-report",
    "mypy",
    "mkdocs-material",
]
```

---

## 7. Build Order & Critical Path

```
Phase 0 (scaffold)
    └── Phase 1 (lexer)
            └── Phase 2 (parser)
                    ├── Phase 3 (typechecker)
                    │       ├── Phase 4 (interpreter)
                    │       │       ├── Phase 5 (CLI) ← first usable release
                    │       │       ├── Phase 6 (REPL)
                    │       │       └── Phase 7 (LSP)
                    │       └── Phase 8 (docs) ← can run in parallel with 4–7
                    └── (stdlib fills in alongside interpreter)
```

The docs site can be started as soon as the type system is stable (Phase 3) because the example programs just need to type-check, not execute. LSP and REPL are independent of each other and can be built in parallel after Phase 4 is done.

---

## 8. First Milestone Checklist

This is the target for a first usable `v0.1.0` tag:

- [ ] `Word` dataclass with full suffix layer model
- [ ] All suffix aliases resolve to canonical forms
- [ ] Parser handles flat sentences + 2-level nesting
- [ ] Type checker catches E001, E004, E005
- [ ] Interpreter runs: assignment, arithmetic, filter/sort pipeline, effect scope with console output
- [ ] `ragul futtat hello.ragul` works end-to-end
- [ ] `ragul ellenőriz` reports structured errors with line numbers
- [ ] CI green on push
- [ ] GitHub Pages deployed with at least index + syntax + stdlib pages