# Hello World

The simplest Ragul program — assign a string and print it.

=== "Hungarian"
    ```ragul
    program-nk-hatás
        üdvözlet-be  "Helló, világ!"-t.
        üdvözlet-képernyőre-va.
    ```

=== "English aliases"
    ```ragul
    program-ours-effect
        greeting->  "Hello, World!"-obj.
        greeting-print-doing.
    ```

**Run it:**

```bash
ragul futtat examples/01_hello.ragul
```

**Output:**

```
Helló, világ!
```

---

## What's happening

- `program-nk-hatás` (`program-ours-effect`) — declares an effect scope named `program`. The `-hatás` / `-effect` suffix marks it as eager: everything inside executes in order, top to bottom.
- `üdvözlet-be  "Helló, világ!"-t.` — assigns the string into the root `üdvözlet`. The compiler infers type `Szöveg`.
- `üdvözlet-képernyőre-va.` — pipes `üdvözlet` to the `képernyőre` (`-print`) channel and executes it with `-va` (`-doing`).

---

## Variation — with concatenation

=== "Hungarian"
    ```ragul
    program-nk-hatás
        név-be  "Ragul"-t.
        üdvözlet-be  "Helló, "-t.
        kimenet-be  üdvözlet-név-összefűz-t.
        kimenet-képernyőre-va.
    ```

=== "English aliases"
    ```ragul
    program-ours-effect
        name->     "Ragul"-obj.
        greeting-> "Hello, "-obj.
        output->   greeting-name-concat-obj.
        output-print-doing.
    ```

**Output:**

```
Helló, Ragul
```

The `-összefűz` / `-concat` suffix concatenates two strings. The second string is passed inline in the chain: `üdvözlet-név-összefűz-t` reads as *"üdvözlet, concatenated with név"*.

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/01_hello.ragul)
