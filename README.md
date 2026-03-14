# Ragul Compiler — v0.1.0

> *Ragul* — from Hungarian *rag* (suffix/affix) + *-ul* (in the manner of a language).  
> An experimental programming language whose core logic is modelled on agglutinative grammar.

---

## What works in v0.1.0

| Feature | Status |
|---|---|
| Lexer with full alias normalisation | ✅ |
| Parser → Scope tree (indentation-based) | ✅ |
| Interpreter — assignment, arithmetic, comparisons | ✅ |
| Inline suffix arguments (`x-3-össze-t`) | ✅ |
| Variable references in chains (`a-b-össze-t`) | ✅ |
| String & list literals | ✅ |
| Effect scopes (`-nk-hatás`) + console I/O | ✅ |
| `képernyőre` channel | ✅ |
| Stdlib: core arithmetic, comparison, logical, string concat | ✅ |
| Stdlib: `matematika` (sqrt, power, abs, round…) | ✅ |
| Stdlib: `szöveg` (uppercase, split, length…) | ✅ |
| Stdlib: `lista` (sort, filter, reverse, unique…) | ✅ |
| Polymorphic suffixes (list filter vs scalar compare) | ✅ |
| `ragul futtat` CLI | ✅ |
| `ragul ellenőriz` CLI | ✅ |
| REPL (`ragul repl`) | ✅ |
| 47 automated tests, all passing | ✅ |

---

## Install

```bash
pip install -e ".[dev]"
```

Requires Python 3.11+.

---

## Running Programs

```bash
# Run a Ragul source file
ragul futtat hello.ragul

# Type-check without running
ragul ellenőriz hello.ragul

# Interactive REPL
ragul repl
```

---

## Language Quick Reference

### Assignment
```
x-ba  3-t.
üdvözlet-ba  "Helló, világ!"-t.
számok-ba  [1, 2, 3]-t.
```

### Arithmetic
```
y-ba  x-3-össze-t.       // x + 3
z-ba  x-y-szoroz-t.      // x × y
m-ba  x-5-maradék-t.     // x mod 5
```

### Effect scope (I/O)
```
program-nk-hatás
    x-ba  "hello"-t.
    x-képernyőre-va.
```

### Suffix chaining (pipeline)
```
rendezett-ba  számok-egyedi-rendezve-t.
nagyok-ba     rendezett-3-felett-t.
```

### Scope / function definition
```
kétszeres-unk
    szám-d.
    szám-szám-össze-t.

y-ba  x-kétszeres-t.
```

### Module import
```
matematika-ból  négyzetgyök-val.
szöveg-ből  nagybetűs-val.
lista-ból.
```

---

## Architecture

```
ragul/
├── model.py        # Word, Sentence, Scope, RagulType dataclasses + alias table
├── lexer.py        # Tokeniser with alias normalisation at lex time
├── parser.py       # Two-pass: word construction + scope tree assembly
├── interpreter.py  # Tree-walking eager evaluator
├── errors.py       # Structured error types E001–E009, W001
├── config.py       # ragul.config TOML loader
└── stdlib/
    ├── core.py     # Always-available: arithmetic, comparison, logical
    └── modules.py  # matematika, szöveg, lista modules
```

---

## Test Suite

```bash
pytest tests/ -v
# 47 passed in 0.15s
```

---

## Next Phases

- **Phase 3** — Type checker (E001, E004, E005)
- **Phase 7** — LSP server (diagnostics, hover, completion)
- **Phase 8** — GitHub Pages documentation site
