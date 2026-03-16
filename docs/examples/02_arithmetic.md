# Arithmetic

Demonstrates arithmetic operations and suffix chaining. Each suffix in a chain operates on the result of the previous one — building a left-to-right pipeline inside a single word.

=== "English aliases"
    ```ragul
    program-ours-effect
        x-into  10-it.
        y-into  3-it.

        // Basic operations
        sum-into      x-y-add-it.       // 10 + 3  = 13
        diff-into     x-y-sub-it.       // 10 - 3  = 7
        product-into  x-y-mul-it.       // 10 * 3  = 30
        quotient-into x-y-div-it.       // 10 / 3  = 3.33
        rem-into      x-y-rem-it.       // 10 mod 3 = 1

        sum-print-doing.
        diff-print-doing.
        product-print-doing.
        quotient-print-doing.
        rem-print-doing.

        // Chained pipeline: (10 + 3) * 2 = 26
        chain-into  x-3-add-2-mul-it.
        chain-print-doing.

        // Math suffixes
        root-into   16-sqrt-it.         // sqrt(16) = 4.0
        power-into  2-10-pow-it.        // 2^10 = 1024

        // Absolute value via subtraction then abs
        negative-into  0-7-sub-it.      // 0 - 7 = -7
        absval-into    negative-abs-it. // |-7| = 7

        root-print-doing.
        power-print-doing.
        absval-print-doing.
    ```

=== "Hungarian"
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

=== "English aliases"
    ```ragul
    x-3-add-it          // x + 3
    x-3-add-2-mul-it    // (x + 3) × 2
    ```

=== "Hungarian"
    ```ragul
    x-3-össze-t          // x + 3
    x-3-össze-2-szoroz-t // (x + 3) × 2
    ```

**Variable references in chains** — a root name in the chain looks up that variable's value:

=== "English aliases"
    ```ragul
    x-y-add-it  // x + y
    x-y-sub-it  // x - y
    ```

=== "Hungarian"
    ```ragul
    x-y-össze-t  // x + y
    x-y-kivon-t  // x - y
    ```

**Suffix reference**

| Hungarian | English | Operation |
|---|---|---|
| `-össze` | `-add` | Add |
| `-kivon` | `-sub` | Subtract |
| `-szoroz` | `-mul` | Multiply |
| `-oszt` | `-div` | Divide |
| `-maradék` | `-rem` | Modulo |
| `-négyzetgyök` | `-sqrt` | Square root |
| `-hatvány` | `-pow` | Power (arg: exponent) |
| `-abszolút` | `-abs` | Absolute value |

---

[Download — English](https://github.com/kory75/ragul/blob/master/examples/en/02_arithmetic.ragul) · [Download — Hungarian](https://github.com/kory75/ragul/blob/master/examples/hu/02_arithmetic.ragul)
