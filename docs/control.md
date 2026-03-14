# Control Flow

Control flow in Ragul is expressed entirely through suffixes and named scopes — no reserved keywords. The same scope-as-suffix unification that makes functions work also makes conditionals and loops composable and reusable.

---

## Conditionals

A conditional is a named scope suffixed with `-ha` (if / given that).

### Simple if

```ragul
pozitív-e-nk-ha
    szám-d.
    szám-0-felett-ha
        szám-kétszeres-t.
```

### If / else

`-hanem` is the else branch — a sibling block at the same indent level as its `-ha`:

```ragul
előjelváltó-nk-ha
    szám-d.
    szám-0-felett-ha
        szám-kétszeres-t.
    -hanem
        szám-felére-t.
```

### If / else-if / else chain

`-különben-ha` (otherwise-if) extends the chain. Each link carries its own condition inline:

```ragul
besoroló-nk-ha
    szám-d.
    szám-100-felett-ha
        "nagy"-t.
    -különben-ha  szám-50-felett-ha
        "közepes"-t.
    -különben-ha  szám-10-felett-ha
        "kicsi"-t.
    -hanem
        "apró"-t.
```

### Calling a conditional scope as a suffix

Exactly like any other named scope:

```ragul
x-be  75-t.
kategória-be  x-besoroló-ha-t.
// kategória = "közepes"
```

### Conditional suffix reference

| Suffix | Meaning |
|---|---|
| `-ha` | if / given that — opens a conditional scope or branch |
| `-hanem` | else — sibling branch when `-ha` condition fails |
| `-különben-ha` | else-if — chained conditional branch |

---

## Loops

Loops are named scopes suffixed with a repetition marker. The condition that controls the loop is provided by a `-ha` root in the same sentence.

### While loop — `-míg`

Repeats the scope while the condition holds:

```ragul
duplázó-nk-míg
    szám-d.
    határ-d.
    szám-kétszeres-t  szám-határ-alatt-ha.

x-be  3-t.
x-be  x-duplázó-míg-t  100-val.
// x doubles repeatedly until x >= 100 → result: 192
```

### Until loop — `-ig`

Repeats until the condition becomes true:

```ragul
x-be  x-növel-ig-t  x-100-felett-ha.
// increment x UNTIL x is above 100
```

### For-each — `-mindegyik`

Applies a scope to every element of a collection:

```ragul
elemfeldolgozó-nk-mindegyik
    elem-d.
    elem-kétszeres-t.

lista-be  [1,2,3,4,5]-t.
kimenet-be  lista-elemfeldolgozó-mindegyik-t.
// [2,4,6,8,10]
```

### Accumulate / fold — `-gyűjt`

Folds a collection into a single value. The accumulator is supplied via `-val`:

```ragul
összesítő-nk-gyűjt
    elem-d.
    összeg-d.            // accumulator
    összeg-elem-össze-t. // add element to accumulator

kimenet-be  lista-összesítő-gyűjt-t  0-val.
// sums the list starting from 0
```

### Early exit — `-megszakít`

`-megszakít` (break) terminates a loop immediately. It always composes with `-ha` so the exit is conditional:

```ragul
kereső-nk-míg
    lista-d.
    cél-d.
    elem-be  lista-következő-t.
    elem-cél-egyenlő-ha
        elem-megszakít-t.
```

### Loop suffix reference

| Suffix | Aliases | Meaning |
|---|---|---|
| `-míg` | `-while` | Repeat while condition holds |
| `-ig` | `-until` | Repeat until condition becomes true |
| `-mindegyik` | `-each`, `-every` | Apply to each element of a collection |
| `-gyűjt` | `-fold`, `-reduce` | Accumulate a result across a collection |
| `-megszakít` | `-break` | Early exit — terminates the current loop |

---

## The Functional Character of Ragul

Ragul's control structures are deeply functional by design:

- Suffix chains are **function composition**
- Scopes are **closures**
- Named conditionals and loops are **reusable transformations**, not imperative control flow

A conditional defined once becomes a suffix reusable anywhere. A loop body defined once can be mapped over any collection. The same mechanisms that define functions define control structures — there is no separate syntax.
