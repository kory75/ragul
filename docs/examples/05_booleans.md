# Booleans & Comparisons

Demonstrates comparison operators and logical combinators. Comparisons produce `Logikai` (boolean) values — `true`/`igaz` or `false`/`hamis` — which can be stored, printed, and combined.

=== "English aliases"
    ```ragul
    program-ours-effect
        x-into  10-it.
        y-into  3-it.

        // Comparisons — produce Logikai values
        greater-into  x-y-above-it.        // 10 > 3   = True
        lesser-into   x-y-below-it.        // 10 < 3   = False
        at_least-into x-10-atleast-it.     // 10 >= 10 = True
        equal-into    x-10-eq-it.          // 10 == 10 = True

        greater-print-doing.             // True
        lesser-print-doing.              // False
        at_least-print-doing.            // True
        equal-print-doing.               // True

        // Logical operators
        p-into  true-it.
        q-into  false-it.

        and_res-into  p-q-and-it.          // True AND False = False
        or_res-into   p-q-or-it.           // True OR False  = True
        not_res-into  p-not-it.            // NOT True       = False

        and_res-print-doing.             // False
        or_res-print-doing.              // True
        not_res-print-doing.             // False

        // Combining two comparisons
        cmp1-into  x-y-above-it.           // 10 > 3   = True
        cmp2-into  x-10-atleast-it.        // 10 >= 10 = True
        both-into  cmp1-cmp2-and-it.       // True AND True = True
        both-print-doing.                // True
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        x-be  10-t.
        y-be  3-t.

        // Comparisons — produce Logikai values
        nagyobb-be   x-y-felett-t.       // 10 > 3   = igaz
        kisebb-be    x-y-alatt-t.        // 10 < 3   = hamis
        legalabb-be  x-10-legalább-t.    // 10 >= 10 = igaz
        egyenlo-be   x-10-egyenlő-t.     // 10 == 10 = igaz

        nagyobb-képernyőre-va.           // True
        kisebb-képernyőre-va.            // False
        legalabb-képernyőre-va.          // True
        egyenlo-képernyőre-va.           // True

        // Logical operators
        p-be  igaz-t.
        q-be  hamis-t.

        es-be    p-q-és-t.               // True AND False = False
        vagy-be  p-q-vagy-t.             // True OR False  = True
        nem-be   p-nem-t.                // NOT True       = False

        es-képernyőre-va.                // False
        vagy-képernyőre-va.              // True
        nem-képernyőre-va.               // False

        // Combining two comparisons
        cmp1-be  x-y-felett-t.           // 10 > 3   = True
        cmp2-be  x-10-legalább-t.        // 10 >= 10 = True
        mindketto-be  cmp1-cmp2-és-t.    // True AND True = True
        mindketto-képernyőre-va.         // True
    ```

**Output:**

```
True
False
True
True
False
True
False
True
```

---

## How comparisons work

Comparison suffixes take an inline argument and return a `Logikai`:

=== "English aliases"
    ```ragul
    x-5-above-it    // is x > 5?
    x-5-below-it    // is x < 5?
    x-5-atleast-it  // is x >= 5?
    x-5-atmost-it   // is x <= 5?
    x-5-eq-it       // is x == 5?
    ```

=== "Hungarian"
    ```ragul
    x-5-felett-t     // is x > 5?
    x-5-alatt-t      // is x < 5?
    x-5-legalább-t   // is x >= 5?
    x-5-legfeljebb-t // is x <= 5?
    x-5-egyenlő-t    // is x == 5?
    ```

The argument can also be a variable: `x-y-above-it` means "is x > y?".

!!! note "Boolean literals"
    `true` and `false` are English aliases for `igaz` and `hamis`. Both forms are accepted
    and normalised at lex time — the interpreter always sees the canonical Hungarian keywords.

---

## Suffix reference

| Hungarian | English | Expects | Produces | Description |
|---|---|---|---|---|
| `-felett` | `-above` | `Szám` | `Logikai` | Greater than |
| `-alatt` | `-below` | `Szám` | `Logikai` | Less than |
| `-legalább` | `-atleast` | `Szám` | `Logikai` | Greater than or equal |
| `-legfeljebb` | `-atmost` | `Szám` | `Logikai` | Less than or equal |
| `-egyenlő` | `-eq` | any | `Logikai` | Equality |
| `-és` | `-and` | `Logikai` | `Logikai` | Logical AND |
| `-vagy` | `-or` | `Logikai` | `Logikai` | Logical OR |
| `-nem` | `-not` | — | `Logikai` | Logical NOT |

---

[Download — English](https://github.com/kory75/ragul/blob/master/examples/en/05_booleans.ragul) · [Download — Hungarian](https://github.com/kory75/ragul/blob/master/examples/hu/05_booleans.ragul)
