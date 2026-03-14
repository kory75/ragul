# Modules

## Design Principles

A module in Ragul is a named scope that spans a file. Because scopes are already the fundamental unit of organisation, modules introduce no new concepts — they are scopes with two additional properties:

- They have an explicit name independent of the filename
- They declare a public/private boundary

Everything that applies to scopes applies to modules: their suffixes compose freely with any other suffix chain, and the compiler treats built-in library modules identically to user-defined ones.

---

## Declaring a Module

A module is declared at the top level of a file using `-nk-modul`:

```ragul
matematika-nk-modul
    kétszeres-unk
        szám-d  Szám-ként.
        szám-szám-össze-t  Szám-ként.

    gyök-unk
        szám-d  Szám-ként.
        szám-négyzetgyök-t  Szám-ként.
```

This file defines the `matematika` module. Its public suffixes (`-kétszeres`, `-gyök`) are immediately available to any file that imports it.

---

## Importing a Module

Modules are imported using a `-t` sentence at the top of the file:

```ragul
matematika-t.

program-nk-hatás
    x-be  9-t.
    y-be  x-gyök-t.
    y-képernyőre-va.
// prints: 3.0
```

---

## Standard Library Modules

The standard library ships three built-in modules:

| Module | Contents |
|---|---|
| `matematika` | Math operations: `-négyzetgyök`, `-hatvány`, `-abszolút`, `-kerekítve`, `-padló`, `-plafon`, `-log`, `-sin`, `-cos` |
| `szöveg` | String operations: `-hossz`, `-nagybetűs`, `-kisbetűs`, `-tartalmaz`, `-kezdődik`, `-végződik`, `-feloszt`, `-formáz`, `-szelet`, `-csere`, `-számmá` |
| `lista` | List operations: `-rendezve`, `-fordítva`, `-első`, `-utolsó`, `-egyedi`, `-lapítva`, `-szűrve`, `-hozzáad`, `-eltávolít` |

These are available without any explicit import — the standard library is loaded automatically.

---

## Module Configuration

Module search paths are configured in `ragul.config`:

```toml
[modulok]
utvonalak = ["./lib", "./vendor"]
```

The compiler searches these paths (in order) when resolving module imports.
