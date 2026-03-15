# Error Handling

## Design Principles

Ragul uses two rules for errors:

- Unhandled errors are **fatal** — they terminate the program
- Errors propagate **automatically** up the suffix chain via the `-e` / `-?` suffix

There are no exceptions, no `try`/`catch` keywords. Error handling follows the same suffix and scope model as everything else.

---

## The `vagy` Type

Any operation that can fail returns a `vagy` — a value that is either a success result or an error:

=== "English aliases"
    ```ragul
    // vagy-Szöveg-vagy-Hiba = either a Szöveg OR a Hiba
    result-into  "adat.txt"-fájlolvasó-doing.
    // result is vagy-Szöveg-vagy-Hiba
    ```

=== "Hungarian"
    ```ragul
    // vagy-Szöveg-vagy-Hiba = either a Szöveg OR a Hiba
    eredmény-be  "adat.txt"-fájlolvasó-va.
    // eredmény is vagy-Szöveg-vagy-Hiba
    ```

The compiler knows `eredmény` is a `vagy` type and enforces that both cases are handled before the value is used. Skipping this produces error **E005**.

---

## Error Propagation — `-e` / `-?`

The `-e` / `-?` suffix sits after the action suffix `-va` / `-doing` in the chain. It means: *"if this operation produced an error, propagate it upward immediately — short-circuit the rest of the chain."*

```
root - [possession] - [aspect]* - action(-va) - [error(-e)] - case
```

=== "English aliases"
    ```ragul
    content-into  "adat.txt"-fájlolvasó-doing-?.
    // call fájlolvasó — if error, propagate up immediately
    // if success, bind result to content
    ```

=== "Hungarian"
    ```ragul
    tartalom-be  "adat.txt"-fájlolvasó-va-e.
    // call fájlolvasó — if error, propagate up immediately
    // if success, bind result to tartalom
    ```

Without `-e` / `-?`, the caller must handle the `vagy` type manually. With it, errors bubble up to the nearest `-hibára` / `-catch` boundary.

---

## Error Handling Boundary — `-hibára` / `-catch`

`-hibára` / `-catch` is a sibling block to the main scope body — exactly like `-hanem` / `-else` is to `-ha` / `-if`. It catches any error that propagates up from within the scope:

=== "English aliases"
    ```ragul
    program-ours-effect
        content-into  "adat.txt"-fájlolvasó-doing-?.
        data-into  content-elemző-doing-?.
        data-print-doing.
        -catch
            "feldolgozási hiba"-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        tartalom-be  "adat.txt"-fájlolvasó-va-e.
        adat-be  tartalom-elemző-va-e.
        adat-képernyőre-va.
        -hibára
            "feldolgozási hiba"-képernyőre-va.
    ```

If any `-va-e` / `-doing-?` sentence fails, execution jumps immediately to `-hibára` / `-catch`. If there is no `-hibára` and an error reaches the top of the program — fatal, program terminates.

---

## Error Values

Errors carry a message. A named error is just a root assigned an error value:

=== "English aliases"
    ```ragul
    hiba-into  "file not found"-it.
    ```

=== "Hungarian"
    ```ragul
    hiba-be  "fájl nem található"-t.
    ```

Inside a `-hibára` / `-catch` block, the error is accessible as `hiba`:

=== "English aliases"
    ```ragul
    program-ours-effect
        content-into  "adat.txt"-fájlolvasó-doing-?.
        content-print-doing.
        -catch
            hiba-print-doing.      // print the error message
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        tartalom-be  "adat.txt"-fájlolvasó-va-e.
        tartalom-képernyőre-va.
        -hibára
            hiba-képernyőre-va.    // print the error message
    ```

!!! note
    `hiba` is the built-in binding name inside a catch block — it is a variable name, not a suffix, and does not have an English alias.

---

## A Complete Example

=== "English aliases"
    ```ragul
    // Fallible file reader
    fájlolvasó-ours
        path-yours  Szöveg-as.
        path-fájlról-from  read-doing-it  vagy-Szöveg-vagy-Hiba-as.

    // Fallible JSON parser
    elemző-ours
        text-yours  Szöveg-as.
        text-json-doing-it  vagy-Lista-vagy-Hiba-as.

    // Program — handles errors at the boundary
    program-ours-effect
        content-into  "adat.txt"-fájlolvasó-doing-?.
        data-into  content-elemző-doing-?.
        data-print-doing.
        -catch
            "hiba: "-hiba-concat-doing  print-doing.
    ```

=== "Hungarian"
    ```ragul
    // Fallible file reader
    fájlolvasó-unk
        útvonal-d  Szöveg-ként.
        útvonal-fájlról-ből  olvas-va-t  vagy-Szöveg-vagy-Hiba-ként.

    // Fallible JSON parser
    elemző-unk
        szöveg-d  Szöveg-ként.
        szöveg-json-va-t  vagy-Lista-vagy-Hiba-ként.

    // Program — handles errors at the boundary
    program-nk-hatás
        tartalom-be  "adat.txt"-fájlolvasó-va-e.
        adat-be  tartalom-elemző-va-e.
        adat-képernyőre-va.
        -hibára
            "hiba: "-hiba-összefűz-va  képernyőre-va.
    ```

---

## Suffix Reference

| Hungarian | English | Position | Meaning |
|---|---|---|---|
| `-va` / `-ve` | `-doing` | After aspects | Execute the action |
| `-e` | `-?` | After `-va` / `-doing` | Propagate error upward if failure |
| `-hibára` | `-catch` | Sibling block | Catches errors propagated within the scope |
| `vagy` | — | Type prefix | Wraps a fallible result — `vagy-X-vagy-Y` |
| `Hiba` | — | Type | The error type — accessible inside `-hibára` as `hiba` |

---

## Compiler Error Codes

| Code | Meaning |
|---|---|
| E005 | Unhandled `vagy` type — fallible result used without `-e` / `-?` or `-hibára` / `-catch` |
| E004 | Effectful suffix called from pure scope |
| E001 | Root guard failure — wrong type for suffix |
| E003 | Parallel write conflict — same root written twice in pure scope |
| E009 | Field mutation outside `-hatás` / `-effect` scope |
| W001 | Harmony warning — type boundary crossed without bridge suffix |

See [Tooling & CLI](tooling.md) for the full error code reference.
