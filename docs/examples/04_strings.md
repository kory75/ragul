# String Operations

Demonstrates the string suffix library. String arguments are passed **inline in the chain** — no separate argument syntax needed.

```ragul
program-nk-hatás
    s-be  "Hello, Ragul!"-t.

    // Length
    n-be  s-hossz-t.
    n-képernyőre-va.               // 13

    // Case conversion
    nagy-be  s-nagybetűs-t.
    kis-be   s-kisbetűs-t.
    nagy-képernyőre-va.            // HELLO, RAGUL!
    kis-képernyőre-va.             // hello, ragul!

    // Contains / starts / ends — needle inline in the chain
    van-be   s-"Ragul"-tartalmaz-t.
    kezd-be  s-"Hello"-kezdődik-t.
    vegz-be  s-"!"-végződik-t.
    van-képernyőre-va.             // True
    kezd-képernyőre-va.            // True
    vegz-képernyőre-va.            // True

    // Replace
    uj-be  s-"Ragul"-"world"-csere-t.
    uj-képernyőre-va.              // Hello, world!

    // Split
    szavak-be  s-", "-feloszt-t.
    szavak-képernyőre-va.          // ['Hello', 'Ragul!']

    // Concatenation
    a-be  "Ragul"-t.
    b-be  a-" rocks"-összefűz-t.
    b-képernyőre-va.               // Ragul rocks
```

**Output:**

```
13
HELLO, RAGUL!
hello, ragul!
True
True
True
Hello, world!
['Hello', 'Ragul!']
Ragul rocks
```

---

## Inline string arguments

String arguments are passed directly in the suffix chain, not as separate words:

```ragul
s-"needle"-tartalmaz-t    // does s contain "needle"?
s-"old"-"new"-csere-t     // replace "old" with "new" in s
s-","-feloszt-t           // split s by ","
```

This is consistent with how numeric arguments work (`x-3-össze-t` = add 3).

---

## Suffix reference

| Suffix | Arg(s) | Produces | Description |
|---|---|---|---|
| `-hossz` | — | `Szám` | Length |
| `-nagybetűs` | — | `Szöveg` | Uppercase |
| `-kisbetűs` | — | `Szöveg` | Lowercase |
| `-tartalmaz` | needle | `Logikai` | Contains substring |
| `-kezdődik` | prefix | `Logikai` | Starts with |
| `-végződik` | suffix | `Logikai` | Ends with |
| `-csere` | old, new | `Szöveg` | Replace all occurrences |
| `-feloszt` | separator | `Lista-Szöveg` | Split |
| `-összefűz` | second string | `Szöveg` | Concatenate |

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/04_strings.ragul)
