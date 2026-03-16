# Ragul

**Ragul** is a pipeline scripting language where **transformation is built into the syntax itself**. Rather than a pipe operator or method chain, each word in a Ragul program is a suffix chain — a left-to-right pipeline of operations stacked onto a root value. The result is code that reads like a recipe: each step is named, each transformation is explicit, and the type checker verifies every stage before the program runs.

The design is inspired by the structural principles of **agglutinative grammar** — specifically Hungarian, where meaning is built by attaching suffixes to roots. Ragul takes that architecture and applies it to computation.

> *Ragul* — from Hungarian *rag* (suffix/affix) + *-ul* (the suffix meaning "in the manner of a language", as in *magyarul* = in Hungarian). A language named by applying a suffix to the word for suffix. Self-referential by design.

---

## The Central Idea

**Meaning is built by stacking suffixes onto a root.** Each suffix adds exactly one layer of semantic transformation. A Ragul word is not just a name — it is a pipeline.

=== "English aliases"
    ```ragul
    data-filter-sorted-from
    // data → filter → sort → FROM
    ```

=== "Hungarian"
    ```ragul
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

=== "English aliases"
    ```ragul
    // Define a suffix that doubles a number
    double-ours
        num-yours.
        num-num-add-it.

    // Use it
    program-ours-effect
        x-into  3-it.
        y-into  x-double-it.
        y-print-doing.
    // prints: 6
    ```

=== "Hungarian"
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

!!! note "Scope names are user-defined"
    `double`, `num`, `program`, `x`, `y` are root identifiers chosen by the programmer —
    they can be any word in any language. Only the *suffixes* have fixed forms.
    The Hungarian tab uses `kétszeres` (double) and `szám` (number) for the same roots.

---

## Getting Started

### Install from PyPI (recommended)

```bash
pip install ragul-lang
```

To also enable **AI-assisted error explanations** (powered by Claude — requires an `ANTHROPIC_API_KEY`):

```bash
pip install ragul-lang[ai]
```

### Install from source

```bash
git clone https://github.com/kory75/ragul.git
cd ragul
pip install -e ".[dev]"
# with AI support:
pip install -e ".[ai,dev]"
```

Then run a program:

```bash
ragul futtat hello.ragul
# or
ragul run hello.ragul
```

Check a file for type errors:

```bash
ragul ellenőriz hello.ragul
# or
ragul check hello.ragul
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
| [Effects & I/O](effects.md) | The `-hatás` / `-effect` model, I/O channels |
| [Error Handling](errors.md) | `vagy` types, `-e` propagation, `-hibára` / `-catch` |
| [Modules](modules.md) | Module system, imports, visibility |
| [Standard Library](stdlib.md) | Built-in suffixes reference |
| [Tooling & CLI](tooling.md) | CLI commands, `ragul.config`, error codes |
| [Glossary](glossary.md) | Every suffix mapped to its English alias + pronunciation |
