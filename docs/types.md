# Types

## Inference

Ragul is **inferred typed**. Types are never declared explicitly — the compiler traces them from usage:

=== "Hungarian"
    ```ragul
    x-be  3-t.           // compiler: x is Szám
    y-be  "hello"-t.     // compiler: y is Szöveg
    lista-be  [1,2,3]-t. // compiler: lista is Lista-Szám
    ```

=== "English aliases"
    ```ragul
    x->  3-obj.           // compiler: x is Num
    y->  "hello"-obj.     // compiler: y is Str
    lista->  [1,2,3]-obj. // compiler: lista is List-Num
    ```

---

## Core Types

| Hungarian | English aliases | Meaning | Examples |
|---|---|---|---|
| `Szám` | `Num` / `Number` | Numbers, measurements | `3`, `3.14`, `-7` |
| `Szöveg` | `Str` / `Text` / `String` | Strings, text | `"hello"`, `"adat.txt"` |
| `Lista` | `List` | Collections | `[1,2,3]`, `["a","b"]` |
| `Logikai` | `Bool` | Booleans | `igaz`, `hamis` |
| `Hiba` | `Err` / `Error` | Error values | propagated via `-e` / `-?` |

Types are capitalised to distinguish them from variable roots, which are lowercase.

English aliases are resolved at parse time — `Num` and `Szám` are identical to the compiler. Mixed usage within a file is permitted.

---

## Generic Types — `Lista-T` / `List-T`

`Lista` / `List` is a generic type — it always carries an element type, written as a suffix chain:

```
Lista-Szám        // a list of numbers      (Hungarian)
List-Num          // a list of numbers      (English aliases)
Lista-Szöveg      // a list of strings
List-Str          // a list of strings
Lista-Lista-Szám  // a list of lists of numbers
List-List-Num     // a list of lists of numbers
```

This notation is consistent with the rest of Ragul — types are built by suffixing, exactly as words are. `Lista` is the root, the element type is its suffix. Nesting composes naturally by continuing the chain.

---

## Or-Types — `vagy` / `or`

`vagy` / `or` (meaning *or*) creates a union type. It is used when an operation may succeed or fail:

=== "Hungarian"
    ```ragul
    // vagy-Szöveg-vagy-Hiba = either a Szöveg OR a Hiba
    eredmény-be  "adat.txt"-fájlolvasó-va.
    // eredmény is vagy-Szöveg-vagy-Hiba
    ```

=== "English aliases"
    ```ragul
    // or-Str-or-Err = either a Str OR an Err
    result->  "adat.txt"-fájlolvasó-doing.
    // result is or-Str-or-Err
    ```

The compiler enforces that both branches of a `vagy` / `or` type are handled before the value is used. See [Error Handling](errors.md) for the full model.

Three-way compounds are legal when needed:

```
vagy-Szám-vagy-Szöveg-vagy-Hiba   // Hungarian
or-Num-or-Str-or-Err              // English aliases
```

---

## Two-Level Type Enforcement

Suffix type checking has two levels:

1. **Root guard** — does the root's type support this suffix at all?
2. **Suffix guard** — does the suffix's contract accept the root's concrete type, including element types for `Lista-T`?

=== "Hungarian"
    ```ragul
    szavak-be  ["a","b","c"]-t.        // Lista-Szöveg
    szavak-3-felett-szűrve-t.
    // ERROR: -felett expects Szám element — got Szöveg
    ```

=== "English aliases"
    ```ragul
    words->  ["a","b","c"]-obj.        // Lista-Szöveg
    words-3-above-filter-obj.
    // ERROR: -above expects Szám element — got Szöveg
    ```

---

## Suffix Type Contracts

Each suffix declares what it expects and what it produces:

| Hungarian | English | Expects | Produces | Arg type |
|---|---|---|---|---|
| `-felett` | `-above` | `Szám` | `Logikai` | `Szám` |
| `-alatt` | `-below` | `Szám` | `Logikai` | `Szám` |
| `-rendezve` | `-sorted` | `Lista-T` | `Lista-T` | — |
| `-szűrve` | `-filter` | `Lista-T` | `Lista-T` | condition |
| `-fordítva` | `-reversed` | `Lista-T` | `Lista-T` | — |
| `-hossz` | `-len` | `Lista-T` or `Szöveg` | `Szám` | — |
| `-szöteggé` | `-tostr` | `Szám` | `Szöveg` | — *(bridge)* |
| `-számmá` | `-tonum` | `Szöveg` | `vagy-Szám-vagy-Hiba` | — *(bridge, fallible)* |

**Bridge suffixes** explicitly convert between types and must be used when chaining across type boundaries.

---

## Type Annotations with `-ként` / `-as`

The `-ként` / `-as` suffix (meaning *acting as / in the role of*) provides optional type annotations on scope parameters and return values:

=== "Hungarian"
    ```ragul
    kétszeres-unk
        szám-d  Szám-ként.
        szám-szám-össze-t  Szám-ként.
    ```

=== "English aliases"
    ```ragul
    kétszeres-ours
        szám-yours  Num-as.
        szám-szám-add-obj  Num-as.
    ```

Reading naturally: *"szám, passed in, acting as a Num"* — and the return *"acting as a Num"*.

A fallible suffix return type:

=== "Hungarian"
    ```ragul
    fájlolvasó-unk
        útvonal-d  Szöveg-ként.
        útvonal-fájlról-ből  olvas-va-t  vagy-Szöveg-vagy-Hiba-ként.
    ```

=== "English aliases"
    ```ragul
    fájlolvasó-ours
        path-yours  Str-as.
        path-fájlról-from  read-doing-obj  or-Str-or-Err-as.
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
