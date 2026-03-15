# Standard Library

The standard library is loaded automatically — no import needed. All suffixes below are available in every Ragul program.

---

## Core — Arithmetic

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-össze` | `-add` | `Szám` | `Szám` | `Szám` | Add |
| `-kivon` | `-sub` | `Szám` | `Szám` | `Szám` | Subtract |
| `-szoroz` | `-mul` | `Szám` | `Szám` | `Szám` | Multiply |
| `-oszt` | `-div` | `Szám` | `Szám` | `Szám` | Divide |
| `-maradék` | `-rem` | `Szám` | `Szám` | `Szám` | Modulo (remainder) |

=== "English aliases"
    ```ragul
    x->  10-it.
    y->  x-3-add-it.            // 13
    z->  x-3-mul-2-add-it.      // 32
    ```

=== "Hungarian"
    ```ragul
    x-be  10-t.
    y-be  x-3-össze-t.           // 13
    z-be  x-3-szoroz-2-össze-t.  // 32
    ```

---

## Core — Comparison

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-felett` | `-above` | `Szám` | `Szám` | `Logikai` | Greater than |
| `-alatt` | `-below` | `Szám` | `Szám` | `Logikai` | Less than |
| `-legalább` | `-atleast` | `Szám` | `Szám` | `Logikai` | Greater than or equal |
| `-legfeljebb` | `-atmost` | `Szám` | `Szám` | `Logikai` | Less than or equal |
| `-egyenlő` | `-eq` | any | any | `Logikai` | Equality |
| `-nemegyenlő` | `-neq` | any | any | `Logikai` | Not equal |

---

## Core — Logical

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-nem` | `-not` | `Logikai` | — | `Logikai` | Logical NOT |
| `-és` | `-and` | `Logikai` | `Logikai` | `Logikai` | Logical AND |
| `-vagy` | `-or` | `Logikai` | `Logikai` | `Logikai` | Logical OR |

---

## Core — String

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-összefűz` | `-concat` | `Szöveg` | `Szöveg` | `Szöveg` | Concatenate strings |

---

## matematika — Math

| Hungarian | English | Expects | Produces | Description |
|---|---|---|---|---|
| `-négyzetgyök` | `-sqrt` | `Szám` | `Szám` | Square root |
| `-hatvány` | `-pow` | `Szám` | `Szám` | Power (arg: exponent) |
| `-abszolút` | `-abs` | `Szám` | `Szám` | Absolute value |
| `-kerekítve` | `-round` | `Szám` | `Szám` | Round to nearest integer |
| `-padló` | `-floor` | `Szám` | `Szám` | Floor |
| `-plafon` | `-ceil` | `Szám` | `Szám` | Ceiling |
| `-log` | `-log` | `Szám` | `Szám` | Logarithm (arg: base) |
| `-sin` | `-sin` | `Szám` | `Szám` | Sine (radians) |
| `-cos` | `-cos` | `Szám` | `Szám` | Cosine (radians) |

=== "English aliases"
    ```ragul
    x->  16-it.
    y->  x-sqrt-it.           // 4.0
    z->  x-pow-it  2-with.    // 256
    ```

=== "Hungarian"
    ```ragul
    x-be  16-t.
    y-be  x-négyzetgyök-t.     // 4.0
    z-be  x-hatvány-t  2-val.  // 256
    ```

---

## szöveg — Strings

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-hossz` | `-len` | `Szöveg` | — | `Szám` | Length |
| `-nagybetűs` | `-upper` | `Szöveg` | — | `Szöveg` | Uppercase |
| `-kisbetűs` | `-lower` | `Szöveg` | — | `Szöveg` | Lowercase |
| `-tartalmaz` | `-contains` | `Szöveg` | `Szöveg` | `Logikai` | Contains substring |
| `-kezdődik` | `-startswith` | `Szöveg` | `Szöveg` | `Logikai` | Starts with prefix |
| `-végződik` | `-endswith` | `Szöveg` | `Szöveg` | `Logikai` | Ends with suffix |
| `-feloszt` | `-split` | `Szöveg` | `Szöveg` | `Lista-Szöveg` | Split by separator |
| `-formáz` | `-format` | `Szöveg` | any | `Szöveg` | Format string (`{}` placeholder) |
| `-szelet` | `-slice` | `Szöveg` | `Szám`, `Szám` | `Szöveg` | Slice (start, end) |
| `-csere` | `-replace` | `Szöveg` | `Szöveg`, `Szöveg` | `Szöveg` | Replace all occurrences |
| `-számmá` | `-tonum` | `Szöveg` | — | `vagy-Szám-vagy-Hiba` | Parse string as number |

=== "English aliases"
    ```ragul
    s->  "helló világ"-it.
    n->  s-len-it.             // 11
    u->  s-upper-it.           // "HELLÓ VILÁG"
    r->  s-replace-it  "világ"-with  "Ragul"-with.  // "helló Ragul"
    ```

=== "Hungarian"
    ```ragul
    s-be  "helló világ"-t.
    n-be  s-hossz-t.            // 11
    u-be  s-nagybetűs-t.        // "HELLÓ VILÁG"
    r-be  s-csere-t  "világ"-val  "Ragul"-val.  // "helló Ragul"
    ```

---

## lista — Lists

| Hungarian | English | Expects | Produces | Description |
|---|---|---|---|---|
| `-rendezve` | `-sorted` | `Lista-T` | `Lista-T` | Sort ascending |
| `-fordítva` | `-reversed` | `Lista-T` | `Lista-T` | Reverse |
| `-első` | `-first` | `Lista-T` | `T` | First element |
| `-utolsó` | `-last` | `Lista-T` | `T` | Last element |
| `-egyedi` | `-unique` | `Lista-T` | `Lista-T` | Remove duplicates |
| `-lapítva` | `-flat` | `Lista-Lista-T` | `Lista-T` | Flatten one level |
| `-szűrve` | `-filter` | `Lista-T` | `Lista-T` | Filter (arg: condition) |
| `-hozzáad` | `-append` | `Lista-T` | `Lista-T` | Append element (arg: element) |
| `-eltávolít` | `-remove` | `Lista-T` | `Lista-T` | Remove element (arg: element) |
| `-hossz` | `-len` | `Lista-T` | `Szám` | Length |
| `-tartalmaz` | `-contains` | `Lista-T` | `Logikai` | Contains element |

=== "English aliases"
    ```ragul
    lista->  [3, 1, 4, 1, 5, 9, 2, 6]-it.
    sorted->  lista-sorted-unique-it.          // [1, 2, 3, 4, 5, 6, 9]
    large->  lista-filter-from  5-above-with  obj. // [9, 6]
    ```

=== "Hungarian"
    ```ragul
    lista-be  [3, 1, 4, 1, 5, 9, 2, 6]-t.
    rendezett-be  lista-rendezve-egyedi-t.      // [1, 2, 3, 4, 5, 6, 9]
    nagy-be  lista-szűrve-ből  5-felett-val  t. // [9, 6]
    ```

---

## Bridge Suffixes

Bridge suffixes convert between types and must be used when chaining across type boundaries:

| Hungarian | English | From | To | Fallible |
|---|---|---|---|---|
| `-szöteggé` | `-tostr` | `Szám` | `Szöveg` | No |
| `-számmá` | `-tonum` | `Szöveg` | `vagy-Szám-vagy-Hiba` | Yes |

=== "English aliases"
    ```ragul
    x->  42-it.
    s->  x-tostr-it.           // "42"

    n->  "123"-tonum-doing-?.   // 123, or propagate error
    ```

=== "Hungarian"
    ```ragul
    x-be  42-t.
    s-be  x-szöteggé-t.         // "42"

    n-be  "123"-számmá-va-e.    // 123, or propagate error
    ```
