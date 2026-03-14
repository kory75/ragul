# Control Flow

Control flow in Ragul is expressed entirely through suffixes and named scopes — no reserved keywords. The same scope-as-suffix unification that makes functions work also makes conditionals and loops composable and reusable.

---

## Conditionals

A conditional is a named scope suffixed with `-ha` / `-if` (if / given that).

### Simple if

=== "Hungarian"
    ```ragul
    pozitív-e-nk-ha
        szám-d.
        szám-0-felett-ha
            szám-kétszeres-t.
    ```

=== "English aliases"
    ```ragul
    pozitív-e-ours-if
        szám-yours.
        szám-0-above-if
            szám-kétszeres-obj.
    ```

### If / else

`-hanem` / `-else` is the else branch — a sibling block at the same indent level as its `-ha` / `-if`:

=== "Hungarian"
    ```ragul
    előjelváltó-nk-ha
        szám-d.
        szám-0-felett-ha
            szám-kétszeres-t.
        -hanem
            szám-felére-t.
    ```

=== "English aliases"
    ```ragul
    előjelváltó-ours-if
        szám-yours.
        szám-0-above-if
            szám-kétszeres-obj.
        -else
            szám-felére-obj.
    ```

### If / else-if / else chain

`-különben-ha` / `-elif` extends the chain. Each link carries its own condition inline:

=== "Hungarian"
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

=== "English aliases"
    ```ragul
    besoroló-ours-if
        szám-yours.
        szám-100-above-if
            "nagy"-obj.
        -elif  szám-50-above-if
            "közepes"-obj.
        -elif  szám-10-above-if
            "kicsi"-obj.
        -else
            "apró"-obj.
    ```

### Calling a conditional scope as a suffix

Exactly like any other named scope:

=== "Hungarian"
    ```ragul
    x-be  75-t.
    kategória-be  x-besoroló-ha-t.
    // kategória = "közepes"
    ```

=== "English aliases"
    ```ragul
    x->  75-obj.
    category->  x-besoroló-if-obj.
    // category = "közepes"
    ```

### Conditional suffix reference

| Hungarian | English | Meaning |
|---|---|---|
| `-ha` | `-if` | if / given that — opens a conditional scope or branch |
| `-hanem` | `-else` | else — sibling branch when `-ha` / `-if` condition fails |
| `-különben-ha` | `-elif` | else-if — chained conditional branch |

---

## Loops

Loops are named scopes suffixed with a repetition marker. The condition that controls the loop is provided by a `-ha` / `-if` root in the same sentence.

### While loop — `-míg` / `-while`

Repeats the scope while the condition holds:

=== "Hungarian"
    ```ragul
    duplázó-nk-míg
        szám-d.
        határ-d.
        szám-kétszeres-t  szám-határ-alatt-ha.

    x-be  3-t.
    x-be  x-duplázó-míg-t  100-val.
    // x doubles repeatedly until x >= 100 → result: 192
    ```

=== "English aliases"
    ```ragul
    duplázó-ours-while
        szám-yours.
        határ-yours.
        szám-kétszeres-obj  szám-határ-below-if.

    x->  3-obj.
    x->  x-duplázó-while-obj  100-with.
    // x doubles repeatedly until x >= 100 → result: 192
    ```

### Until loop — `-ig` / `-until`

Repeats until the condition becomes true:

=== "Hungarian"
    ```ragul
    x-be  x-növel-ig-t  x-100-felett-ha.
    // increment x UNTIL x is above 100
    ```

=== "English aliases"
    ```ragul
    x->  x-növel-until-obj  x-100-above-if.
    // increment x UNTIL x is above 100
    ```

### For-each — `-mindegyik` / `-each`

Applies a scope to every element of a collection:

=== "Hungarian"
    ```ragul
    elemfeldolgozó-nk-mindegyik
        elem-d.
        elem-kétszeres-t.

    lista-be  [1,2,3,4,5]-t.
    kimenet-be  lista-elemfeldolgozó-mindegyik-t.
    // [2,4,6,8,10]
    ```

=== "English aliases"
    ```ragul
    elemfeldolgozó-ours-each
        elem-yours.
        elem-kétszeres-obj.

    lista->  [1,2,3,4,5]-obj.
    output->  lista-elemfeldolgozó-each-obj.
    // [2,4,6,8,10]
    ```

### Accumulate / fold — `-gyűjt` / `-fold`

Folds a collection into a single value. The accumulator is supplied via `-val` / `-with`:

=== "Hungarian"
    ```ragul
    összesítő-nk-gyűjt
        elem-d.
        összeg-d.            // accumulator
        összeg-elem-össze-t. // add element to accumulator

    kimenet-be  lista-összesítő-gyűjt-t  0-val.
    // sums the list starting from 0
    ```

=== "English aliases"
    ```ragul
    összesítő-ours-fold
        elem-yours.
        total-yours.         // accumulator
        total-elem-add-obj.  // add element to accumulator

    output->  lista-összesítő-fold-obj  0-with.
    // sums the list starting from 0
    ```

### Early exit — `-megszakít` / `-break`

`-megszakít` / `-break` terminates a loop immediately. It always composes with `-ha` / `-if` so the exit is conditional:

=== "Hungarian"
    ```ragul
    kereső-nk-míg
        lista-d.
        cél-d.
        elem-be  lista-következő-t.
        elem-cél-egyenlő-ha
            elem-megszakít-t.
    ```

=== "English aliases"
    ```ragul
    kereső-ours-while
        lista-yours.
        target-yours.
        elem->  lista-következő-obj.
        elem-target-eq-if
            elem-break-obj.
    ```

### Loop suffix reference

| Hungarian | English | Meaning |
|---|---|---|
| `-míg` | `-while` | Repeat while condition holds |
| `-ig` | `-until` | Repeat until condition becomes true |
| `-mindegyik` | `-each` / `-every` | Apply to each element of a collection |
| `-gyűjt` | `-fold` / `-reduce` | Accumulate a result across a collection |
| `-megszakít` | `-break` | Early exit — terminates the current loop |

---

## The Functional Character of Ragul

Ragul's control structures are deeply functional by design:

- Suffix chains are **function composition**
- Scopes are **closures**
- Named conditionals and loops are **reusable transformations**, not imperative control flow

A conditional defined once becomes a suffix reusable anywhere. A loop body defined once can be mapped over any collection. The same mechanisms that define functions define control structures — there is no separate syntax.
