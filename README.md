# Ragul

> *Ragul* — from Hungarian *rag* (suffix/affix) + *-ul* (in the manner of a language).
> An experimental programming language whose core logic is modelled on agglutinative grammar.

**Meaning is built by stacking suffixes onto a root — a suffix chain is a pipeline.**

```ragul
adatok-szűrve-rendezve-ból  5-felett-val  kimenet-ba  másol-va.
// FROM data→filter(>5)→sort,  INTO output,  AS copy
```

📖 **[Full documentation →](https://kory75.github.io/ragul/)**

---

## Install

Ragul is not yet on PyPI. Install from source:

```bash
git clone https://github.com/kory75/ragul.git
cd ragul
pip install -e ".[dev]"
```

Requires **Python 3.11+**.

---

## Quick Start

```bash
# Run a program
ragul futtat hello.ragul

# Type-check without running
ragul ellenőriz hello.ragul

# Interactive REPL
ragul repl

# Start the LSP server (for editor integration)
ragul lsp
```

---

## Examples

### Hello World

```ragul
program-nk-hatás
    üdvözlet-be  "helló világ"-t.
    üdvözlet-képernyőre-va.
```

### Arithmetic pipeline

```ragul
program-nk-hatás
    x-be  10-t.
    y-be  x-3-össze-2-szoroz-t.   // (10 + 3) × 2 = 26
    y-képernyőre-va.
```

### Filter and sort a list

```ragul
program-nk-hatás
    adatok-be  [7, 2, 15, 3, 9, 1, 12, 4]-t.
    eredmény-be  adatok-szűrve-rendezve-ból  5-felett-val  t.
    eredmény-képernyőre-va.
// [7, 9, 12, 15]
```

### Define and call a custom suffix

```ragul
// Define -kétszeres as a reusable suffix
kétszeres-unk
    szám-d.
    szám-szám-össze-t.

program-nk-hatás
    x-be  7-t.
    y-be  x-kétszeres-t.    // 14
    y-képernyőre-va.
```

### Conditionals

```ragul
besoroló-nk-ha
    szám-d.
    szám-100-felett-ha
        "nagy"-t.
    -különben-ha  szám-50-felett-ha
        "közepes"-t.
    -hanem
        "kicsi"-t.

program-nk-hatás
    kategória-be  75-besoroló-ha-t.
    kategória-képernyőre-va.
// közepes
```

### Loops

```ragul
// Sum a list using fold
összesítő-nk-gyűjt
    elem-d.
    összeg-d.
    összeg-elem-össze-t.

program-nk-hatás
    lista-be  [1, 2, 3, 4, 5]-t.
    összeg-be  lista-összesítő-gyűjt-t  0-val.
    összeg-képernyőre-va.
// 15
```

### Error handling

```ragul
program-nk-hatás
    tartalom-be  "adat.txt"-fájlolvasó-va-e.
    tartalom-képernyőre-va.
    -hibára
        hiba-képernyőre-va.
```

---

## What's in v0.1.0

| Feature | Status |
|---|---|
| Lexer with full alias normalisation | ✅ |
| Parser → Scope tree (indentation-based) | ✅ |
| Static type checker (E001–E009, W001) | ✅ |
| Interpreter — assignment, arithmetic, pipelines | ✅ |
| All loop kinds: `-míg`, `-ig`, `-mindegyik`, `-gyűjt` | ✅ |
| Conditionals: `-ha` / `-hanem` / `-különben-ha` | ✅ |
| Error propagation: `-e` and `-hibára` | ✅ |
| Effect scopes (`-nk-hatás`) + I/O channels | ✅ |
| Stdlib: arithmetic, comparison, logical, string, list, math | ✅ |
| CLI: `futtat`, `ellenőriz`, `fordít`, `repl`, `lsp` | ✅ |
| Interactive REPL with persistent environment | ✅ |
| LSP server: diagnostics, hover, completion, go-to-def | ✅ |
| Agent architecture with Claude AI error analysis | ✅ |
| GitHub Actions CI (pytest + mypy on every push) | ✅ |
| Documentation site (GitHub Pages) | ✅ |

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
>>> x-be  3-t.
>>> y-be  x-kétszeres-t.
>>> y-képernyőre-va.
6
>>> :mutat
x = 3  (Szám)
y = 6  (Szám)
>>> :kilep
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
