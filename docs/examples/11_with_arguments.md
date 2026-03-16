# -with / -val Arguments

Explains and demonstrates Ragul's **instrument suffix** (`-val` / `-with` / `-&`), which supplies an extra argument to a suffix from a separate word in the sentence.

---

## Inline vs. sentence-level arguments

There are two ways to pass an argument to a suffix:

| Form | Example | When to use |
|---|---|---|
| **Inline** (baked into the chain) | `s-"Hello"-contains-it` | The argument is a literal known at write time |
| **`-with`** (separate sentence word) | `s-contains-it  word-with.` | The argument is a variable, computed value, or too long to inline |

Both forms are semantically identical — the choice is purely about readability.

---

## 1. Arithmetic with a variable argument

=== "English aliases"
    ```ragul
    program-ours-effect
        base-into  10-it.
        step-into  3-it.

        // Inline: argument baked into the chain
        a-into  base-3-add-it.
        a-print-doing.                 // 13

        // -with: argument supplied from a variable
        b-into  base-add-it  step-with.
        b-print-doing.                 // 13
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        alap-ba  10-t.
        lepes-ba  3-t.

        // Inline: az argumentum a láncba sütve
        a-ba  alap-3-össze-t.
        a-képernyőre-va.               // 13

        // -val: az argumentum önálló változóból
        b-ba  alap-össze-t  lepes-val.
        b-képernyőre-va.               // 13
    ```

---

## 2. String operations

Multiple `-with` arguments are consumed left-to-right by the suffixes that need them.

=== "English aliases"
    ```ragul
    program-ours-effect
        sentence-into  "Hello, Ragul!"-it.
        sep-into       ", "-it.

        // Contains — search term from a variable
        word-into   "Ragul"-it.
        found-into  sentence-contains-it  word-with.
        found-print-doing.             // True

        // Split — separator from a variable
        parts-into  sentence-split-it  sep-with.
        parts-print-doing.             // ['Hello', 'Ragul!']

        // Replace — two -with arguments in sequence
        old_word-into  "Ragul"-it.
        new_word-into  "world"-it.
        changed-into  sentence-replace-it  old_word-with  new_word-with.
        changed-print-doing.           // Hello, world!
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        mondat-ba  "Szia, Ragul!"-t.
        elvalaszto-ba  ", "-t.

        // Tartalmaz — a keresett szó változóból
        szoveg-ba  "Ragul"-t.
        van-ba  mondat-tartalmaz-t  szoveg-val.
        van-képernyőre-va.             // True

        // Szétválasztás — az elválasztó változóból
        szavak-ba  mondat-feloszt-t  elvalaszto-val.
        szavak-képernyőre-va.          // ['Szia', 'Ragul!']

        // Csere — két -val argumentum egymás után
        regi-ba  "Ragul"-t.
        uj-ba    "világ"-t.
        modositott-ba  mondat-csere-t  regi-val  uj-val.
        modositott-képernyőre-va.      // Szia, világ!
    ```

---

## 3. User-defined scopes with multiple parameters

When a scope is called as a suffix, the first `-yours` (`-d`) parameter receives the piped-in value; all subsequent parameters receive `-with` arguments left-to-right.

=== "English aliases"
    ```ragul
    multiply-ours
        x-yours.
        y-yours.
        x-y-mul-it.

    program-ours-effect
        result-into  5-multiply-it  6-with.
        result-print-doing.            // 30
    ```

=== "Hungarian"
    ```ragul
    szorzat-unk
        x-d.
        y-d.
        x-y-szoroz-t.

    program-nk-hatás
        eredmeny-ba  5-szorzat-t  6-val.
        eredmeny-képernyőre-va.        // 30
    ```

---

## 4. Fold (reduce) with an initial accumulator

A `-fold` (`-gyűjt`) scope reduces a list to a single value. The **initial accumulator** is supplied as the first `-with` argument in the calling sentence.

The scope receives two `-yours` parameters: the first is the accumulator, the second is the current element.

=== "English aliases"
    ```ragul
    sum_fold-ours-fold
        accumulated-yours.
        item-yours.
        accumulated-item-add-it.

    program-ours-effect
        numbers-into  [1, 2, 3, 4, 5]-it.

        total-into   numbers-sum_fold-it  0-with.
        total-print-doing.             // 15

        offset-into  numbers-sum_fold-it  100-with.
        offset-print-doing.            // 115
    ```

=== "Hungarian"
    ```ragul
    osszead-unk-gyűjt
        felhalmozott-d.
        elem-d.
        felhalmozott-elem-össze-t.

    program-nk-hatás
        szamok-ba  [1, 2, 3, 4, 5]-t.

        osszeg-ba   szamok-osszead-t  0-val.
        osszeg-képernyőre-va.          // 15

        eltolt-ba  szamok-osszead-t  100-val.
        eltolt-képernyőre-va.          // 115
    ```

**Output:**

```
13
13
True
['Hello', 'Ragul!']
Hello, world!
30
15
115
```

---

## Suffix aliases

| Canonical | English alias | Symbol |
|---|---|---|
| `-val` / `-vel` | `-with` | `-&` |

The front-vowel harmonic variant `-vel` is accepted anywhere `-val` appears (vowel harmony with the root).

---

## Key rules

- `-with` words are consumed **left-to-right** by suffixes that need arguments, in chain order.
- An inline argument (e.g. `-3-add`) and a `-with` argument fill the same slot — they are interchangeable for numeric and string literals.
- For fold scopes, the possession order in the scope header is `name-ours-fold` (`-unk-gyűjt`), not `name-fold-ours`.

---

[Download — English](https://github.com/kory75/ragul/blob/master/examples/en/11_with_arguments.ragul) · [Download — Hungarian](https://github.com/kory75/ragul/blob/master/examples/hu/11_val_argumentumok.ragul)
