# Error Handling

## Design Principles

Ragul uses two rules for errors:

- Unhandled errors are **fatal** — they terminate the program
- Errors propagate **automatically** up the suffix chain via the `-e` suffix

There are no exceptions, no `try`/`catch` keywords. Error handling follows the same suffix and scope model as everything else.

---

## The `vagy` Type

Any operation that can fail returns a `vagy` — a value that is either a success result or an error:

```ragul
// vagy-Szöveg-vagy-Hiba = either a Szöveg OR a Hiba
eredmény-be  "adat.txt"-fájlolvasó-va.
// eredmény is vagy-Szöveg-vagy-Hiba
```

The compiler knows `eredmény` is a `vagy` type and enforces that both cases are handled before the value is used. Skipping this produces error **E005**.

---

## Error Propagation — `-e`

The `-e` suffix sits after the action suffix `-va` / `-ve` in the chain. It means: *"if this operation produced an error, propagate it upward immediately — short-circuit the rest of the chain."*

```
root - [possession] - [aspect]* - action(-va) - [error(-e)] - case
```

```ragul
tartalom-be  "adat.txt"-fájlolvasó-va-e.
// call fájlolvasó — if error, propagate up immediately
// if success, bind result to tartalom
```

Without `-e`, the caller must handle the `vagy` type manually. With `-e`, errors bubble up to the nearest `-hibára` boundary.

---

## Error Handling Boundary — `-hibára`

`-hibára` is a sibling block to the main scope body — exactly like `-hanem` is to `-ha`. It catches any error that propagates up from within the scope:

```ragul
program-nk-hatás
    tartalom-be  "adat.txt"-fájlolvasó-va-e.
    adat-be  tartalom-elemző-va-e.
    adat-képernyőre-va.
    -hibára
        "feldolgozási hiba"-képernyőre-va.
```

If any `-va-e` sentence fails, execution jumps immediately to `-hibára`. If there is no `-hibára` and an error reaches the top of the program — fatal, program terminates.

---

## Error Values

Errors carry a message. A named error is just a root assigned an error value:

```ragul
hiba-be  "fájl nem található"-t.
```

Inside a `-hibára` block, the error is accessible as `hiba`:

```ragul
program-nk-hatás
    tartalom-be  "adat.txt"-fájlolvasó-va-e.
    tartalom-képernyőre-va.
    -hibára
        hiba-képernyőre-va.    // print the error message
```

---

## A Complete Example

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

| Suffix | Position | Meaning |
|---|---|---|
| `-va` / `-ve` | After aspects | Execute the action |
| `-e` | After `-va` / `-ve` | Propagate error upward if failure |
| `-hibára` | Sibling block | Catches errors propagated within the scope |
| `vagy` | Type prefix | Wraps a fallible result — `vagy-X-vagy-Y` |
| `Hiba` | Type | The error type — accessible inside `-hibára` as `hiba` |

---

## Compiler Error Codes

| Code | Meaning |
|---|---|
| E005 | Unhandled `vagy` type — fallible result used without `-e` or `-hibára` |
| E004 | Effectful suffix called from pure scope |
| E001 | Root guard failure — wrong type for suffix |
| E003 | Parallel write conflict — same root written twice in pure scope |
| E009 | Field mutation outside `-hatás` scope |
| W001 | Harmony warning — type boundary crossed without bridge suffix |

See [Tooling & CLI](tooling.md) for the full error code reference.
