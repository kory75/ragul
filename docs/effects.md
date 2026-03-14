# Effects & I/O

## I/O as a Suffix Family

I/O in Ragul is not special-cased by the compiler. Every I/O channel is a named scope defined with `-nk-hatás` / `-ours-effect` (the effect scope suffix). This makes every channel a suffix that can appear in any suffix chain — while the compiler enforces it can only be called from within another effect scope.

---

## The Effect Scope — `-hatás` / `-effect`

Lazy evaluation means sentences only execute when their result is needed. A sentence that writes to screen has no result — so the lazy evaluator would never run it. The `-hatás` / `-effect` suffix solves this by marking a scope as **eager**: everything inside executes in order, top to bottom, unconditionally.

=== "Hungarian"
    ```ragul
    program-nk-hatás
        x-be  "helló világ"-t.
        x-képernyőre-va.
    ```

=== "English aliases"
    ```ragul
    program-ours-effect
        x->  "hello world"-obj.
        x-print-doing.
    ```

Two rules enforced by the compiler:

- Inside a `-hatás` / `-effect` scope, all sentences execute **eagerly in order**
- A **pure scope** (without `-hatás`) **cannot call an effectful scope** — compile error E004

=== "Hungarian"
    ```ragul
    tiszta-számítás-unk
        x-be  3-t.
        x-képernyőre-va.    // ERROR E004: effectful suffix called from pure scope
    ```

=== "English aliases"
    ```ragul
    tiszta-számítás-ours
        x->  3-obj.
        x-print-doing.      // ERROR E004: effectful suffix called from pure scope
    ```

---

## Standard I/O Channels

Every channel is a built-in scope defined with `-nk-hatás` / `-ours-effect`. The channel name carries its own case suffix indicating direction — `-ra` / `-re` (onto) for write, `-ról` / `-ről` (from) for read:

| Channel root | English | Direction | Meaning |
|---|---|---|---|
| `képernyőre` | `-print` alias | write | Console / stdout |
| `bemenetről` | — | read | Console / stdin |
| `fájlra` | — | write | File system write |
| `fájlról` | — | read | File system read |
| `hálózatra` | — | write | Network write |
| `hálózatról` | — | read | Network read |
| `stderr` | — | write | Stderr / error output |

All channels work identically — same suffix mechanism, different target. Swapping the channel root is the only change:

=== "Hungarian"
    ```ragul
    program-nk-hatás
        x-be  "helló"-t.
        x-képernyőre-va.    // write to console
        x-fájlra-va.        // write to file — same sentence structure
        x-stderr-va.        // write to stderr — same sentence structure
    ```

=== "English aliases"
    ```ragul
    program-ours-effect
        x->  "hello"-obj.
        x-print-doing.      // write to console
        x-fájlra-doing.     // write to file — same sentence structure
        x-stderr-doing.     // write to stderr — same sentence structure
    ```

---

## Reading Input

Reading is also an effect operation. The pattern uses the read channel as a source with `-ből` / `-from`:

=== "Hungarian"
    ```ragul
    program-nk-hatás
        input-be  bemenetről-ből  olvas-va-t.
        input-képernyőre-va.
    ```

=== "English aliases"
    ```ragul
    program-ours-effect
        input->  bemenetről-from  read-doing-obj.
        input-print-doing.
    ```

---

## Defining Custom Channels

Channels are not compiler magic — they are Ragul scopes, defined exactly like any other scope with `-nk-hatás` / `-ours-effect`. The standard library provides the built-in channels, but you can define your own:

=== "Hungarian"
    ```ragul
    adatbázisba-nk-hatás
        lekérdezés-d.
        // implementation: execute lekérdezés against database
    ```

=== "English aliases"
    ```ragul
    adatbázisba-ours-effect
        query-yours.
        // implementation: execute query against database
    ```

Once defined, `adatbázisba` becomes a suffix usable anywhere — identically to built-in channels:

=== "Hungarian"
    ```ragul
    program-nk-hatás
        sql-be  "SELECT * FROM users"-t.
        sql-adatbázisba-va.
    ```

=== "English aliases"
    ```ragul
    program-ours-effect
        sql->  "SELECT * FROM users"-obj.
        sql-adatbázisba-doing.
    ```

---

## Suffix Reference

| Hungarian | English | Meaning |
|---|---|---|
| `-nk-hatás` | `-ours-effect` | Defines an effect scope — eager evaluation, I/O permitted |
| `-hatás` | `-effect` | Marks a scope as effectful when composing |
| `-va` / `-ve` | `-doing` | Action — executes the operation |
| `-képernyőre` | `-print` | Write to stdout |
| `-ból` / `-ből` / `-ról` / `-ről` | `-from` | Source — FROM (read direction) |
| `-ra` / `-re` | — | Target embedded in channel name (write direction) |
