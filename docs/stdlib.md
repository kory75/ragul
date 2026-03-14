# Standard Library

The standard library is loaded automatically — no import needed. All suffixes below are available in every Ragul program.

---

## Core — Arithmetic

| Suffix | Expects | Arg | Produces | Description |
|---|---|---|---|---|
| `-össze` | `Szám` | `Szám` | `Szám` | Add |
| `-kivon` | `Szám` | `Szám` | `Szám` | Subtract |
| `-szoroz` | `Szám` | `Szám` | `Szám` | Multiply |
| `-oszt` | `Szám` | `Szám` | `Szám` | Divide |
| `-maradék` | `Szám` | `Szám` | `Szám` | Modulo (remainder) |

```ragul
x-be  10-t.
y-be  x-3-össze-t.       // 13
z-be  x-3-szoroz-2-össze-t.  // 32
```

---

## Core — Comparison

| Suffix | Expects | Arg | Produces | Description |
|---|---|---|---|---|
| `-felett` | `Szám` | `Szám` | `Logikai` | Greater than |
| `-alatt` | `Szám` | `Szám` | `Logikai` | Less than |
| `-legalább` | `Szám` | `Szám` | `Logikai` | Greater than or equal |
| `-legfeljebb` | `Szám` | `Szám` | `Logikai` | Less than or equal |
| `-egyenlő` | any | any | `Logikai` | Equality |

---

## Core — Logical

| Suffix | Expects | Arg | Produces | Description |
|---|---|---|---|---|
| `-nem` | `Logikai` | — | `Logikai` | Logical NOT |
| `-és` | `Logikai` | `Logikai` | `Logikai` | Logical AND |
| `-vagy` | `Logikai` | `Logikai` | `Logikai` | Logical OR |

---

## Core — String

| Suffix | Expects | Arg | Produces | Description |
|---|---|---|---|---|
| `-összefűz` | `Szöveg` | `Szöveg` | `Szöveg` | Concatenate strings |

---

## matematika — Math

| Suffix | Expects | Produces | Description |
|---|---|---|---|
| `-négyzetgyök` | `Szám` | `Szám` | Square root |
| `-hatvány` | `Szám` | `Szám` | Power (arg: exponent) |
| `-abszolút` | `Szám` | `Szám` | Absolute value |
| `-kerekítve` | `Szám` | `Szám` | Round to nearest integer |
| `-padló` | `Szám` | `Szám` | Floor |
| `-plafon` | `Szám` | `Szám` | Ceiling |
| `-log` | `Szám` | `Szám` | Natural logarithm |
| `-sin` | `Szám` | `Szám` | Sine (radians) |
| `-cos` | `Szám` | `Szám` | Cosine (radians) |

```ragul
x-be  16-t.
y-be  x-négyzetgyök-t.     // 4.0
z-be  x-hatvány-t  2-val.  // 256
```

---

## szöveg — Strings

| Suffix | Expects | Arg | Produces | Description |
|---|---|---|---|---|
| `-hossz` | `Szöveg` | — | `Szám` | Length |
| `-nagybetűs` | `Szöveg` | — | `Szöveg` | Uppercase |
| `-kisbetűs` | `Szöveg` | — | `Szöveg` | Lowercase |
| `-tartalmaz` | `Szöveg` | `Szöveg` | `Logikai` | Contains substring |
| `-kezdődik` | `Szöveg` | `Szöveg` | `Logikai` | Starts with prefix |
| `-végződik` | `Szöveg` | `Szöveg` | `Logikai` | Ends with suffix |
| `-feloszt` | `Szöveg` | `Szöveg` | `Lista-Szöveg` | Split by separator |
| `-formáz` | `Szám` | — | `Szöveg` | Number to string |
| `-szelet` | `Szöveg` | `Szám`, `Szám` | `Szöveg` | Slice (start, end) |
| `-csere` | `Szöveg` | `Szöveg`, `Szöveg` | `Szöveg` | Replace all occurrences |
| `-számmá` | `Szöveg` | — | `vagy-Szám-vagy-Hiba` | Parse string as number |

```ragul
s-be  "helló világ"-t.
n-be  s-hossz-t.            // 11
u-be  s-nagybetűs-t.        // "HELLÓ VILÁG"
r-be  s-csere-t  "világ"-val  "Ragul"-val.  // "helló Ragul"
```

---

## lista — Lists

| Suffix | Expects | Produces | Description |
|---|---|---|---|
| `-rendezve` | `Lista-T` | `Lista-T` | Sort ascending |
| `-fordítva` | `Lista-T` | `Lista-T` | Reverse |
| `-első` | `Lista-T` | `T` | First element |
| `-utolsó` | `Lista-T` | `T` | Last element |
| `-egyedi` | `Lista-T` | `Lista-T` | Remove duplicates |
| `-lapítva` | `Lista-Lista-T` | `Lista-T` | Flatten one level |
| `-szűrve` | `Lista-T` | `Lista-T` | Filter (arg: condition) |
| `-hozzáad` | `Lista-T` | `Lista-T` | Append element (arg: element) |
| `-eltávolít` | `Lista-T` | `Lista-T` | Remove element (arg: element) |
| `-hossz` | `Lista-T` | `Szám` | Length |

```ragul
lista-be  [3, 1, 4, 1, 5, 9, 2, 6]-t.
rendezett-be  lista-rendezve-egyedi-t.     // [1, 2, 3, 4, 5, 6, 9]
nagy-be  lista-szűrve-ből  5-felett-val  t. // [9, 6]
```

---

## Bridge Suffixes

Bridge suffixes convert between types and must be used when chaining across type boundaries:

| Suffix | From | To | Fallible |
|---|---|---|---|
| `-szöveggé` | `Szám` | `Szöveg` | No |
| `-számmá` | `Szöveg` | `vagy-Szám-vagy-Hiba` | Yes |

```ragul
x-be  42-t.
s-be  x-szöveggé-t.         // "42"

n-be  "123"-számmá-va-e.    // 123, or propagate error
```
