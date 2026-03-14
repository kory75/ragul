# Types

## Inference

Ragul is **inferred typed**. Types are never declared explicitly — the compiler traces them from usage:

```ragul
x-be  3-t.           // compiler: x is Szám
y-be  "hello"-t.     // compiler: y is Szöveg
lista-be  [1,2,3]-t. // compiler: lista is Lista-Szám
```

---

## Core Types

| Type | Meaning | Examples |
|---|---|---|
| `Szám` | Numbers, measurements | `3`, `3.14`, `-7` |
| `Szöveg` | Strings, text | `"hello"`, `"adat.txt"` |
| `Lista` | Collections | `[1,2,3]`, `["a","b"]` |
| `Logikai` | Booleans | `igaz`, `hamis` |
| `Hiba` | Error values | propagated via `-e` |

Types are capitalised to distinguish them from variable roots, which are lowercase.

---

## Generic Types — `Lista-T`

`Lista` is a generic type — it always carries an element type, written as a suffix chain:

```
Lista-Szám        // a list of numbers
Lista-Szöveg      // a list of strings
Lista-Logikai     // a list of booleans
Lista-Lista-Szám  // a list of lists of numbers
```

This notation is consistent with the rest of Ragul — types are built by suffixing, exactly as words are. `Lista` is the root, the element type is its suffix. Nesting composes naturally by continuing the chain.

---

## Or-Types — `vagy`

`vagy` (meaning *or*) creates a union type. It is used when an operation may succeed or fail:

```ragul
// vagy-Szöveg-vagy-Hiba = either a Szöveg OR a Hiba
eredmény-be  "adat.txt"-fájlolvasó-va.
// eredmény is vagy-Szöveg-vagy-Hiba
```

The compiler enforces that both branches of a `vagy` type are handled before the value is used. See [Error Handling](errors.md) for the full model.

Three-way compounds are legal when needed:

```
vagy-Szám-vagy-Szöveg-vagy-Hiba
```

---

## Two-Level Type Enforcement

Suffix type checking has two levels:

1. **Root guard** — does the root's type support this suffix at all?
2. **Suffix guard** — does the suffix's contract accept the root's concrete type, including element types for `Lista-T`?

```ragul
szavak-be  ["a","b","c"]-t.        // Lista-Szöveg
szavak-3-felett-szűrve-t.
// ERROR: -felett expects Szám element — got Szöveg
```

---

## Suffix Type Contracts

Each suffix declares what it expects and what it produces:

| Suffix | Expects | Produces | Arg type |
|---|---|---|---|
| `-felett` | `Szám` | `Logikai` | `Szám` |
| `-alatt` | `Szám` | `Logikai` | `Szám` |
| `-rendezve` | `Lista-T` | `Lista-T` | — |
| `-szűrve` | `Lista-T` | `Lista-T` | condition |
| `-fordítva` | `Lista-T` | `Lista-T` | — |
| `-hossz` | `Lista-T` or `Szöveg` | `Szám` | — |
| `-szöveggé` | `Szám` | `Szöveg` | — *(bridge)* |
| `-számmá` | `Szöveg` | `vagy-Szám-vagy-Hiba` | — *(bridge, fallible)* |

**Bridge suffixes** explicitly convert between types and must be used when chaining across type boundaries.

---

## Type Annotations with `-ként`

The `-ként` suffix (meaning *acting as / in the role of*) provides optional type annotations on scope parameters and return values:

```ragul
kétszeres-unk
    szám-d  Szám-ként.
    szám-szám-össze-t  Szám-ként.
```

Reading naturally: *"szám, passed in, acting as a Szám"* — and the return *"acting as a Szám"*. No new syntax — `-ként` already exists.

A fallible suffix return type:

```ragul
fájlolvasó-unk
    útvonal-d  Szöveg-ként.
    útvonal-fájlról-ből  olvas-va-t  vagy-Szöveg-vagy-Hiba-ként.
```

Annotations are **optional** — unannotated scopes still work via inference. They are most useful for:

- Public suffixes others will call (library code)
- Bridge suffixes where the type change is non-obvious
- Any suffix returning `vagy` — callers need to know the failure type

---

## Vowel Harmony (Type Harmony)

Inspired by Hungarian vowel harmony, Ragul supports an optional **type harmony** warning system. Suffix chains that cross types without a bridge suffix can be flagged.

Controlled in `ragul.config`:

```toml
[ellenorzes]
harmonia = "warn"    # warn on dissonant chains (default)
# harmonia = "strict"  # treat as compile error
# harmonia = "off"     # silent
```

This feature is informational — it never blocks compilation unless `strict` is set.
