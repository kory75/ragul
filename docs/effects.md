# Effects & I/O

## I/O as a Suffix Family

I/O in Ragul is not special-cased by the compiler. Every I/O channel is a named scope defined with `-nk-hatás` / `-ours-effect`. This makes every channel a suffix that can appear in any suffix chain — while the compiler enforces it can only be called from within another effect scope.

---

## The Effect Scope — `-hatás` / `-effect`

Lazy evaluation means sentences only execute when their result is needed. A sentence that writes to screen has no result — so the lazy evaluator would never run it. The `-hatás` / `-effect` suffix solves this by marking a scope as **eager**: everything inside executes in order, top to bottom, unconditionally.

=== "English aliases"
    ```ragul
    program-ours-effect
        x-into  "hello world"-it.
        x-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        x-be  "helló világ"-t.
        x-képernyőre-va.
    ```

Two rules enforced by the compiler:

- Inside a `-hatás` / `-effect` scope, all sentences execute **eagerly in order**
- A **pure scope** (without `-hatás`) **cannot call an effectful scope** — compile error E004

=== "English aliases"
    ```ragul
    pure-calculation-ours
        x-into  3-it.
        x-print-doing.      // ERROR E004: effectful suffix called from pure scope
    ```

=== "Hungarian"
    ```ragul
    tiszta-számítás-unk
        x-be  3-t.
        x-képernyőre-va.    // ERROR E004: effectful suffix called from pure scope
    ```

---

## I/O Channels

Every channel is a built-in effect scope. The table below lists all channels with their English aliases.

| Hungarian root | English alias | Direction | Meaning |
|---|---|---|---|
| `képernyőre` | `stdout` / `-print` | write | Console stdout |
| `bemenetről` | `stdin` | read | Console stdin |
| `stderr` | `stderr` | write | Stderr |
| `fájlból` | `filein` | read | File read |
| `fájlra` | `fileout` | write | File write |
| `hálózatból` | `netin` | read | Network read (stub — v0.4.0) |
| `hálózatra` | `netout` | write | Network write (stub — v0.4.0) |

`stdout` and `stdin` normalise to `képernyőre` and `bemenetről` at lex time — they are full aliases, not separate channels.

---

## Console Output

`-print` / `-képernyőre` writes a value to stdout. `stderr` writes to stderr.

=== "English aliases"
    ```ragul
    program-ours-effect
        msg-into  "hello world"-it.
        msg-print-doing.            // stdout
        msg-stderr-doing.           // stderr
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        üzenet-be  "helló világ"-t.
        üzenet-képernyőre-va.       // stdout
        üzenet-stderr-va.           // stderr
    ```

---

## Console Input

`stdin` / `bemenetről` reads a line from the user when resolved as a source value.

=== "English aliases"
    ```ragul
    program-ours-effect
        name-into  stdin-it.
        greeting-into  "Hello, "-name-concat-it.
        greeting-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        nev-be  bemenetről-t.
        udvozles-be  "Szia, "-nev-összefűz-t.
        udvozles-képernyőre-va.
    ```

---

## File Write

`-fileout` / `-fájlra` writes a value to a file. The filename is the inline argument immediately before the channel suffix.

=== "English aliases"
    ```ragul
    program-ours-effect
        report-into  "Sales: 42, Returns: 3"-it.
        report-"report.txt"-fileout-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        jelentes-be  "Eladás: 42, Visszárú: 3"-t.
        jelentes-"report.txt"-fájlra-va.
    ```

The filename can also be a variable:

=== "English aliases"
    ```ragul
    program-ours-effect
        outfile-into  "report.txt"-it.
        report-into   "Sales: 42, Returns: 3"-it.
        report-outfile-fileout-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        kijfajl-be  "report.txt"-t.
        jelentes-be "Eladás: 42, Visszárú: 3"-t.
        jelentes-kijfajl-fájlra-va.
    ```

---

## File Read

`-filein` / `-fájlból` reads the entire contents of a file and returns a string. It returns a `Hiba` value if the file cannot be read.

=== "English aliases"
    ```ragul
    program-ours-effect
        content-into  "data.txt"-filein-it.
        content-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        tartalom-ba  "data.txt"-fájlból-t.
        tartalom-képernyőre-va.
    ```

Operations can be chained directly onto the read — for example, parse a JSON file in one step:

=== "English aliases"
    ```ragul
    program-ours-effect
        records-into  "orders.json"-filein-json-it.
        count-into    records-len-it.
        count-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        rekordok-ba  "orders.json"-fájlból-json-t.
        db-ba        rekordok-hossz-t.
        db-képernyőre-va.
    ```

---

## File I/O with Error Handling

File operations can fail. `-filein` / `-fájlból` returns a `Hiba` value when the file does not exist or cannot be read. Attach `-e` / `-?` to propagate the error to the nearest `-catch` / `-hibára` handler.

=== "English aliases"
    ```ragul
    program-ours-effect
        content-into  "config.txt"-filein-?-it.
        content-print-doing.
    -catch
        "Error: could not read config.txt"-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        tartalom-ba  "config.txt"-fájlból-e-t.
        tartalom-képernyőre-va.
    -hibára
        "Hiba: nem sikerült beolvasni a config.txt fájlt"-képernyőre-va.
    ```

The same pattern applies to writing — `-fileout` / `-fájlra` returns a `Hiba` if the file cannot be written (for example, a read-only path):

=== "English aliases"
    ```ragul
    program-ours-effect
        data-into  "results"-it.
        data-"/read-only/out.txt"-fileout-?-doing.
    -catch
        "Error: could not write output file"-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        adat-be  "eredmények"-t.
        adat-"/read-only/out.txt"-fájlra-e-va.
    -hibára
        "Hiba: nem sikerült megírni a kimeneti fájlt"-képernyőre-va.
    ```

A complete read-transform-write pipeline with error handling on both ends:

=== "English aliases"
    ```ragul
    program-ours-effect
        raw-into      "input.json"-filein-?-it.
        records-into  raw-json-it.
        names-into    records-"name"-field-it.
        names-tojson-"output.json"-fileout-?-doing.
    -catch
        "Pipeline failed — check input.json exists and output path is writable"-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        nyers-ba     "input.json"-fájlból-e-t.
        rekordok-ba  nyers-json-t.
        nevek-ba     rekordok-"name"-mező-t.
        nevek-jsonná-"output.json"-fájlra-e-va.
    -hibára
        "Hiba a feldolgozásban — ellenőrizd az input.json fájlt"-képernyőre-va.
    ```

---

## Defining Custom Channels

Channels are not compiler magic — they are Ragul scopes, defined exactly like any other scope with `-nk-hatás` / `-ours-effect`. The standard library provides the built-in channels, but you can define your own:

=== "English aliases"
    ```ragul
    adatbázisba-ours-effect
        query-yours.
        // implementation: execute query against database
    ```

=== "Hungarian"
    ```ragul
    adatbázisba-nk-hatás
        lekérdezés-d.
        // implementation: execute lekérdezés against database
    ```

Once defined, `adatbázisba` becomes a suffix usable anywhere — identically to built-in channels:

=== "English aliases"
    ```ragul
    program-ours-effect
        sql-into  "SELECT * FROM users"-it.
        sql-adatbázisba-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        sql-be  "SELECT * FROM users"-t.
        sql-adatbázisba-va.
    ```

---

## Suffix Reference

| Hungarian | English | Meaning |
|---|---|---|
| `-nk-hatás` | `-ours-effect` | Declares an effect scope — eager, I/O permitted |
| `-va` / `-ve` | `-doing` | Action — executes the operation |
| `-képernyőre` | `-print` / `stdout` | Write to stdout |
| `bemenetről` | `stdin` | Read from stdin (used as root value) |
| `stderr` | `stderr` | Write to stderr |
| `-fájlból` | `-filein` | Read entire file, returns `Szöveg` or `Hiba` |
| `-fájlra` | `-fileout` | Write value to file (filename is inline arg) |
| `-e` / `-?` | `-e` / `-?` | Propagate `Hiba` to nearest `-catch` handler |
