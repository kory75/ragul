# Functions & Scopes

## Scopes Are Suffixes

**A named scope and a custom suffix are the same thing.** Defining a named scope simultaneously defines a suffix that can be applied anywhere. There is no separate function declaration syntax.

=== "Hungarian"
    ```ragul
    kétszeres-unk
        szám-d.
        szám-szám-össze-t  Szám-ként.
    ```

=== "English aliases"
    ```ragul
    kétszeres-ours
        szám-yours.
        szám-szám-add-obj  Szám-as.
    ```

This definition makes `-kétszeres` immediately available as an aspect suffix:

=== "Hungarian"
    ```ragul
    x-be  3-t.
    y-be  x-kétszeres-t.                    // y = 6

    lista-be  [1,2,3]-t.
    lista-kétszeres-ből  kimenet-be  ír-va.  // [2,4,6]
    ```

=== "English aliases"
    ```ragul
    x->  3-obj.
    y->  x-kétszeres-obj.                    // y = 6

    lista->  [1,2,3]-obj.
    lista-kétszeres-from  output->  write-doing.  // [2,4,6]
    ```

---

## Parameters

Parameters are roots marked with `-d` / `-yours` (passed in). They receive values from the calling sentence via `-val` / `-with` bindings, in left-to-right order:

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

=== "English aliases"
    ```ragul
    szűrőhatár-ours
        lista-yours.       // receives the root (first argument)
        threshold-yours.   // receives the first -with argument
        lista-threshold-above-filter-obj  List-as.

    // Called as:
    output->  adatok-szűrőhatár-obj  5-with.
    // adatok → lista-yours, 5 → threshold-yours
    ```

With type annotations:

=== "Hungarian"
    ```ragul
    felett-unk
        érték-d  Szám-ként.
        küszöb-d  Szám-ként.
        érték-küszöb-nagyobb-t  Logikai-ként.
    ```

=== "English aliases"
    ```ragul
    felett-ours
        value-yours  Num-as.
        threshold-yours  Num-as.
        value-threshold-above-obj  Bool-as.
    ```

---

## Return Value

The final unnamed result root of a scope is its return value — no explicit return keyword needed:

=== "Hungarian"
    ```ragul
    kétszeres-unk
        szám-d.
        szám-szám-össze-t.  // this is the return value
    ```

=== "English aliases"
    ```ragul
    kétszeres-ours
        szám-yours.
        szám-szám-add-obj.  // this is the return value
    ```

---

## Scope and Binding

### Indentation as Scope

Ragul uses indentation (tabs) to define scope boundaries. Roots defined within a scope cease to exist when that scope closes:

=== "Hungarian"
    ```ragul
    számítás-unk
        x-be  3-t.
        y-be  10-t.
        eredmény-be  x-y-össze-t.

    // x, y, eredmény do not exist here
    ```

=== "English aliases"
    ```ragul
    számítás-ours
        x->  3-obj.
        y->  10-obj.
        result->  x-y-add-obj.

    // x, y, result do not exist here
    ```

### Nested Scopes

Scopes nest freely. Inner scopes can reference roots from outer scopes, but not vice versa:

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

=== "English aliases"
    ```ragul
    feldolgozás-ours
        lista->  [1,2,3,4,5]-obj.

        szűrés-ours
            smaller->  lista-filter-from  3-below-with  obj.
            smaller-from  output->  write-doing.

        // smaller does not exist here
        lista-from  output->  write-doing.
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

=== "Hungarian"
    ```ragul
    feldolgozás-unk
        x-m-be  3-t.                        // immutable
        bemenet-d.                          // parameter — passed in from outside
        eredmény-unk-be  bemenet-szűrve-t.  // explicitly scoped result
    ```

=== "English aliases"
    ```ragul
    feldolgozás-ours
        x-mine->  3-obj.                      // immutable
        input-yours.                          // parameter — passed in from outside
        result-ours->  input-filter-obj.      // explicitly scoped result
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

=== "English aliases"
    ```ragul
    // Numeric operations
    kétszeres-ours
        szám-yours  Num-as.
        szám-szám-add-obj  Num-as.

    felére-ours
        szám-yours  Num-as.
        szám-2-div-obj  Num-as.

    // Threshold filter
    szűrőhatár-ours
        lista-yours  List-as.
        threshold-yours  Num-as.
        lista-filter-from  threshold-above-with  obj  List-as.

    // Fallible file reader
    fájlolvasó-ours
        path-yours  Str-as.
        path-fájlról-from  read-doing-obj  or-Str-or-Err-as.
    ```

Calling these is unchanged — annotations are invisible at the call site:

=== "Hungarian"
    ```ragul
    x-be  3-t.
    y-be  x-kétszeres-t.                     // y = 6

    kimenet-be  adatok-szűrőhatár-t  5-val.  // filter list above 5

    tartalom-be  "adat.txt"-fájlolvasó-va-e. // fallible — propagate error
    ```

=== "English aliases"
    ```ragul
    x->  3-obj.
    y->  x-kétszeres-obj.                    // y = 6

    output->  adatok-szűrőhatár-obj  5-with. // filter list above 5

    content->  "adat.txt"-fájlolvasó-doing-?. // fallible — propagate error
    ```
