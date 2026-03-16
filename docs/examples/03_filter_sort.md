# Filter and Sort

Demonstrates list pipelines — stacking suffixes to filter, deduplicate, sort, and reverse a list in a single chain.

=== "English aliases"
    ```ragul
    program-ours-effect
        numbers-into  [7, 2, 15, 3, 9, 1, 12, 4, 9, 3]-it.

        // Remove duplicates, then sort ascending
        sorted-into   numbers-unique-sorted-it.

        // Keep only numbers greater than 3
        large-into    sorted-3-above-it.

        // Reverse the result
        flipped-into  large-reversed-it.

        numbers-print-doing.
        sorted-print-doing.
        large-print-doing.
        flipped-print-doing.
    ```

=== "Hungarian"
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
numbers-unique-sorted-it
│        │       │
│        │       └── sort the deduplicated list
│        └── remove duplicates from numbers
└── the source list
```

The filter uses an inline literal argument — `3-above` / `3-felett` means "greater than 3":

=== "English aliases"
    ```ragul
    sorted-3-above-it
    //     ^^^^ inline arg passed to -above
    ```

=== "Hungarian"
    ```ragul
    rendezett-3-felett-t
    //         ^^^^ inline arg passed to -felett
    ```

---

## One-liner version

=== "English aliases"
    ```ragul
    result-into  numbers-unique-sorted-3-above-reversed-it.
    // [7, 2, 15, 3, 9, 1, 12, 4, 9, 3]
    // → unique → sort → filter(>3) → reverse
    // = [15, 12, 9, 7, 4]
    ```

=== "Hungarian"
    ```ragul
    eredmény-be  számok-egyedi-rendezve-3-felett-fordítva-t.
    // [7, 2, 15, 3, 9, 1, 12, 4, 9, 3]
    // → unique → sort → filter(>3) → reverse
    // = [15, 12, 9, 7, 4]
    ```

---

## Suffix reference

| Hungarian | English | Effect |
|---|---|---|
| `-egyedi` | `-unique` | Remove duplicates |
| `-rendezve` | `-sorted` | Sort ascending |
| `-fordítva` | `-reversed` | Reverse |
| `-szűrve` | `-filter` | Filter by condition (arg: condition) |
| `-felett` | `-above` | Greater than (produces `Logikai`) |

---

[Download — English](https://github.com/kory75/ragul/blob/master/examples/en/03_filter_sort.ragul) · [Download — Hungarian](https://github.com/kory75/ragul/blob/master/examples/hu/03_filter_sort.ragul)
