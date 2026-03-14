# Ragul

**Ragul** is an experimental programming language whose core logic is modelled on **agglutinative grammar** — specifically the structural principles of Hungarian. Rather than using Hungarian words as commands, Ragul takes the *architecture* of the language as its computational model.

> *Ragul* — from Hungarian *rag* (suffix/affix) + *-ul* (the suffix meaning "in the manner of a language", as in *magyarul* = in Hungarian). A language named by applying a suffix to the word for suffix. Self-referential by design.

---

## The Central Idea

**Meaning is built by stacking suffixes onto a root.** Each suffix adds exactly one layer of semantic transformation. A Ragul word is not just a name — it is a pipeline.

```
data-szűrve-rendezve-ból
// data → filter → sort → FROM
```

Key properties that follow from this design:

- **No brackets for structure** — suffix chains carry all meaning
- **Free word order** — roles are encoded in suffixes, not position
- **A function call is a suffix**, not a separate construct
- **A scope definition and a function definition are the same thing**

---

## Quick Example

```ragul
// Define a suffix that doubles a number
kétszeres-unk
    szám-d.
    szám-szám-össze-t.

// Use it
program-nk-hatás
    x-be  3-t.
    y-be  x-kétszeres-t.
    y-képernyőre-va.
// prints: 6
```

---

## Getting Started

Ragul is not yet on PyPI. Install from source:

```bash
git clone https://github.com/kory75/ragul.git
cd ragul
pip install -e ".[dev]"
```

Then run a program:

```bash
ragul futtat hello.ragul
```

Check a file for type errors:

```bash
ragul ellenőriz hello.ragul
```

Start the interactive REPL:

```bash
ragul repl
```

---

## Navigation

| Section | Contents |
|---|---|
| [Syntax](syntax.md) | Words, sentences, suffix stacking, assignment |
| [Types](types.md) | Type system, generics, harmony, or-types |
| [Functions & Scopes](functions.md) | Scopes, parameters, return values |
| [Control Flow](control.md) | Conditionals, loops, early exit |
| [Effects & I/O](effects.md) | The `-hatás` model, I/O channels |
| [Error Handling](errors.md) | `vagy` types, `-e` propagation, `-hibára` |
| [Modules](modules.md) | Module system, imports, visibility |
| [Standard Library](stdlib.md) | Built-in suffixes reference |
| [Tooling & CLI](tooling.md) | CLI commands, `ragul.config`, error codes |
