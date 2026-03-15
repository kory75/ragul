# Functions & Scopes

## Scopes Are Suffixes

**A named scope and a custom suffix are the same thing.** Defining a named scope simultaneously defines a suffix that can be applied anywhere. There is no separate function declaration syntax.

=== "English aliases"
    ```ragul
    kétszeres-ours
        szám-yours.
        szám-szám-add-it  Szám-as.
    ```

=== "Hungarian"
    ```ragul
    kétszeres-unk
        szám-d.
        szám-szám-össze-t  Szám-ként.
    ```

This definition makes `-kétszeres` immediately available as an aspect suffix:

=== "English aliases"
    ```ragul
    x-into  3-it.
    y-into  x-kétszeres-it.                    // y = 6

    lista-into  [1,2,3]-it.
    lista-kétszeres-from  output-into  write-doing.  // [2,4,6]
    ```

=== "Hungarian"
    ```ragul
    x-be  3-t.
    y-be  x-kétszeres-t.                    // y = 6

    lista-be  [1,2,3]-t.
    lista-kétszeres-ből  kimenet-be  ír-va.  // [2,4,6]
    ```

---

## Parameters

Parameters are roots marked with `-d` / `-yours` (passed in). They receive values from the calling sentence via `-val` / `-with` bindings, in left-to-right order:

=== "English aliases"
    ```ragul
    szűrőhatár-ours
        lista-yours.       // receives the root (first argument)
        threshold-yours.   // receives the first -with argument
        lista-threshold-above-filter-it  List-as.

    // Called as:
    output-into  adatok-szűrőhatár-it  5-with.
    // adatok → lista-yours, 5 → threshold-yours
    ```

=== "Hungarian"
    ```ragul
    szűrőhatár-unk
        lista-d.           // receives the root (first argument)
        küszöb-d.          // receives the first -val argument
        lista-küszöb-felett-szűrve-t  Lista-ként.

    // Called as:
    kimenet-be  adatok-szűrőhatár-t  5-val.
    // adatok → lista-d, 5 → küszöb-d
    ```

With type annotations:

=== "English aliases"
    ```ragul
    felett-ours
        value-yours  Num-as.
        threshold-yours  Num-as.
        value-threshold-above-it  Bool-as.
    ```

=== "Hungarian"
    ```ragul
    felett-unk
        érték-d  Szám-ként.
        küszöb-d  Szám-ként.
        érték-küszöb-nagyobb-t  Logikai-ként.
    ```

---

## Return Value

The final unnamed result root of a scope is its return value — no explicit return keyword needed:

=== "English aliases"
    ```ragul
    kétszeres-ours
        szám-yours.
        szám-szám-add-it.  // this is the return value
    ```

=== "Hungarian"
    ```ragul
    kétszeres-unk
        szám-d.
        szám-szám-össze-t.  // this is the return value
    ```

---

## Scope and Binding

### Indentation as Scope

Ragul uses indentation (tabs) to define scope boundaries. Roots defined within a scope cease to exist when that scope closes:

=== "English aliases"
    ```ragul
    számítás-ours
        x-into  3-it.
        y-into  10-it.
        result-into  x-y-add-it.

    // x, y, result do not exist here
    ```

=== "Hungarian"
    ```ragul
    számítás-unk
        x-be  3-t.
        y-be  10-t.
        eredmény-be  x-y-össze-t.

    // x, y, eredmény do not exist here
    ```

### Nested Scopes

Scopes nest freely. Inner scopes can reference roots from outer scopes, but not vice versa:

=== "English aliases"
    ```ragul
    feldolgozás-ours
        lista-into  [1,2,3,4,5]-it.

        szűrés-ours
            smaller-into  lista-filter-from  3-below-with  obj.
            smaller-from  output-into  write-doing.

        // smaller does not exist here
        lista-from  output-into  write-doing.
    ```

=== "Hungarian"
    ```ragul
    feldolgozás-unk
        lista-be  [1,2,3,4,5]-t.

        szűrés-unk
            kisebb-be  lista-szűrve-ből  3-alatt-val  t.
            kisebb-ből  kimenet-be  ír-va.

        // kisebb does not exist here
        lista-ből  kimenet-be  ír-va.
    ```

---

## Possession Suffixes

Possession suffixes express explicit ownership when needed. Scoping is implicit by default — indentation handles it.

| Hungarian | English | Meaning |
|---|---|---|
| *(implicit)* | — | Belongs to current scope (default) |
| `-unk` / `-nk` | `-ours` | Explicitly owned by this scope |
| `-m` / `-em` | `-mine` | Immutable within this scope |
| `-d` / `-ed` | `-yours` | Passed in from outer scope (parameter) |
| `-ja` / `-je` | `-its` | Belongs to / references another root |

Usage mirrors `this.` in languages like C# — available when needed, not required:

=== "English aliases"
    ```ragul
    feldolgozás-ours
        x-mine-into  3-it.                      // immutable
        input-yours.                          // parameter — passed in from outside
        result-ours-into  input-filter-it.      // explicitly scoped result
    ```

=== "Hungarian"
    ```ragul
    feldolgozás-unk
        x-m-be  3-t.                        // immutable
        bemenet-d.                          // parameter — passed in from outside
        eredmény-unk-be  bemenet-szűrve-t.  // explicitly scoped result
    ```

---

## Conceptual Mapping

| Traditional concept | Ragul equivalent |
|---|---|
| Function definition | Named scope (`-unk` / `-ours`) |
| Function call | Suffix in a chain |
| Parameters | `-d` / `-yours` roots inside the scope |
| Return value | Final result root |
| Composition | Suffix stacking |
| Modules | Nested scopes (`-modul` / `-module`) |
| Type annotation | `-ként` / `-as` on `-d` roots and return |

---

## A Complete Example

A small library of annotated suffixes:

=== "English aliases"
    ```ragul
    // Numeric operations
    kétszeres-ours
        szám-yours  Num-as.
        szám-szám-add-it  Num-as.

    felére-ours
        szám-yours  Num-as.
        szám-2-div-it  Num-as.

    // Threshold filter
    szűrőhatár-ours
        lista-yours  List-as.
        threshold-yours  Num-as.
        lista-filter-from  threshold-above-with  obj  List-as.

    // Fallible file reader
    fájlolvasó-ours
        path-yours  Str-as.
        path-fájlról-from  read-doing-it  or-Str-or-Err-as.
    ```

=== "Hungarian"
    ```ragul
    // Numeric operations
    kétszeres-unk
        szám-d  Szám-ként.
        szám-szám-össze-t  Szám-ként.

    felére-unk
        szám-d  Szám-ként.
        szám-2-oszt-t  Szám-ként.

    // Threshold filter
    szűrőhatár-unk
        lista-d  Lista-ként.
        küszöb-d  Szám-ként.
        lista-szűrve-ből  küszöb-felett-val  t  Lista-ként.

    // Fallible file reader
    fájlolvasó-unk
        útvonal-d  Szöveg-ként.
        útvonal-fájlról-ből  olvas-va-t  vagy-Szöveg-vagy-Hiba-ként.
    ```

Calling these is unchanged — annotations are invisible at the call site:

=== "English aliases"
    ```ragul
    x-into  3-it.
    y-into  x-kétszeres-it.                    // y = 6

    output-into  adatok-szűrőhatár-it  5-with. // filter list above 5

    content-into  "adat.txt"-fájlolvasó-doing-?. // fallible — propagate error
    ```

=== "Hungarian"
    ```ragul
    x-be  3-t.
    y-be  x-kétszeres-t.                     // y = 6

    kimenet-be  adatok-szűrőhatár-t  5-val.  // filter list above 5

    tartalom-be  "adat.txt"-fájlolvasó-va-e. // fallible — propagate error
    ```
