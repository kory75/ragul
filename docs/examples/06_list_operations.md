# List Operations

Demonstrates the full list suffix library — sorting, filtering, reversing, slicing, and modifying lists.

=== "English aliases"
    ```ragul
    program-ours-effect
        numbers-into  [7, 2, 15, 3, 9, 1, 12, 4, 9, 3]-it.

        // Sort ascending
        sorted-into   numbers-sorted-it.
        sorted-print-doing.            // [1, 2, 3, 3, 4, 7, 9, 9, 12, 15]

        // Remove duplicates
        unique-into   numbers-unique-it.
        unique-print-doing.            // [7, 2, 15, 3, 9, 1, 12, 4]

        // Sort + deduplicate pipeline
        clean-into    numbers-unique-sorted-it.
        clean-print-doing.             // [1, 2, 3, 4, 7, 9, 12, 15]

        // Reverse
        flipped-into  sorted-reversed-it.
        flipped-print-doing.           // [15, 12, 9, 9, 7, 4, 3, 3, 2, 1]

        // Filter — condition inline in the chain
        large-into    sorted-3-above-it.
        large-print-doing.             // [4, 7, 9, 9, 12, 15]

        // First and last
        first_num-into  sorted-first-it.
        last_num-into   sorted-last-it.
        first_num-print-doing.         // 1
        last_num-print-doing.          // 15

        // Length
        count-into  numbers-len-it.
        count-print-doing.             // 10

        // Add and remove elements
        extended-into  sorted-append-it  100-with.
        extended-print-doing.          // [1, 2, 3, 3, 4, 7, 9, 9, 12, 15, 100]

        reduced-into   sorted-remove-it  1-with.
        reduced-print-doing.           // [2, 3, 3, 4, 7, 9, 9, 12, 15]
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        szamok-be  [7, 2, 15, 3, 9, 1, 12, 4, 9, 3]-t.

        // Sort ascending
        rendezett-be  szamok-rendezve-t.
        rendezett-képernyőre-va.       // [1, 2, 3, 3, 4, 7, 9, 9, 12, 15]

        // Remove duplicates
        egyedi-be  szamok-egyedi-t.
        egyedi-képernyőre-va.          // [7, 2, 15, 3, 9, 1, 12, 4]

        // Sort + deduplicate pipeline
        tiszta-be  szamok-egyedi-rendezve-t.
        tiszta-képernyőre-va.          // [1, 2, 3, 4, 7, 9, 12, 15]

        // Reverse
        fordított-be  rendezett-fordítva-t.
        fordított-képernyőre-va.       // [15, 12, 9, 9, 7, 4, 3, 3, 2, 1]

        // Filter — condition inline in the chain
        nagyok-be  rendezett-3-felett-t.
        nagyok-képernyőre-va.          // [4, 7, 9, 9, 12, 15]

        // First and last
        elso-be   rendezett-első-t.
        utolso-be rendezett-utolsó-t.
        elso-képernyőre-va.            // 1
        utolso-képernyőre-va.          // 15

        // Length
        hossz-be  szamok-hossz-t.
        hossz-képernyőre-va.           // 10

        // Add and remove elements
        bovített-be  rendezett-hozzáad-t  100-val.
        bovített-képernyőre-va.        // [1, 2, 3, 3, 4, 7, 9, 9, 12, 15, 100]

        csökkentett-be  rendezett-eltávolít-t  1-val.
        csökkentett-képernyőre-va.     // [2, 3, 3, 4, 7, 9, 9, 12, 15]
    ```

**Output:**

```
[1, 2, 3, 3, 4, 7, 9, 9, 12, 15]
[7, 2, 15, 3, 9, 1, 12, 4]
[1, 2, 3, 4, 7, 9, 12, 15]
[15, 12, 9, 9, 7, 4, 3, 3, 2, 1]
[4, 7, 9, 9, 12, 15]
1
15
10
[1, 2, 3, 3, 4, 7, 9, 9, 12, 15, 100]
[2, 3, 3, 4, 7, 9, 9, 12, 15]
```

---

## Chaining transformations

List suffixes can be stacked into arbitrarily long pipelines:

=== "English aliases"
    ```ragul
    // Remove duplicates, sort, keep > 5, reverse — all in one chain
    result-into  numbers-unique-sorted-5-above-reversed-it.
    ```

=== "Hungarian"
    ```ragul
    // Remove duplicates, sort, keep > 5, reverse — all in one chain
    eredmény-be  szamok-egyedi-rendezve-5-felett-fordítva-t.
    ```

The type system ensures each suffix in the chain receives the right element type. A `Lista-Szám` can use `-felett` / `-above`; a `Lista-Szöveg` cannot.

---

## Suffix reference

| Hungarian | English | Arg | Produces | Description |
|---|---|---|---|---|
| `-rendezve` | `-sorted` | — | `Lista-T` | Sort ascending |
| `-fordítva` | `-reversed` | — | `Lista-T` | Reverse |
| `-egyedi` | `-unique` | — | `Lista-T` | Remove duplicates |
| `-első` | `-first` | — | `T` | First element |
| `-utolsó` | `-last` | — | `T` | Last element |
| `-hossz` | `-len` | — | `Szám` | Length |
| `-hozzáad` | `-append` | element | `Lista-T` | Append element |
| `-eltávolít` | `-remove` | element | `Lista-T` | Remove first occurrence |
| `-lapítva` | `-flat` | — | `Lista-T` | Flatten one level |

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/06_list_operations.ragul)
