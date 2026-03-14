# Arithmetic

Demonstrates arithmetic operations and suffix chaining. Each suffix in a chain operates on the result of the previous one — building a left-to-right pipeline inside a single word.

```ragul
program-nk-hatás
    x-be  10-t.
    y-be  3-t.

    // Basic operations
    ossz-be       x-y-össze-t.       // 10 + 3  = 13
    kulonbseg-be  x-y-kivon-t.       // 10 - 3  = 7
    szorzat-be    x-y-szoroz-t.      // 10 * 3  = 30
    hanyados-be   x-y-oszt-t.        // 10 / 3  = 3.33
    maradek-be    x-y-maradék-t.     // 10 mod 3 = 1

    ossz-képernyőre-va.
    kulonbseg-képernyőre-va.
    szorzat-képernyőre-va.
    hanyados-képernyőre-va.
    maradek-képernyőre-va.

    // Chained pipeline: (10 + 3) * 2 = 26
    lanc-be  x-3-össze-2-szoroz-t.
    lanc-képernyőre-va.

    // Math suffixes
    gyok-be     16-négyzetgyök-t.    // sqrt(16) = 4.0
    hatvany-be   2-10-hatvány-t.     // 2^10 = 1024

    // Absolute value via subtraction then abs
    negativ-be  0-7-kivon-t.         // 0 - 7 = -7
    abs-be      negativ-abszolút-t.  // |-7| = 7

    gyok-képernyőre-va.
    hatvany-képernyőre-va.
    abs-képernyőre-va.
```

**Output:**

```
13
7
30
3.3333333333333335
1
26
4.0
1024
7
```

---

## Key concepts

**Inline literal arguments** — numeric literals in the suffix chain are consumed as arguments by the next suffix:

```ragul
x-3-össze-t      // x + 3
x-3-össze-2-szoroz-t  // (x + 3) × 2
```

**Variable references in chains** — a root name in the chain looks up that variable's value:

```ragul
x-y-össze-t      // x + y
x-y-kivon-t      // x - y
```

**Suffix reference**

| Suffix | Operation |
|---|---|
| `-össze` | Add |
| `-kivon` | Subtract |
| `-szoroz` | Multiply |
| `-oszt` | Divide |
| `-maradék` | Modulo |
| `-négyzetgyök` | Square root |
| `-hatvány` | Power (arg: exponent) |
| `-abszolút` | Absolute value |

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/02_arithmetic.ragul)
