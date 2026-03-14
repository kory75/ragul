# Hello World

The simplest Ragul program — assign a string and print it.

```ragul
program-nk-hatás
    üdvözlet-be  "Helló, világ!"-t.
    üdvözlet-képernyőre-va.
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

- `program-nk-hatás` — declares an effect scope named `program`. The `-hatás` suffix marks it as eager: everything inside executes in order, top to bottom.
- `üdvözlet-be  "Helló, világ!"-t.` — assigns the string into the root `üdvözlet`. The compiler infers type `Szöveg`.
- `üdvözlet-képernyőre-va.` — pipes `üdvözlet` to the `képernyőre` (screen) channel and executes it with `-va`.

---

## Variation — with concatenation

```ragul
program-nk-hatás
    név-be  "Ragul"-t.
    üdvözlet-be  "Helló, "-t.
    kimenet-be  üdvözlet-név-összefűz-t.
    kimenet-képernyőre-va.
```

**Output:**

```
Helló, Ragul
```

The `-összefűz` suffix concatenates two strings. The second string is passed inline in the chain: `üdvözlet-név-összefűz-t` reads as *"üdvözlet, concatenated with név"*.

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/01_hello.ragul)
