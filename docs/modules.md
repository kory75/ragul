# Modules

## Design Principles

A module in Ragul is a named scope that spans a file. Because scopes are already the fundamental unit of organisation, modules introduce no new concepts — they are scopes with two additional properties:

- They have an explicit name independent of the filename
- They declare a public/private boundary

Everything that applies to scopes applies to modules: their suffixes compose freely with any other suffix chain, and the compiler treats built-in library modules identically to user-defined ones.

---

## Declaring a Module

A module is declared at the top level of a file using `-nk-modul` / `-ours-module`:

=== "English aliases"
    ```ragul
    matematika-ours-module
        kétszeres-ours
            szám-yours  Szám-as.
            szám-szám-add-it  Szám-as.

        gyök-ours
            szám-yours  Szám-as.
            szám-sqrt-it  Szám-as.
    ```

=== "Hungarian"
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

Modules are imported using a `-t` / `-it` sentence at the top of the file:

=== "English aliases"
    ```ragul
    matematika-it.

    program-ours-effect
        x-into  9-it.
        y-into  x-gyök-it.
        y-print-doing.
    // prints: 3.0
    ```

=== "Hungarian"
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

The standard library ships three built-in modules. All suffixes are available without any explicit import — the standard library is loaded automatically.

| Module | Hungarian suffixes | English aliases |
|---|---|---|
| `matematika` | `-négyzetgyök`, `-hatvány`, `-abszolút`, `-kerekítve`, `-padló`, `-plafon`, `-log`, `-sin`, `-cos` | `-sqrt`, `-pow`, `-abs`, `-round`, `-floor`, `-ceil`, `-log`, `-sin`, `-cos` |
| `szöveg` | `-hossz`, `-nagybetűs`, `-kisbetűs`, `-tartalmaz`, `-kezdődik`, `-végződik`, `-feloszt`, `-formáz`, `-szelet`, `-csere`, `-számmá` | `-len`, `-upper`, `-lower`, `-contains`, `-startswith`, `-endswith`, `-split`, `-format`, `-slice`, `-replace`, `-tonum` |
| `lista` | `-rendezve`, `-fordítva`, `-első`, `-utolsó`, `-egyedi`, `-lapítva`, `-szűrve`, `-hozzáad`, `-eltávolít` | `-sorted`, `-reversed`, `-first`, `-last`, `-unique`, `-flat`, `-filter`, `-append`, `-remove` |

---

## Module Configuration

Module search paths are configured in `ragul.config`:

```toml
[modulok]
utvonalak = ["./lib", "./vendor"]
```

The compiler searches these paths (in order) when resolving module imports.
