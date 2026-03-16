# Ragul

> A pipeline scripting language where **transformation is built into the syntax itself**.
> Each word is a suffix chain — a left-to-right pipeline stacked onto a root value.
> Inspired by the structural principles of agglutinative grammar (Hungarian).

```ragul
data-into  [7, 2, 15, 3, 9, 1, 12, 4]-it.
result-into  data-unique-sorted-5-above-it.
result-print-doing.
// [7, 9, 12, 15]
```

📖 **[Full documentation →](https://kory75.github.io/ragul/)**

---

## Install

```bash
pip install ragul-lang
```

Requires **Python 3.11+**.

To also enable **AI-assisted error explanations** (Claude Opus 4.6, requires `ANTHROPIC_API_KEY`):

```bash
pip install ragul-lang[ai]
```

Or install from source:

```bash
git clone https://github.com/kory75/ragul.git
cd ragul
pip install -e ".[dev]"        # toolchain + dev tools
pip install -e ".[ai,dev]"     # + AI support
```

---

## Quick Start

```bash
# Run a program
ragul run hello.ragul

# Type-check without running
ragul check hello.ragul

# Interactive REPL
ragul repl

# Start the LSP server (for editor integration)
ragul lsp

# Scaffold a new project
ragul new project myapp
```

Hungarian primary names (`futtat`, `ellenőriz`, `repl`, `új`) are also accepted.

---

## Examples

### Hello World

```ragul
program-ours-effect
    greeting-into  "Hello, World!"-it.
    greeting-print-doing.
```

### Arithmetic pipeline

```ragul
program-ours-effect
    x-into  10-it.
    y-into  x-3-add-2-mul-it.   // (10 + 3) × 2 = 26
    y-print-doing.
```

### Filter and sort a list

```ragul
program-ours-effect
    data-into    [7, 2, 15, 3, 9, 1, 12, 4]-it.
    result-into  data-unique-sorted-5-above-it.
    result-print-doing.
// [7, 9, 12, 15]
```

### Define and call a custom suffix

```ragul
// Define -double as a reusable suffix
double-ours
    num-yours.
    num-num-add-it.

program-ours-effect
    x-into  7-it.
    y-into  x-double-it.    // 14
    y-print-doing.
```

### Conditionals

```ragul
classify-ours-if
    num-yours.
    num-100-above-if
        "large"-it.
    -else-if  num-50-above-if
        "medium"-it.
    -else
        "small"-it.

program-ours-effect
    category-into  75-classify-if-it.
    category-print-doing.
// medium
```

### Loops

```ragul
// Sum a list using fold
summer-ours-fold
    item-yours.
    total-yours.
    total-item-add-it.

program-ours-effect
    list-into    [1, 2, 3, 4, 5]-it.
    result-into  list-summer-fold-it  0-with.
    result-print-doing.
// 15
```

### Error handling

```ragul
program-ours-effect
    content-into  "data.txt"-readfile-doing-?.
    content-print-doing.
    -catch
        hiba-print-doing.
```

---

## What's in v0.2.0

| Feature | Status |
|---|---|
| Lexer with full alias normalisation | ✅ |
| Parser → Scope tree (indentation-based) | ✅ |
| Static type checker (E001–E009, W001) | ✅ |
| **E006** scope leak detection | ✅ |
| **E007** module resolution failure | ✅ |
| Interpreter — assignment, arithmetic, pipelines | ✅ |
| All loop kinds: `-while`, `-until`, `-each`, `-fold` | ✅ |
| Conditionals: `-if` / `-else` / `-else-if` | ✅ |
| Error propagation: `-?` and `-catch` | ✅ |
| Effect scopes (`-ours-effect`) + I/O channels | ✅ |
| `true` / `false` boolean aliases | ✅ |
| English I/O aliases: `stdout`, `stdin`, `stderr`, `filein`, `fileout` | ✅ |
| `netin` / `netout` channel stubs | ✅ |
| `adatok` module — JSON + CSV parse/emit, field access | ✅ |
| Stdlib: arithmetic, comparison, logical, string, list, math | ✅ |
| CLI: `run`, `check`, `compile`, `repl`, `lsp`, `new` | ✅ |
| `ragul new project` / `ragul new module` scaffolding | ✅ |
| Interactive REPL with persistent environment | ✅ |
| LSP server: diagnostics, hover, completion, go-to-def | ✅ |
| Agent architecture with Claude AI error analysis | ✅ |
| GitHub Actions CI (pytest + mypy on every push) | ✅ |
| Documentation site (GitHub Pages) | ✅ |
| Published on PyPI as `ragul-lang` | ✅ |

---

## Architecture

```
ragul/
├── model.py          # Word, Sentence, Scope, RagulType + alias table
├── lexer.py          # Tokeniser with alias normalisation at lex time
├── parser.py         # Two-pass: word construction + scope tree assembly
├── typechecker.py    # Static type checker, E001–E009, W001
├── interpreter.py    # Tree-walking interpreter
├── errors.py         # Structured error types and formatters
├── config.py         # ragul.config TOML loader
├── main.py           # CLI entry point
├── stdlib/
│   ├── core.py       # Arithmetic, comparison, logical, string concat
│   └── modules.py    # matematika, szöveg, lista modules
├── agents/
│   ├── orchestrator.py   # Coordinates the pipeline; Claude AI error analysis
│   ├── task.py           # Task / TaskResult message protocol
│   └── ...               # LexerAgent, ParserAgent, TypeAgent, InterpAgent, ...
├── repl/
│   └── repl.py       # Interactive REPL
└── lsp/
    └── server.py     # pygls LSP server
```

---

## Running Tests

```bash
pytest ragul/tests/ -v
```

With type checking:

```bash
python -m mypy ragul/ --ignore-missing-imports
```

---

## Suffix Alias Quick Reference

Each suffix has a canonical Hungarian form plus English and symbolic aliases:

| Role | Canonical | English | Symbol |
|---|---|---|---|
| Source (from) | `-ból` / `-ből` | `-from` | `-<` |
| Target (into) | `-ba` / `-be` | `-into` | `->` |
| Instrument (with) | `-val` / `-vel` | `-with` | `-&` |
| Object (acted on) | `-t` | `-it` | `-*` |
| Action (execute) | `-va` / `-ve` | `-doing` | `-!` |
| Error propagation | `-e` | `-else-fail` | `-?` |

---

## REPL

```bash
ragul repl
```

```
>>> x-into  3-it.
>>> y-into  x-double-it.
>>> y-print-doing.
6
>>> :show
x = 3  (Szám)
y = 6  (Szám)
>>> :exit
```

---

## `ragul.config`

Place at your project root:

```toml
[projekt]
nev     = "my-project"
verzio  = "0.1.0"
belepes = "main.ragul"

[ellenorzes]
harmonia = "warn"   # "warn" | "strict" | "off"
tipus    = "warn"   # "warn" | "strict" | "off"
```

---

## License

Apache 2.0 — see [LICENSE](LICENSE) for the full text.
