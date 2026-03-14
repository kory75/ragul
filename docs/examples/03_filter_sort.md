# Filter and Sort

Demonstrates list pipelines — stacking suffixes to filter, deduplicate, sort, and reverse a list in a single chain.

```ragul
program-nk-hatás
    számok-be  [7, 2, 15, 3, 9, 1, 12, 4, 9, 3]-t.

    // Remove duplicates, then sort ascending
    rendezett-be  számok-egyedi-rendezve-t.

    // Keep only numbers greater than 3
    nagyok-be  rendezett-3-felett-t.

    // Reverse the result
    fordított-be  nagyok-fordítva-t.

    számok-képernyőre-va.
    rendezett-képernyőre-va.
    nagyok-képernyőre-va.
    fordított-képernyőre-va.
```

**Output:**

```
[7, 2, 15, 3, 9, 1, 12, 4, 9, 3]
[1, 2, 3, 4, 7, 9, 12, 15]
[4, 7, 9, 12, 15]
[15, 12, 9, 7, 4]
```

---

## How the pipeline works

Each suffix in the chain transforms the result of the previous:

```
számok-egyedi-rendezve-t
│        │       │
│        │       └── sort the deduplicated list
│        └── remove duplicates from számok
└── the source list
```

The filter uses an inline literal argument — `3-felett` means "greater than 3":

```ragul
rendezett-3-felett-t
//         ^^^^ inline arg passed to -felett
```

---

## One-liner version

The entire pipeline can be written as a single chain:

```ragul
eredmény-be  számok-egyedi-rendezve-3-felett-fordítva-t.
// [7, 2, 15, 3, 9, 1, 12, 4, 9, 3]
// → unique → sort → filter(>3) → reverse
// = [15, 12, 9, 7, 4]
```

---

## Suffix reference

| Suffix | Effect |
|---|---|
| `-egyedi` | Remove duplicates |
| `-rendezve` | Sort ascending |
| `-fordítva` | Reverse |
| `-szűrve` | Filter by condition (arg: condition) |
| `-felett` | Greater than (produces `Logikai`) |

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/03_filter_sort.ragul)
