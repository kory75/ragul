# Error Handling

Demonstrates Ragul's error model: operations that can fail return a `vagy` (or) type, `-e` / `-?` propagates errors upward automatically, and `-hibára` / `-catch` catches them at the boundary.

=== "English aliases"
    ```ragul
    program-ours-effect
        // -tonum tries to parse a string as a number — it fails on non-numeric strings.
        // -? propagates the error upward; -catch catches it.

        n->  "not-a-number"-tonum-doing-?.
        n-print-doing.
        -catch
            "Error caught: could not parse string as number"-print-doing.
    ```

=== "Hungarian"
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

`-számmá` / `-tonum` returns `vagy-Szám-vagy-Hiba` — either a number or an error. The `-e` / `-?` suffix after `-va` / `-doing` means: *"if this produced an error, propagate it upward immediately."*

```
n-be  "not-a-number"-számmá-va-e.
                     │       │  │
                     │       │  └── propagate error if failure
                     │       └── execute the operation
                     └── attempt to parse as number
```

When the error propagates, execution jumps directly to the `-hibára` / `-catch` block, skipping any remaining sentences in the scope.

---

## The `-hibára` / `-catch` boundary

`-hibára` is a sibling block to the scope body — structurally identical to `-hanem` / `-else` for conditionals:

=== "English aliases"
    ```ragul
    program-ours-effect
        // ... sentences that might fail with -? ...
        -catch
            // ... runs only if an error propagated up ...
            hiba-print-doing.     // 'hiba' is bound to the error value
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        // ... sentences that might fail with -e ...
        -hibára
            // ... runs only if an error propagated up ...
            hiba-képernyőre-va.   // 'hiba' is bound to the error value
    ```

!!! note
    `hiba` is the built-in name bound to the error value inside a catch block.
    It is a variable name, not a suffix — it does not have an English alias.

If no `-hibára` / `-catch` is present and an error reaches the top of the program, it is **fatal** — the program terminates with exit code 3.

---

## Error propagation chain

`-e` / `-?` can appear anywhere in a chain. Multiple fallible operations in sequence will each propagate to the same `-hibára` / `-catch`:

=== "English aliases"
    ```ragul
    program-ours-effect
        content->  "data.txt"-readfile-doing-?.  // fails if file missing
        data->     content-parse-doing-?.         // fails if content invalid
        data-print-doing.
        -catch
            "Pipeline failed: "-hiba-concat-doing  print-doing.
    ```

=== "Hungarian"
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
