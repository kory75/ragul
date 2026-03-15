# Hello World

The simplest Ragul program — assign a string and print it.

=== "English aliases"
    ```ragul
    program-ours-effect
        greeting->  "Hello, World!"-it.
        greeting-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        üdvözlet-be  "Helló, világ!"-t.
        üdvözlet-képernyőre-va.
    ```

**Run it:**

```bash
ragul run examples/01_hello.ragul
# or
ragul futtat examples/01_hello.ragul
```

**Output:**

```
Hello, World!
```

---

## What's happening

- `program-ours-effect` (`program-nk-hatás`) — declares an effect scope named `program`. The `-effect` / `-hatás` suffix marks it as eager: everything inside executes in order, top to bottom.
- `greeting->  "Hello, World!"-it.` — assigns the string into the root `greeting`. The compiler infers type `Szöveg` (string).
- `greeting-print-doing.` — pipes `greeting` to the `-print` (`képernyőre`) channel and executes it with `-doing` (`-va`).

---

## Variation — with concatenation

=== "English aliases"
    ```ragul
    program-ours-effect
        name->     "Ragul"-it.
        greeting-> "Hello, "-it.
        output->   greeting-name-concat-it.
        output-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        név-be  "Ragul"-t.
        üdvözlet-be  "Helló, "-t.
        kimenet-be  üdvözlet-név-összefűz-t.
        kimenet-képernyőre-va.
    ```

**Output:**

```
Hello, Ragul
```

The `-concat` / `-összefűz` suffix concatenates two strings. The second string is passed inline in the chain: `greeting-name-concat-it` reads as *"greeting, concatenated with name"*.

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/01_hello.ragul)
