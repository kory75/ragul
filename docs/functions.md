# Functions & Scopes

## Scopes Are Suffixes

**A named scope and a custom suffix are the same thing.** Defining a named scope simultaneously defines a suffix that can be applied anywhere. There is no separate function declaration syntax.

```ragul
kétszeres-unk
    szám-d.
    szám-szám-össze-t  Szám-ként.
```

This definition makes `-kétszeres` immediately available as an aspect suffix:

```ragul
x-be  3-t.
y-be  x-kétszeres-t.                    // y = 6

lista-be  [1,2,3]-t.
lista-kétszeres-ből  kimenet-be  ír-va.  // [2,4,6]
```

---

## Parameters

Parameters are roots marked with `-d` (yours — passed in). They receive values from the calling sentence via `-val` bindings, in left-to-right order:

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

```ragul
felett-unk
    érték-d  Szám-ként.
    küszöb-d  Szám-ként.
    érték-küszöb-nagyobb-t  Logikai-ként.
```

---

## Return Value

The final unnamed result root of a scope is its return value — no explicit return keyword needed:

```ragul
kétszeres-unk
    szám-d.
    szám-szám-össze-t.  // this is the return value
```

---

## Scope and Binding

### Indentation as Scope

Ragul uses indentation (tabs) to define scope boundaries. Roots defined within a scope cease to exist when that scope closes:

```ragul
számítás-unk
    x-be  3-t.
    y-be  10-t.
    eredmény-be  x-y-össze-t.

// x, y, eredmény do not exist here
```

### Nested Scopes

Scopes nest freely. Inner scopes can reference roots from outer scopes, but not vice versa:

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

| Suffix | Aliases | Meaning |
|---|---|---|
| *(implicit)* | — | Belongs to current scope (default) |
| `-unk` / `-nk` | `-ours` | Explicitly owned by this scope |
| `-m` / `-em` | `-mine` | Immutable within this scope |
| `-d` / `-ed` | `-yours` | Passed in from outer scope (parameter) |
| `-ja` / `-je` | `-its` | Belongs to / references another root |

Usage mirrors `this.` in languages like C# — available when needed, not required:

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
| Function definition | Named scope |
| Function call | Suffix in a chain |
| Parameters | `-d` roots inside the scope |
| Return value | Final result root |
| Composition | Suffix stacking |
| Modules | Nested scopes |
| Type annotation | `-ként` on `-d` roots and return |

---

## A Complete Example

A small library of annotated suffixes:

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

```ragul
x-be  3-t.
y-be  x-kétszeres-t.                     // y = 6

kimenet-be  adatok-szűrőhatár-t  5-val.  // filter list above 5

tartalom-be  "adat.txt"-fájlolvasó-va-e. // fallible — propagate error
```
