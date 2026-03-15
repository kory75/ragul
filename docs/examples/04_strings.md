# String Operations

Demonstrates the string suffix library. String arguments are passed **inline in the chain** — no separate argument syntax needed.

=== "English aliases"
    ```ragul
    program-ours-effect
        s->  "Hello, Ragul!"-it.

        // Length
        n->  s-len-it.
        n-print-doing.                 // 13

        // Case conversion
        upper->  s-upper-it.
        lower->  s-lower-it.
        upper-print-doing.             // HELLO, RAGUL!
        lower-print-doing.             // hello, ragul!

        // Contains / starts / ends — needle inline in the chain
        has->    s-"Ragul"-contains-it.
        starts-> s-"Hello"-startswith-it.
        ends->   s-"!"-endswith-it.
        has-print-doing.               // True
        starts-print-doing.            // True
        ends-print-doing.              // True

        // Replace
        new_str->  s-"Ragul"-"world"-replace-it.
        new_str-print-doing.           // Hello, world!

        // Split
        words->  s-", "-split-it.
        words-print-doing.             // ['Hello', 'Ragul!']

        // Concatenation
        a->  "Ragul"-it.
        b->  a-" rocks"-concat-it.
        b-print-doing.                 // Ragul rocks
    ```

=== "Hungarian"
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

=== "English aliases"
    ```ragul
    s-"needle"-contains-it    // does s contain "needle"?
    s-"old"-"new"-replace-it  // replace "old" with "new" in s
    s-","-split-it            // split s by ","
    ```

=== "Hungarian"
    ```ragul
    s-"needle"-tartalmaz-t    // does s contain "needle"?
    s-"old"-"new"-csere-t     // replace "old" with "new" in s
    s-","-feloszt-t           // split s by ","
    ```

This is consistent with how numeric arguments work (`x-3-add-it` = add 3).

---

## Suffix reference

| Hungarian | English | Arg(s) | Produces | Description |
|---|---|---|---|---|
| `-hossz` | `-len` | — | `Szám` | Length |
| `-nagybetűs` | `-upper` | — | `Szöveg` | Uppercase |
| `-kisbetűs` | `-lower` | — | `Szöveg` | Lowercase |
| `-tartalmaz` | `-contains` | needle | `Logikai` | Contains substring |
| `-kezdődik` | `-startswith` | prefix | `Logikai` | Starts with |
| `-végződik` | `-endswith` | suffix | `Logikai` | Ends with |
| `-csere` | `-replace` | old, new | `Szöveg` | Replace all occurrences |
| `-feloszt` | `-split` | separator | `Lista-Szöveg` | Split |
| `-összefűz` | `-concat` | second string | `Szöveg` | Concatenate |

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/04_strings.ragul)
