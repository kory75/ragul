# Error Handling

Demonstrates Ragul's error model: operations that can fail return a `vagy` (or) type, `-e` propagates errors upward automatically, and `-hibára` catches them at the boundary.

```ragul
program-nk-hatás
    // -számmá tries to parse a string as a number — it fails on non-numeric strings.
    // -e propagates the error upward; -hibára catches it.

    n-be  "not-a-number"-számmá-va-e.
    n-képernyőre-va.
    -hibára
        "Error caught: could not parse string as number"-képernyőre-va.
```

**Output:**

```
Error caught: could not parse string as number
```

---

## How it works

`-számmá` returns `vagy-Szám-vagy-Hiba` — either a number or an error. The `-e` suffix after `-va` means: *"if this produced an error, propagate it upward immediately."*

```
n-be  "not-a-number"-számmá-va-e.
                     │       │  │
                     │       │  └── propagate error if failure
                     │       └── execute the operation
                     └── attempt to parse as number
```

When the error propagates, execution jumps directly to the `-hibára` block, skipping any remaining sentences in the scope.

---

## The `-hibára` boundary

`-hibára` is a sibling block to the scope body — structurally identical to `-hanem` for conditionals:

```ragul
program-nk-hatás
    // ... sentences that might fail with -e ...
    -hibára
        // ... runs only if an error propagated up ...
        hiba-képernyőre-va.   // 'hiba' is bound to the error value
```

If no `-hibára` is present and an error reaches the top of the program, it is **fatal** — the program terminates with exit code 3.

---

## Error propagation chain

`-e` can appear anywhere in a chain. Multiple fallible operations in sequence will each propagate to the same `-hibára`:

```ragul
program-nk-hatás
    tartalom-be  "adat.txt"-fájlolvasó-va-e.  // fails if file missing
    adat-be      tartalom-elemző-va-e.          // fails if content invalid
    adat-képernyőre-va.
    -hibára
        "Pipeline failed: "-hiba-összefűz-va  képernyőre-va.
```

---

[Download example](https://github.com/kory75/ragul/blob/master/examples/07_error_handling.ragul)
