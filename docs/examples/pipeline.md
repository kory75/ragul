# Data Pipeline

This example demonstrates Ragul's core strength: stacking suffixes to build processing pipelines.

---

## Filter and sort a list

```ragul
program-nk-hatás
    adatok-be  [7, 2, 15, 3, 9, 1, 12, 4]-t.

    // keep numbers above 5, then sort ascending
    eredmény-be  adatok-szűrve-rendezve-ból  5-felett-val  t.

    eredmény-képernyőre-va.
```

**Output:**

```
[7, 9, 12, 15]
```

**What's happening in `adatok-szűrve-rendezve-ból  5-felett-val`:**

- `adatok` — the source list
- `-szűrve` — filter aspect; takes a condition via `-val`
- `-rendezve` — sort aspect (applied after filter)
- `-ból` — case: source (FROM)
- `5-felett-val` — the filter condition: "greater than 5", bound to `-szűrve`

---

## Chaining multiple transformations

```ragul
program-nk-hatás
    számok-be  [3, 1, 4, 1, 5, 9, 2, 6, 5, 3, 5]-t.

    // remove duplicates, keep >= 4, sort, take first 3
    top-be  számok-egyedi-szűrve-rendezve-ból  4-legalább-val  t.
    első3-be  top-első-t.

    első3-képernyőre-va.
```

---

## Define a reusable pipeline suffix

```ragul
// Define a suffix that filters and sorts any list of numbers
szűrtRendezett-unk
    lista-d  Lista-Szám-ként.
    küszöb-d  Szám-ként.
    lista-szűrve-rendezve-ból  küszöb-felett-val  t  Lista-Szám-ként.

// Use it
program-nk-hatás
    a-be  [7, 2, 15, 3, 9, 1, 12]-t.
    b-be  [100, 50, 3, 75, 8, 42]-t.

    a-szűrt-be  a-szűrtRendezett-t  5-val.
    b-szűrt-be  b-szűrtRendezett-t  40-val.

    a-szűrt-képernyőre-va.   // [7, 9, 12, 15]
    b-szűrt-képernyőre-va.   // [42, 50, 75, 100]
```

---

## Fold / reduce

Sum a list using `-gyűjt`:

```ragul
összesítő-nk-gyűjt
    elem-d.
    összeg-d.
    összeg-elem-össze-t.

program-nk-hatás
    lista-be  [1, 2, 3, 4, 5]-t.
    összeg-be  lista-összesítő-gyűjt-t  0-val.
    összeg-képernyőre-va.
// prints: 15
```

---

## Pipeline with error handling

Read numbers from a list of strings, parsing each — skip failures:

```ragul
program-nk-hatás
    szövegek-be  ["3", "alma", "7", "2.5", "körte"]-t.

    számok-be  []-t.

    feldolgozó-nk-hatás-mindegyik
        s-d.
        n-be  s-számmá-va.
        n-számok-hozzáad-ba.
        -hibára
            // skip unparseable entries silently
            "kihagyva: "-s-összefűz-va  stderr-va.

    szövegek-feldolgozó-mindegyik-va.
    számok-képernyőre-va.
// prints: [3.0, 7.0, 2.5]
// stderr: kihagyva: alma
// stderr: kihagyva: körte
```
