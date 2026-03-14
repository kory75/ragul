# Hello World

The simplest Ragul program — assign a string and print it.

```ragul
program-nk-hatás
    üdvözlet-be  "helló világ"-t.
    üdvözlet-képernyőre-va.
```

**Run it:**

```bash
ragul futtat hello.ragul
```

**Output:**

```
helló világ
```

---

## What's happening

- `program-nk-hatás` — declares an effect scope named `program`. The `-hatás` suffix means everything inside executes eagerly in order.
- `üdvözlet-be  "helló világ"-t.` — assigns the string `"helló világ"` into the root `üdvözlet`. No type annotation needed — the compiler infers `Szöveg`.
- `üdvözlet-képernyőre-va.` — pipes `üdvözlet` to the `képernyőre` (screen) channel and executes it with `-va`.

---

## With a variable

```ragul
program-nk-hatás
    név-be  "Ragul"-t.
    üdvözlet-be  "helló "-t.
    kimenet-be  üdvözlet-név-összefűz-t.
    kimenet-képernyőre-va.
```

**Output:**

```
helló Ragul
```

---

## Using the REPL

You can try these interactively:

```bash
ragul repl
```

```
>>> üdvözlet-be  "helló világ"-t.
>>> üdvözlet-képernyőre-va.
helló világ
>>>
```
