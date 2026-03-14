# Booleans & Comparisons

Demonstrates comparison operators and logical combinators. Comparisons produce `Logikai` (boolean) values — `igaz` (true) or `hamis` (false) — which can be stored, printed, and combined.

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

    es-be   p-q-és-t.                // True AND False = False
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

```ragul
x-5-felett-t    // is x > 5?
x-5-alatt-t     // is x < 5?
x-5-legalább-t  // is x >= 5?
x-5-legfeljebb-t // is x <= 5?
x-5-egyenlő-t   // is x == 5?
```

The argument can also be a variable:

```ragul
x-y-felett-t    // is x > y?
```

---

## Suffix reference

| Suffix | Expects | Produces | Description |
|---|---|---|---|
| `-felett` | `Szám` | `Logikai` | Greater than |
| `-alatt` | `Szám` | `Logikai` | Less than |
| `-legalább` | `Szám` | `Logikai` | Greater than or equal |
| `-legfeljebb` | `Szám` | `Logikai` | Less than or equal |
| `-egyenlő` | any | `Logikai` | Equality |
| `-és` | `Logikai` | `Logikai` | Logical AND |
| `-vagy` | `Logikai` | `Logikai` | Logical OR |
| `-nem` | — | `Logikai` | Logical NOT |

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/05_booleans.ragul)
