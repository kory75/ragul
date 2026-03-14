# Effects & I/O

## I/O as a Suffix Family

I/O in Ragul is not special-cased by the compiler. Every I/O channel is a named scope defined with `-nk-hatás` (the effect scope suffix). This makes every channel a suffix that can appear in any suffix chain — while the compiler enforces it can only be called from within another effect scope.

---

## The Effect Scope — `-hatás`

Lazy evaluation means sentences only execute when their result is needed. A sentence that writes to screen has no result — so the lazy evaluator would never run it. The `-hatás` suffix solves this by marking a scope as **eager**: everything inside executes in order, top to bottom, unconditionally.

```ragul
program-nk-hatás
    x-be  "helló világ"-t.
    x-képernyőre-va.
```

Two rules enforced by the compiler:

- Inside a `-hatás` scope, all sentences execute **eagerly in order**
- A **pure scope** (without `-hatás`) **cannot call an effectful scope** — compile error E004

```ragul
tiszta-számítás-unk
    x-be  3-t.
    x-képernyőre-va.    // ERROR E004: effectful suffix called from pure scope
```

---

## Standard I/O Channels

Every channel is a built-in scope defined with `-nk-hatás`. The channel name carries its own case suffix indicating direction — `-ra` / `-re` (onto) for write, `-ról` / `-ről` (from) for read:

| Channel root | Direction | Meaning |
|---|---|---|
| `képernyőre` | write | Console / stdout |
| `bemenetről` | read | Console / stdin |
| `fájlra` | write | File system write |
| `fájlról` | read | File system read |
| `hálózatra` | write | Network write |
| `hálózatról` | read | Network read |
| `stderr` | write | Stderr / error output |

All channels work identically — same suffix mechanism, different target. Swapping the channel root is the only change:

```ragul
program-nk-hatás
    x-be  "helló"-t.
    x-képernyőre-va.    // write to console
    x-fájlra-va.        // write to file — same sentence structure
    x-stderr-va.        // write to stderr — same sentence structure
```

---

## Reading Input

Reading is also an effect operation. The pattern uses the read channel as a source with `-ből`:

```ragul
program-nk-hatás
    input-be  bemenetről-ből  olvas-va-t.
    input-képernyőre-va.
```

---

## Defining Custom Channels

Channels are not compiler magic — they are Ragul scopes, defined exactly like any other scope with `-nk-hatás`. The standard library provides the built-in channels, but you can define your own:

```ragul
adatbázisba-nk-hatás
    lekérdezés-d.
    // implementation: execute lekérdezés against database
```

Once defined, `adatbázisba` becomes a suffix usable anywhere — identically to built-in channels:

```ragul
program-nk-hatás
    sql-be  "SELECT * FROM users"-t.
    sql-adatbázisba-va.
```

---

## Suffix Reference

| Suffix | Meaning |
|---|---|
| `-nk-hatás` | Defines an effect scope — eager evaluation, I/O permitted |
| `-hatás` | Marks a scope as effectful when composing |
| `-va` / `-ve` | Action — executes the operation |
| `-ból` / `-ből` / `-ról` / `-ről` | Source — FROM (read direction) |
| `-ra` / `-re` | Target embedded in channel name (write direction) |
