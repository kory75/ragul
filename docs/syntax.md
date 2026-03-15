# Syntax

## The Sentence

The base unit of Ragul is a **sentence** — multiple roots interacting, terminated by a full stop.

```
root₁-suffixes  root₂-suffixes  root₃-suffixes.
```

Because every root's role is encoded in its suffix chain, **word order is free**. These sentences are identical:

=== "English aliases"
    ```ragul
    x-from  output->  copy-doing.
    output->  copy-doing  x-from.
    copy-doing  x-from  output->.
    ```

=== "Hungarian"
    ```ragul
    x-ból  kimenet-ba  másol-va.
    kimenet-ba  másol-va  x-ból.
    másol-va  x-ból  kimenet-ba.
    ```

---

## The Word

A Ragul word is a root followed by a suffix chain. The suffix stack follows a fixed hierarchy:

```
root - [possession] - [aspect]* - [action] - [error] - case
```

| Layer | Position | Role |
|---|---|---|
| Root | Base | The thing being described |
| Possession | Innermost suffix | Ownership / scope / lifetime |
| Aspect(s) | Middle (repeatable) | Transformations applied to the root |
| Action | After aspects | Executes the operation (`-va` / `-doing`) |
| Error | After action | Propagates failure upward (`-e` / `-?`) |
| Case | Outermost suffix | The role this word plays in the sentence |

---

## Suffix Stacking

Aspect suffixes stack left to right, each operating on the result of the previous. This encodes a mini-pipeline inside a single word:

=== "English aliases"
    ```ragul
    data-filter-filter-sorted-from
    // data → filter → filter → sort → FROM
    ```

=== "Hungarian"
    ```ragul
    data-szűrve-szűrve-rendezve-ból
    // data → filter → filter → sort → FROM
    ```

Multiple `-val` / `-with` arguments bind to aspects in left-to-right order:

=== "English aliases"
    ```ragul
    data-filter-filter-sorted-from  3-above-with  10-below-with  output->  copy-doing.
    // FROM data→filter(>3)→filter(<10)→sort,  INTO output,  AS copy
    ```

=== "Hungarian"
    ```ragul
    data-szűrve-szűrve-rendezve-ból  3-felett-val  10-alatt-val  kimenet-ba  másol-va.
    // FROM data→filter(>3)→filter(<10)→sort,  INTO output,  AS copy
    ```

---

## Suffix Aliases

Each suffix has a canonical Hungarian form plus optional aliases. The parser treats all aliases as identical. Use whichever reads most naturally to you.

| Role | Canonical | English | Symbol |
|---|---|---|---|
| Source (from) | `-ból` / `-ből` | `-from` | `-<` |
| Target (into) | `-ba` / `-be` | `-into` | `->` |
| Instrument (with) | `-val` / `-vel` | `-with` | `-&` |
| Context (at/scope) | `-nál` / `-nél` | `-at` | `-@` |
| Role (acting as) | `-ként` | `-as` | `-:` |
| Object (acted on) | `-t` | `-obj` | `-*` |
| Action (execute) | `-va` / `-ve` | `-doing` | `-!` |
| Error propagation | `-e` | `-else-fail` | `-?` |

Mixed alias usage within the same file is permitted — the parser does not enforce consistency.

---

## Assignment

Assignment is not special syntax — it is an ordinary sentence. The target carries `-be` / `->` (into) and the value carries `-t` / `-obj` (accusative):

=== "English aliases"
    ```ragul
    x->  3-obj.
    lista->  [1, 2, 3]-obj.
    greeting->  "hello"-obj.
    ```

=== "Hungarian"
    ```ragul
    x-be  3-t.
    lista-be  [1, 2, 3]-t.
    üdvözlet-be  "hello"-t.
    ```

`-be` is the front-vowel harmonic variant of `-ba`. Both mean *into* — the choice follows vowel harmony with the root. No type annotation is required — the compiler infers types from the value.

There is no special assignment operator. Assignment is just a sentence where a value flows into a named target.

---

## Comments

Comments begin with `//` and run to the end of the line:

```ragul
// This is a comment
x-be  3-t.   // inline comment
```

---

## Lists

List literals use square brackets with comma-separated elements:

=== "English aliases"
    ```ragul
    lista->  [1, 2, 3]-obj.
    words->  ["alma", "körte", "szilva"]-obj.
    matrix->  [[1,2], [3,4]]-obj.
    ```

=== "Hungarian"
    ```ragul
    lista-be  [1, 2, 3]-t.
    szavak-be  ["alma", "körte", "szilva"]-t.
    mátrix-be  [[1,2], [3,4]]-t.
    ```

---

## Scopes and Indentation

Ragul uses **indentation** (tabs) to define scope boundaries. A new indent level opens a new scope; dedenting closes it.

=== "English aliases"
    ```ragul
    számítás-ours
        x->  3-obj.
        y->  10-obj.
        result->  x-y-add-obj.
        result-from  output->  write-doing.

    // x, y, result do not exist here
    ```

=== "Hungarian"
    ```ragul
    számítás-unk
        x-be  3-t.
        y-be  10-t.
        eredmény-be  x-y-össze-t.
        eredmény-ből  kimenet-be  ír-va.

    // x, y, eredmény do not exist here
    ```

See [Functions & Scopes](functions.md) for the full scoping model.
