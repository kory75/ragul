# Ragul Language Specification
**Version:** 1.0 — Complete  
**Status:** Work in Progress  
**Author:** Kornel Farkas  

> *Ragul* — from Hungarian *rag* (suffix/affix) + *-ul* (the suffix meaning "in the manner of a language", as in *magyarul* = in Hungarian). A language named by applying a suffix to the word for suffix. Self-referential by design.

---

## 1. Design Philosophy

Ragul is an experimental programming language whose core logic is modelled on **agglutinative grammar** — specifically the structural principles of Hungarian. Rather than using Hungarian words as commands, Ragul takes the *architecture* of the language as its computational model.

The central idea: **meaning is built by stacking suffixes onto a root**, each suffix adding exactly one layer of semantic transformation. A Ragul word is not just a name — it is a pipeline.

Key properties that follow from this:
- No brackets for structure — suffix chains carry all meaning
- Free word order — roles are encoded in suffixes, not position
- A function call is a suffix, not a separate construct
- A scope definition and a function definition are the same thing

---

## 2. Syntax

### 2.1 The Sentence

The base unit of Ragul is a **sentence** — multiple roots interacting, terminated by a full stop.

```
root₁-suffixes  root₂-suffixes  root₃-suffixes.
```

Because every root's role is encoded in its suffix chain, **word order is free**. These sentences are identical:

```
x-ból  kimenet-ba  másol-va.
kimenet-ba  másol-va  x-ból.
másol-va  x-ból  kimenet-ba.
```

### 2.2 The Word

A Ragul word is a root followed by a suffix chain. The suffix stack follows a fixed hierarchy:

```
root - [possession] - [aspect]* - [action] - [error] - case
```

| Layer | Position | Role |
|---|---|---|
| Root | Base | The thing being described |
| Possession | Innermost suffix | Ownership / scope / lifetime |
| Aspect(s) | Middle (repeatable) | Transformations applied to the root |
| Action | After aspects | Executes the operation (`-va` / `-ve`) |
| Error | After action | Propagates failure upward (`-e`) |
| Case | Outermost suffix | The role this word plays in the sentence |

### 2.3 Suffix Stacking

Aspect suffixes stack left to right, each operating on the result of the previous. This encodes a mini-pipeline inside a single word:

```
data-szűrve-szűrve-rendezve-ból
// data → filter → filter → sort → FROM
```

Multiple `-val` (with/instrument) arguments bind to aspects in left-to-right order:

```
data-szűrve-szűrve-rendezve-ból  3-felett-val  10-alatt-val  kimenet-ba  másol-va.
// FROM data→filter(>3)→filter(<10)→sort,  INTO output,  AS copy
```

### 2.4 Suffix Aliases

Each suffix has a canonical form plus optional aliases. The parser treats all aliases as identical. Programmers choose whichever reads naturally to them.

| Role | Canonical | Hungarian | English | Symbol |
|---|---|---|---|---|
| Source (from) | `-ból` | `-ból` | `-from` | `-<` |
| Target (into) | `-ba` / `-be` | `-ba` / `-be` | `-into` | `->` |
| Instrument (with) | `-val` | `-val` | `-with` | `-&` |
| Context (at/scope) | `-nál` | `-nál` | `-at` | `-@` |
| Role (acting as) | `-ként` | `-ként` | `-as` | `-:` |
| Object (acted on) | `-t` | `-t` | `-it` | `-*` |
| Action (execute) | `-va` / `-ve` | `-va` / `-ve` | `-doing` | `-!` |
| Error propagation | `-e` | `-e` | `-else-fail` | `-?` |

Mixed alias usage within the same file is permitted — the parser does not enforce consistency.

### 2.5 Assignment

Assignment is not special syntax — it is an ordinary sentence. The target carries `-be` (into) and the value carries `-t` (accusative — the thing being placed):

```
x-be  3-t.
lista-be  [1, 2, 3]-t.
üdvözlet-be  "hello"-t.
```

`-be` is the front-vowel harmonic variant of `-ba`. Both mean *into* — the choice follows vowel harmony with the root. No type annotation is required — the compiler infers types from the value.

There is no special assignment operator or syntax. Assignment is just a sentence where a value flows into a named target.

---

## 3. Type System

### 3.1 Inference

Ragul is **inferred typed**. Types are never declared explicitly — the compiler traces them from usage. No ceremony required:

```
x-be  3-t.           // compiler: x is Szám
y-be  "hello"-t.     // compiler: y is Szöveg
lista-be  [1,2,3]-t. // compiler: lista is Lista-Szám
```

### 3.2 Core Types

| Type | Meaning | Examples |
|---|---|---|
| `Szám` | Numbers, measurements, coordinates | `3`, `3.14`, `-7` |
| `Szöveg` | Strings, text, symbols | `"hello"`, `"adat.txt"` |
| `Lista` | Collections, structures | `[1,2,3]`, `["a","b"]` |
| `Logikai` | Booleans, logical values | `igaz`, `hamis` |
| `Hiba` | Error values | propagated via `-e` |

Types are capitalised to distinguish them from variable roots, which are lowercase.

### 3.3 Generic Types — `Lista-T` Notation

`Lista` is a generic type — it always carries an element type, written as a suffix chain:

```
Lista-Szám        // a list of numbers
Lista-Szöveg      // a list of strings
Lista-Logikai     // a list of booleans
Lista-Lista-Szám  // a list of lists of numbers
```

This notation is consistent with the rest of Ragul — types are built by suffixing, exactly as words are. `Lista` is the root, the element type is its suffix. Nesting composes naturally by continuing the chain.

The compiler always infers the full concrete type from usage:

```
számok-be    [1,2,3]-t.         // Lista-Szám
szavak-be    ["a","b","c"]-t.   // Lista-Szöveg
mátrix-be    [[1,2],[3,4]]-t.   // Lista-Lista-Szám
```

**Type preservation through suffix chains** — collection suffixes that do not change the element type preserve it automatically. The compiler tracks the element type through the chain:

```
lista-ból  rendezve-val  szűrve-val.

számok-be     [3,1,4,1,5]-t.                // Lista-Szám
rendezett-be  számok-rendezve-t.            // Lista-Szám — preserved
nagyok-be     rendezett-3-felett-szűrve-t.  // Lista-Szám — preserved
```

A suffix that changes element type declares the new type explicitly in its contract:

```
// -szöveggé on a Lista maps each element — returns Lista-Szöveg
számok-szöveggé-ből  kimenet-be  ír-va.  // Lista-Szöveg
```

### 3.4 The `vagy` Compound Type

`vagy` (meaning *or*) is the type that wraps any fallible result — a value that is either a success type or a failure type. It follows the same suffix-chain notation as `Lista`:

```
vagy-Szöveg-vagy-Hiba            // either a Szöveg, or a Hiba
vagy-Szám-vagy-Hiba              // either a Szám, or a Hiba
vagy-Lista-Szám-vagy-Hiba        // either a Lista-Szám, or a Hiba
vagy-Szám-vagy-Szöveg-vagy-Hiba  // three-way — rare, but legal
```

The notation is unified — `vagy` and `Lista` both build compound types by suffixing. The compiler knows any `vagy` type requires both cases to be handled before the value is used. See section 10 for error handling details.

### 3.5 Dual Type Enforcement

Type checking operates at two independent levels:

**Root guard** — does the root's type support this suffix at all?  
**Suffix guard** — does the suffix's declared contract accept the root's specific type?

Both must pass. Failure messages identify which guard failed and why:

```
"hello"-felett-ból  5-val  kimenet-ba.
// Root guard FAIL: "hello" is Szöveg — suffix -felett expects Szám
```

Element type mismatches are also caught:

```
szavak-be  ["a","b","c"]-t.        // Lista-Szöveg
szavak-3-felett-szűrve-t.
// Suffix guard FAIL: -felett expects Szám element — got Szöveg
```

### 3.6 Suffix Type Contracts

Each suffix declares what it expects and what it produces. Collection suffixes use `Lista-T` notation to express type preservation — `T` denotes *any concrete type* that flows through unchanged:

| Suffix | Expects | Produces | Arg type |
|---|---|---|---|
| `-felett` | `Szám` | `Logikai` | `Szám` |
| `-alatt` | `Szám` | `Logikai` | `Szám` |
| `-rendezve` | `Lista-T` | `Lista-T` | — |
| `-szűrve` | `Lista-T` | `Lista-T` | condition |
| `-fordítva` | `Lista-T` | `Lista-T` | — |
| `-hossz` | `Lista-T` or `Szöveg` | `Szám` | — |
| `-szöveggé` | `Szám` | `Szöveg` | — *(bridge)* |
| `-számmá` | `Szöveg` | `vagy-Szám-vagy-Hiba` | — *(bridge, fallible)* |

Bridge suffixes explicitly convert between types and must be used when chaining across type boundaries. User-defined generic suffixes (suffixes that use `T` in their own contracts) are a future extension.

### 3.7 Vowel Harmony (Optional)

Inspired by Hungarian vowel harmony, Ragul supports an optional **type harmony** warning system. Suffix chains that cross types without a bridge suffix can be flagged.

Controlled by project config:

```
// ragul.config
harmony: warn     // warn on dissonant chains (default)
harmony: strict   // treat as compile error
harmony: off      // silent
```

This feature is informational — it never blocks compilation unless `strict` is set.

---

## 4. Custom Suffix Declarations

### 4.1 Suffixes and Scopes Are the Same Thing

Every named scope simultaneously defines a suffix. There is no separate suffix declaration syntax — declaring a scope *is* declaring a suffix. The standard library's built-in suffixes (`-felett`, `-szűrve`, `-rendezve`, etc.) are defined using exactly the same mechanism as user-defined ones. The only difference is that some standard library suffixes may have native implementations for performance, but their interface is identical.

This means the answer to "how do I define a custom suffix?" is: **define a named scope.**

### 4.2 Type Annotations with `-ként`

The existing `-ként` suffix (meaning *acting as / in the role of*) provides type annotation. It attaches to parameter roots (`-d`) and the return value to declare what types are expected and produced:

```
kétszeres-unk
    szám-d  Szám-ként.
    szám-szám-össze-t  Szám-ként.
```

Reading naturally: *"szám, passed in, acting as a Szám"* — and the return *"acting as a Szám"*. No new syntax — `-ként` already exists, this is just a new position for it.

A suffix that transforms type (bridge):

```
szöveggé-unk
    szám-d  Szám-ként.
    szám-formáz-t  Szöveg-ként.
```

A suffix with a `-val` argument:

```
felett-unk
    érték-d  Szám-ként.
    küszöb-d  Szám-ként.
    érték-küszöb-nagyobb-t  Logikai-ként.
```

Parameters appear in order — the first `-d` receives the root, subsequent `-d` roots receive `-val` arguments left-to-right, matching the calling convention in section 5.2.

### 4.3 Fallible Suffixes — `vagy` Return Types

A suffix that can fail declares its return type using the `vagy-X-vagy-Y-ként` compound form:

```
fájlolvasó-unk
    útvonal-d  Szöveg-ként.
    útvonal-fájlról-ből  olvas-va-t  vagy-Szöveg-vagy-Hiba-ként.
```

Reading: *"acting as either a Szöveg or a Hiba"* — the caller must handle both cases. The `vagy...vagy` pattern mirrors Hungarian *"either...or"* naturally.

Three-way compounds are legal when genuinely needed:

```
vagy-Szám-vagy-Szöveg-vagy-Hiba-ként
```

In practice, if `Hiba` appears in every fallible suffix's return type, defining a shared `Hiba` type (see section 9) keeps declarations concise.

### 4.4 Enforcement

Type annotations on suffix declarations follow the same enforcement model as the harmony system — controlled by `ragul.config`:

```
// ragul.config
típus: warn     // warn on contract violations (default)
típus: strict   // treat as compile error
típus: off      // silent — inference only
```

This keeps the compiler simple while allowing projects that want hard guarantees to opt into them. The default `warn` mode surfaces mismatches without blocking compilation.

### 4.5 Annotations Are Optional

Type annotations are never required. An unannotated scope still works — the compiler infers types from the body. Annotations are declarations of *intent*, useful for:

- Public suffixes others will call (library code)
- Bridge suffixes where the type change is non-obvious
- Any suffix returning `vagy` — callers need to know the failure type

A private helper scope used only once needs no annotation.

### 4.6 Full Example

A small library of annotated suffixes:

```
// Numeric operations
kétszeres-unk
    szám-d  Szám-ként.
    szám-szám-össze-t  Szám-ként.

felére-unk
    szám-d  Szám-ként.
    szám-2-oszt-t  Szám-ként.

// Threshold filter — returns same type as input
szűrőhatár-unk
    lista-d  Lista-ként.
    küszöb-d  Szám-ként.
    lista-szűrve-ből  küszöb-felett-val  t  Lista-ként.

// Fallible file reader
fájlolvasó-unk
    útvonal-d  Szöveg-ként.
    útvonal-fájlról-ből  olvas-va-t  vagy-Szöveg-vagy-Hiba-ként.

// Bridge: number to formatted string
szöveggé-unk
    szám-d  Szám-ként.
    szám-formáz-t  Szöveg-ként.
```

Calling these is unchanged — suffix annotations are invisible at the call site:

```
x-be  3-t.
y-be  x-kétszeres-t.                          // y = 6

kimenet-be  adatok-szűrőhatár-t  5-val.        // filter list above 5

tartalom-be  "adat.txt"-fájlolvasó-va-e.       // fallible — propagate error
```

### 4.7 Suffix Declaration Quick Reference

```
// Simple suffix — one type in, same type out
név-unk
    param-d  Típus-ként.
    ...
    eredmény-t  Típus-ként.

// Suffix with argument
név-unk
    param-d    Típus-ként.     // root
    arg-d      Típus-ként.     // first -val argument
    ...
    eredmény-t  Típus-ként.

// Bridge suffix — changes type
név-unk
    param-d  Szám-ként.
    ...
    eredmény-t  Szöveg-ként.

// Fallible suffix
név-unk
    param-d  Típus-ként.
    ...
    eredmény-t  vagy-Típus-vagy-Hiba-ként.
```

---

## 5. Scope & Binding

### 5.1 Indentation as Scope

Ragul uses **indentation** (tabs) to define scope boundaries, similar to Python. A new indent level opens a new scope; dedenting closes it. Roots defined within a scope cease to exist when that scope closes.

```
számítás-unk
    x-be  3-t.
    y-be  10-t.
    eredmény-be  x-y-össze-t.
    eredmény-ből  kimenet-be  ír-va.

// x, y, eredmény do not exist here
```

### 5.2 Nested Scopes

Scopes nest freely. Inner scopes can reference roots from outer scopes, but not vice versa:

```
feldolgozás-unk
    lista-be  [1,2,3,4,5]-t.

    szűrés-unk
        kisebb-be  lista-szűrve-ből  3-alatt-val  t.
        kisebb-ből  kimenet-be  ír-va.

    // kisebb does not exist here
    lista-ből  kimenet-be  ír-va.
```

### 5.3 Possession Suffixes

Scoping is **implicit by default** — indentation handles it. Possession suffixes are optional and used only when explicit ownership needs to be expressed:

| Suffix | Aliases | Meaning |
|---|---|---|
| *(implicit)* | — | Belongs to current scope (default) |
| `-unk` / `-nk` | `-ours` | Explicitly owned by this scope |
| `-m` / `-em` | `-mine` | Immutable within this scope |
| `-d` / `-ed` | `-yours` | Passed in from outer scope (parameter) |
| `-ja` / `-je` | `-its` | Belongs to / references another root |

Usage mirrors `this.` in languages like C# — available when needed, not required:

```
feldolgozás-unk
    x-m-be  3-t.                         // immutable
    bemenet-d.                           // parameter — passed in from outside
    eredmény-unk-be  bemenet-szűrve-t.    // explicitly scoped result
```

---

## 6. Functions

### 6.1 The Unification: Scopes Are Suffixes

**A named scope and a custom suffix are the same thing.** Defining a named scope simultaneously defines a suffix that can be applied anywhere. There is no separate function declaration syntax.

```
kétszeres-unk
    szám-d.
    szám-szám-össze-t  Szám-ként.
```

This definition makes `-kétszeres` immediately available as an aspect suffix:

```
x-be  3-t.
y-be  x-kétszeres-t.                      // y = 6

lista-be  [1,2,3]-t.
lista-kétszeres-ből  kimenet-be  ír-va.  // [2,4,6]
```

### 6.2 Parameters

Parameters are roots marked with `-d` (yours — passed in). They receive values from the calling sentence via `-val` bindings, in left-to-right order:

```
szűrőhatár-unk
    lista-d.           // receives the root
    küszöb-d.          // receives the first -val argument
    lista-küszöb-felett-szűrve-t  Lista-ként.

// Called as:
kimenet-be  adatok-szűrőhatár-t  5-val.
// adatok → lista-d, 5 → küszöb-d
```

### 6.3 Return Value

The final unnamed result root of a scope is its return value — no explicit return keyword needed.

### 6.4 Conceptual Mapping

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

## 7. Execution Model

### 7.1 Internal Representation — Words as Vectors

Ragul does not use a traditional Abstract Syntax Tree (AST) internally. A word in Ragul is already a flat, ordered sequence of layers — and this maps directly onto a **vector** rather than a nested tree.

```
[ root | possession | aspect... | action | error | case ]
```

Each word is represented as a flat dataclass:

```python
@dataclass
class Word:
    root:       str
    possession: str | None
    aspects:    list[str]
    action:     str | None
    error:      bool
    case:       str
```

A sentence is a list of `Word` vectors. The compiler does not need to build and then traverse a tree — it reads the vectors directly, matches case roles (`-ból`, `-ba`, `-val`, etc.), and constructs a **dependency graph** from those relationships. This is more natural for Ragul than an AST because the suffix layer hierarchy is already flat and ordered by definition.

The dependency graph, not word order, drives evaluation. Free word order is safe because roles are encoded in the vectors themselves — position carries no meaning.

### 7.2 Compilation Target

For the initial implementation, Ragul interprets the sentence graph directly from the vector representation — no bytecode phase. This keeps the MVP simple and fast to iterate on. Bytecode compilation is a future target once the language semantics are stable.

### 7.3 Evaluation Strategy

Ragul uses **lazy evaluation**. Sentences are declarations of relationships, not sequences of steps. The compiler builds a dependency graph from the case roles in each word vector and evaluates roots in dependency order — not in the order they appear in the sentence.

This is what makes free word order safe:

```
kimenet-ba  data-szűrve-ból  3-felett-val  másol-va.
```

The compiler sees that `kimenet-ba` depends on `data-szűrve-ból` and evaluates the source first, regardless of its position in the sentence.

**MVP note:** the initial implementation may use eager evaluation within pure scopes for simplicity, with `-hatás` already enforced as eager. Full lazy evaluation is introduced once the core interpreter is stable.

### 7.4 Scope Lifetime

Roots are allocated when their scope opens and released when it closes. Lazy evaluation means a root is not computed until its value is first needed — but its lifetime is still bounded by its scope's indentation boundary.

---

## 8. Control Flow

Control flow in Ragul is expressed entirely through suffixes and named scopes — no reserved keywords. The same scope-as-suffix unification that makes functions work also makes conditionals and loops composable and reusable.

### 8.1 Conditionals

A conditional is a named scope suffixed with `-ha` (if / given that). The `-ha` suffix signals to the compiler that this scope contains branching logic.

**Simple if:**
```
pozitív-nk-ha
    szám-d.
    szám-0-felett-ha
        szám-kétszeres-t.
```

**If / else** — `-hanem` is the else branch, a sibling block at the same indent level as the `-ha` branch it pairs with:
```
előjelváltó-nk-ha
    szám-d.
    szám-0-felett-ha
        szám-kétszeres-t.
    -hanem
        szám-felére-t.
```

**If / else-if / else chain** — `-különben-ha` (otherwise-if) extends the chain. Each link carries its own condition inline:
```
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

**Calling a conditional scope as a suffix** — exactly like any other named scope:
```
x-be  75-t.
kategória-be  x-besoroló-ha-t.
// kategória = "közepes"
```

### 8.2 Conditional Suffix Reference

| Suffix | Meaning |
|---|---|
| `-ha` | if / given that — opens a conditional scope or branch |
| `-hanem` | else — sibling branch when `-ha` condition fails |
| `-különben-ha` | else-if — chained conditional branch |

### 8.3 Loops

Loops are named scopes suffixed with a repetition marker. The condition that controls the loop is provided by a `-ha` root in the same sentence — using the same mechanism as standalone conditionals.

**While loop** — `-míg` repeats the scope while the condition holds:
```
duplázó-nk-míg
    szám-d.
    határ-d.
    szám-kétszeres-t  szám-határ-alatt-ha.

x-be  3-t.
x-be  x-duplázó-míg-t  100-val.
// x doubles repeatedly until x >= 100 → result: 192
```

**Until loop** — `-ig` repeats until the condition becomes true:
```
x-be  x-növel-ig-t  x-100-felett-ha.
// increment x UNTIL x is above 100
```

**For each** — `-mindegyik` applies a scope to every element of a collection:
```
elemfeldolgozó-nk-mindegyik
    elem-d.
    elem-kétszeres-t.

lista-be  [1,2,3,4,5]-t.
kimenet-be  lista-elemfeldolgozó-mindegyik-t.
// [2,4,6,8,10]
```

**Accumulate / reduce** — `-gyűjt` folds a collection into a single value. The accumulator is supplied via `-val`:
```
összesítő-nk-gyűjt
    elem-d.
    összeg-d.           // accumulator
    összeg-elem-össze-t.      // add element to accumulator

kimenet-be  lista-összesítő-gyűjt-t  0-val.
// sums the list starting from 0
```

**Early exit** — `-megszakít` (break) terminates a loop immediately. It composes with `-ha` so the exit is always conditional:
```
kereső-nk-míg
    lista-d.
    cél-d.
    elem-be  lista-következő-t.
    elem-cél-egyenlő-ha
        elem-megszakít-t.
```

### 8.4 Loop Suffix Reference

| Suffix | Aliases | Meaning |
|---|---|---|
| `-míg` | `-while` | Repeat while condition holds |
| `-ig` | `-until` | Repeat until condition becomes true |
| `-mindegyik` | `-each`, `-every` | Apply to each element of a collection |
| `-gyűjt` | `-fold`, `-reduce` | Accumulate a result across a collection |
| `-megszakít` | `-break` | Early exit — terminates the current loop |

### 8.5 The Functional Character of Ragul

Ragul's design has emerged as deeply functional — and this is consistent, not accidental. Suffix chains are function composition. Scopes are closures. Lazy evaluation is pure. Named conditionals and loops are reusable transformations rather than imperative control structures.

This raises a natural question about object-oriented programming, explored in section 13.

---

## 9. I/O and Side Effects

### 9.1 I/O as a Suffix Family

I/O in Ragul is not special-cased by the compiler. Every I/O channel is a named scope defined with `-nk-hatás` (the effect scope suffix). This makes every channel a suffix that can appear in any suffix chain, while the compiler enforces that it can only be called from within another effect scope.

### 9.2 The Effect Scope — `-hatás`

Lazy evaluation means sentences only execute when their result is needed. A sentence that writes to screen has no result — so the lazy evaluator would never run it. The `-hatás` suffix solves this by marking a scope as **eager**: everything inside executes in order, top to bottom, unconditionally.

```
program-nk-hatás
    x-be  "helló világ"-t.
    x-képernyőre-va.
```

Two rules enforced by the compiler:

- Inside a `-hatás` scope, all sentences execute eagerly in order
- A pure scope (without `-hatás`) cannot call an effectful scope — this is a compile error

```
tiszta-számítás-unk
    x-be  3-t.
    x-képernyőre-va.    // ERROR: effectful suffix called from pure scope
```

### 9.3 Standard I/O Channels

Every channel is a built-in scope defined with `-nk-hatás`. The channel name carries its own case suffix indicating direction — `-ra` / `-re` (onto) for write, `-ról` / `-ről` (from) for read:

| Channel root | Direction | Meaning |
|---|---|---|
| `képernyőre` | write | Console / stdout |
| `bemenetről` | read | Console / stdin |
| `fájlra` | write | File system write |
| `fájlról` | read | File system read |
| `hálózatra` | write | Network write |
| `hálózatról` | read | Network read |
| `stderr` | write | Stderr / error output |

All channels work identically — same suffix mechanism, different target. Swapping the channel root is the only change needed:

```
program-nk-hatás
    x-be  "helló"-t.
    x-képernyőre-va.    // write to console
    x-fájlra-va.        // write to file — same sentence structure
    x-stderr-va.        // write to stderr — same sentence structure
```

### 9.4 How Channels Are Defined

Channels are not compiler magic — they are Ragul scopes, defined exactly like any other scope with `-nk-hatás`. The standard library provides the built-in channels, but users can define their own:

```
adatbázisba-nk-hatás
    lekérdezés-d.
    // implementation: execute lekérdezés against database
```

Once defined, `adatbázisba` becomes a suffix usable anywhere — identically to built-in channels:

```
program-nk-hatás
    sql-be  "SELECT * FROM users"-t.
    sql-adatbázisba-va.
```

### 9.5 Reading Input

Reading is also an effect operation — it reaches outside the program boundary. The pattern uses the read channel as a source with `-ből`:

```
program-nk-hatás
    input-be  bemenetről-ből  olvas-va-t.
    input-képernyőre-va.
```

### 9.6 Suffix Reference

| Suffix | Meaning |
|---|---|
| `-nk-hatás` | Defines an effect scope — eager evaluation, I/O permitted |
| `-hatás` | Marks a scope as effectful when composing |
| `-va` / `-ve` | Action — executes the operation |
| `-ként` | Role — acting in a capacity (as a type, as an agent) |
| `-ből` / `-ről` | Source — FROM (read direction) |
| `-ra` / `-re` | Target embedded in channel name (write direction) |

---

## 10. Error Handling

### 10.1 Design Principles

Ragul uses two rules for errors:

- Unhandled errors are **fatal** — they terminate the program
- Errors propagate **automatically** up the suffix chain via the `-e` suffix

There are no exceptions, no `try/catch` keywords. Error handling follows the same suffix and scope model as everything else.

### 10.2 The `vagy` Type

Any operation that can fail returns a `vagy` — a value that is either a success result or an error (see section 3.3). The full form names both sides:

```
// vagy-Szöveg-vagy-Hiba = either a Szöveg OR a Hiba
eredmény-be  "adat.txt"-fájlolvasó-va.
// eredmény is vagy-Szöveg-vagy-Hiba
```

The compiler knows `eredmény` is a `vagy` type and enforces that both cases are handled before the value is used.

### 10.3 Error Propagation — `-e`

The `-e` suffix sits after the action suffix `-va` / `-ve` in the chain. It means: *"if this operation produced an error, propagate it upward immediately — short-circuit the rest of the chain."*

```
root - [possession] - [aspect]* - action(-va) - [error(-e)] - case
```

```
tartalom-be  "adat.txt"-fájlolvasó-va-e.
// call fájlolvasó — if error, propagate up immediately
// if success, bind result to tartalom
```

Without `-e`, the caller must handle the `vagy` type manually. With `-e`, errors bubble up to the nearest `-hibára` boundary.

### 10.4 Error Handling Boundary — `-hibára`

`-hibára` is a sibling block to the main scope body — exactly like `-hanem` is to `-ha`. It catches any error that propagates up from within the scope:

```
program-nk-hatás
    tartalom-be  "adat.txt"-fájlolvasó-va-e.
    adat-be  tartalom-elemző-va-e.
    adat-képernyőre-va.
    -hibára
        "feldolgozási hiba"-képernyőre-va.
```

If any `-va-e` sentence fails, execution jumps immediately to `-hibára`. If there is no `-hibára` and an error reaches the top of the program — fatal, program terminates.

### 10.5 Error Values

Errors carry a message. A named error is just a root assigned an error value:

```
hiba-be  "fájl nem található"-t.
```

Inside a `-hibára` block, the error is accessible as `hiba`:

```
program-nk-hatás
    tartalom-be  "adat.txt"-fájlolvasó-va-e.
    tartalom-képernyőre-va.
    -hibára
        hiba-képernyőre-va.    // print the error message
```

### 10.6 A Complete Example

```
// Fallible file reader
fájlolvasó-unk
    útvonal-d  Szöveg-ként.
    útvonal-fájlról-ből  olvas-va-t  vagy-Szöveg-vagy-Hiba-ként.

// Fallible JSON parser
elemző-unk
    szöveg-d  Szöveg-ként.
    szöveg-json-va-t  vagy-Lista-vagy-Hiba-ként.

// Program — handles errors at the boundary
program-nk-hatás
    tartalom-be  "adat.txt"-fájlolvasó-va-e.
    adat-be  tartalom-elemző-va-e.
    adat-képernyőre-va.
    -hibára
        "hiba: "-hiba-összefűz-va  képernyőre-va.
```

### 10.7 Suffix Reference

| Suffix | Position | Meaning |
|---|---|---|
| `-va` / `-ve` | After aspects | Execute the action |
| `-e` | After `-va` / `-ve` | Propagate error upward if failure |
| `-hibára` | Sibling block | Catches errors propagated within the scope |
| `vagy` | Type prefix | Wraps a fallible result — `vagy-X-vagy-Y` |
| `Hiba` | Type | The error type — accessible inside `-hibára` as `hiba` |

---

## 11. Module System

### 11.1 Design Principles

A module in Ragul is a named scope that spans a file. Because scopes are already the fundamental unit of organisation, modules introduce no new concepts — they are scopes with two additional properties: they have an explicit name independent of the filename, and they declare a public/private boundary.

Everything that applies to scopes applies to modules: their suffixes compose freely with any other suffix chain, and the compiler treats built-in library modules identically to user-defined ones.

### 11.2 Declaring a Module

A module is declared at the top level of a file using `-nk-modul`:

```
matematika-nk-modul
    kétszeres-unk
        szám-d  Szám-ként.
        szám-szám-össze-t  Szám-ként.

    gyök-unk
        szám-d  Szám-ként.
        szám-négyzetgyök-t  Szám-ként.

    segéd-nk-m    // private — -m (mine) means not exported
        szám-d  Szám-ként.
        szám-2-oszt-t  Szám-ként.
```

The module name (`matematika`) is explicit and independent of the filename. The file can be named anything — the compiler uses the declared name, not the filesystem name.

**Visibility** follows the existing possession suffix model — no new syntax needed:

| Possession | Meaning in module context |
|---|---|
| *(none)* / `-unk` | Public — exported, callable by importers |
| `-m` | Private — internal implementation detail, not exported |

This reuses `-m` (mine — belongs to this scope exclusively) exactly as it already means in non-module scopes.

### 11.3 Importing a Module

Importing uses `-ból` (from) — the same suffix that already means *from* in every other context. A top-level sentence beginning with `-ból` is recognised by the compiler as an import declaration:

**Whole module import:**
```
matematika-ból.
```

All public suffixes of `matematika` become available in the current scope.

**Selective import** — `-val` (with) selects specific suffixes:
```
matematika-ból  kétszeres-val  gyök-val.
```

Only `-kétszeres` and `-gyök` are imported. Other public suffixes are ignored.

**Aliasing** — `-ként` (acting as) renames a suffix on import:
```
matematika-ból  kétszeres-dupla-ként-val.
// -kétszeres is imported and available locally as -dupla
```

Multiple aliases in one statement:
```
matematika-ból  kétszeres-dupla-ként-val  gyök-arány-ként-val.
```

All forms compose naturally — the vocabulary is entirely existing suffixes.

### 11.4 Module Resolution

Module paths are not written in source code. The compiler resolves module names to files using a fixed search order:

1. Same directory as the importing file
2. Project search paths listed in `ragul.config`
3. Standard library location (built into the compiler)

```
// ragul.config
modulok: ["./lib", "./vendor"]
```

This keeps source files path-independent. The single place to configure search paths is `ragul.config`. If a module name cannot be resolved, the compiler reports it as an error before type checking begins.

### 11.5 Circular Dependencies

Lazy evaluation naturally tolerates many dependency patterns that eager languages cannot. However, true circular definitions (where A's value depends on B and B's value depends on A with no lazy boundary between them) are a compile error. The compiler detects these during dependency graph construction and reports the cycle explicitly.

### 11.6 A Complete Example

```
// matematika.ragul
matematika-nk-modul

    kétszeres-unk
        szám-d  Szám-ként.
        szám-szám-össze-t  Szám-ként.

    gyök-unk
        szám-d  Szám-ként.
        szám-négyzetgyök-t  Szám-ként.

    összeg-unk
        lista-d  Lista-ként.
        lista-összesítő-gyűjt-ből  0-val  t  Szám-ként.

    segéd-nk-m    // private — not exported
        szám-d  Szám-ként.
        szám-2-oszt-t  Szám-ként.


// main.ragul
matematika-ból  kétszeres-val  gyök-val.

program-nk-hatás
    x-be  9-t.
    y-be  x-gyök-t.
    z-be  y-kétszeres-t.
    z-képernyőre-va.
    // prints 6  (√9 = 3, 3×2 = 6)


// Using alias
matematika-ból  összeg-szumma-ként-val.

program-nk-hatás
    lista-be  [1,2,3,4,5]-t.
    lista-szumma-ből  kimenet-be  ír-va.
    // prints 15
```

### 11.7 Suffix Reference

| Syntax | Meaning |
|---|---|
| `név-nk-modul` | Declare a named module |
| `-m` on child scope | Private — not exported |
| `modul-ból.` | Import all public suffixes |
| `modul-ból  suffix-val.` | Import specific suffix |
| `modul-ból  suffix-alias-ként-val.` | Import with local alias |
| `modulok:` in `ragul.config` | Search paths for module resolution |

---

## 12. Standard Library

### 12.1 Two Tiers: Core and Modules

The standard library is split into two tiers:

**Core** — always available, no import needed. These are the arithmetic, comparison, and logical operations so fundamental that requiring an import would be noise. They are part of the language itself, compiled in alongside the case suffixes and possession suffixes.

**Library modules** — imported selectively using the module system (section 11). Each module groups related suffixes by the type they primarily operate on. Only what is needed is imported.

Built-in suffixes are defined using exactly the same mechanism as user-defined ones — they are pre-compiled Ragul scopes, not compiler magic. The standard library is just a set of modules that ship with the compiler.

### 12.2 Core Suffixes

Core suffixes are always in scope. No import statement is needed or possible for these.

**Arithmetic — Szám → Szám**

| Suffix | Args | Meaning |
|---|---|---|
| `-össze` | `Szám-val` | Add |
| `-kivon` | `Szám-val` | Subtract |
| `-szoroz` | `Szám-val` | Multiply |
| `-oszt` | `Szám-val` | Divide |
| `-maradék` | `Szám-val` | Modulo (remainder) |

```
x-be  10-t.
y-be  x-3-össze-t.       // 13
z-be  y-2-szoroz-t.      // 26
m-be  z-5-maradék-t.     // 1
```

**Comparison — Szám → Logikai**

| Suffix | Args | Meaning |
|---|---|---|
| `-felett` | `Szám-val` | Greater than |
| `-alatt` | `Szám-val` | Less than |
| `-legalább` | `Szám-val` | Greater than or equal |
| `-legfeljebb` | `Szám-val` | Less than or equal |

**Equality — any → Logikai**

| Suffix | Args | Meaning |
|---|---|---|
| `-egyenlő` | `any-val` | Equal — works on any type |
| `-nemegyenlő` | `any-val` | Not equal |

**Logical — Logikai → Logikai**

| Suffix | Args | Meaning |
|---|---|---|
| `-nem` | — | Negate (NOT) |
| `-és` | `Logikai-val` | AND |
| `-vagy` | `Logikai-val` | OR |

```
feltétel-be  x-10-felett-t.
másik-be  y-0-egyenlő-nem-t.
mindkettő-be  feltétel-másik-és-t.
```

**String concatenation — Szöveg → Szöveg**

| Suffix | Args | Meaning |
|---|---|---|
| `-összefűz` | `Szöveg-val` | Concatenate two strings |

```
üdvözlet-be  "helló "-"világ"-összefűz-t.
```

### 12.3 `matematika` Module

Advanced numeric operations. Import what is needed:

```
matematika-ból  négyzetgyök-val  hatvány-val.
```

| Suffix | Input | Output | Args | Meaning |
|---|---|---|---|---|
| `-négyzetgyök` | `Szám` | `Szám` | — | Square root |
| `-hatvány` | `Szám` | `Szám` | `Szám-val` | Power |
| `-abszolút` | `Szám` | `Szám` | — | Absolute value |
| `-kerekítve` | `Szám` | `Szám` | — | Round to nearest integer |
| `-padló` | `Szám` | `Szám` | — | Round down (floor) |
| `-plafon` | `Szám` | `Szám` | — | Round up (ceiling) |
| `-log` | `Szám` | `Szám` | `Szám-val` | Logarithm (base as arg) |
| `-sin` | `Szám` | `Szám` | — | Sine |
| `-cos` | `Szám` | `Szám` | — | Cosine |
| `-szöveggé` | `Szám` | `Szöveg` | — | Convert number to string *(bridge)* |

```
matematika-ból  négyzetgyök-val  hatvány-val  szöveggé-val.

program-nk-hatás
    x-be  9-t.
    y-be  x-négyzetgyök-t.            // 3.0
    z-be  2-10-hatvány-t.             // 1024
    szöveg-be  y-szöveggé-t.          // "3.0"
    szöveg-képernyőre-va.
```

### 12.4 `szöveg` Module

String operations. `-hossz` is shared with `lista` — the suffix works on both types, resolved by the type system at compile time.

```
szöveg-ből  hossz-val  nagybetűs-val  feloszt-val.
```

| Suffix | Input | Output | Args | Meaning |
|---|---|---|---|---|
| `-hossz` | `Szöveg` | `Szám` | — | Length in characters |
| `-nagybetűs` | `Szöveg` | `Szöveg` | — | Uppercase |
| `-kisbetűs` | `Szöveg` | `Szöveg` | — | Lowercase |
| `-tartalmaz` | `Szöveg` | `Logikai` | `Szöveg-val` | Contains substring |
| `-kezdődik` | `Szöveg` | `Logikai` | `Szöveg-val` | Starts with |
| `-végződik` | `Szöveg` | `Logikai` | `Szöveg-val` | Ends with |
| `-szelet` | `Szöveg` | `Szöveg` | `Szám-val Szám-val` | Slice (start, end) |
| `-csere` | `Szöveg` | `Szöveg` | `Szöveg-val Szöveg-val` | Replace (from, to) |
| `-feloszt` | `Szöveg` | `Lista-Szöveg` | `Szöveg-val` | Split by delimiter |
| `-formáz` | `Szöveg` | `Szöveg` | `any-val` | Format string with value |
| `-számmá` | `Szöveg` | `vagy-Szám-vagy-Hiba` | — | Parse to number *(bridge, fallible)* |

```
szöveg-ből  nagybetűs-val  feloszt-val  hossz-val  számmá-val.

program-nk-hatás
    mondat-be  "helló világ"-t.
    szavak-be  mondat-" "-feloszt-t.        // ["helló", "világ"]
    nagy-be    mondat-nagybetűs-t.          // "HELLÓ VILÁG"
    hossz-be   mondat-hossz-t.             // 11

    szám-be    "42"-számmá-va-e.           // fallible — propagate error
    szám-képernyőre-va.
    -hibára
        "nem szám"-képernyőre-va.
```

### 12.5 `lista` Module

Collection operations. `-hossz` works on `Lista` exactly as it does on `Szöveg`.

```
lista-ból  rendezve-val  szűrve-val  első-val.
```

| Suffix | Input | Output | Args | Meaning |
|---|---|---|---|---|
| `-hossz` | `Lista` | `Szám` | — | Number of elements |
| `-rendezve` | `Lista` | `Lista` | — | Sort ascending |
| `-rendezve-le` | `Lista` | `Lista` | — | Sort descending |
| `-szűrve` | `Lista` | `Lista` | condition | Filter by condition |
| `-fordítva` | `Lista` | `Lista` | — | Reverse |
| `-első` | `Lista` | `any` | — | First element |
| `-utolsó` | `Lista` | `any` | — | Last element |
| `-tartalmaz` | `Lista` | `Logikai` | `any-val` | Contains element |
| `-hozzáad` | `Lista` | `Lista` | `any-val` | Append element |
| `-eltávolít` | `Lista` | `Lista` | `any-val` | Remove first matching element |
| `-szelet` | `Lista` | `Lista` | `Szám-val Szám-val` | Slice (start, end) |
| `-egyedi` | `Lista` | `Lista` | — | Remove duplicates |
| `-lapítva` | `Lista-Lista` | `Lista` | — | Flatten one level |

```
lista-ból  rendezve-val  szűrve-val  hossz-val  első-val.

program-nk-hatás
    számok-be  [3,1,4,1,5,9,2,6]-t.
    egyediek-be   számok-egyedi-t.               // [3,1,4,5,9,2,6]
    rendezett-be  egyediek-rendezve-t.            // [1,2,3,4,5,6,9]
    nagyok-be     rendezett-5-felett-szűrve-t.    // [6,9]
    első-be       nagyok-első-t.                  // 6
    első-képernyőre-va.
```

### 12.6 Shared Suffix: `-hossz`

`-hossz` is defined in both `szöveg` and `lista` with the same name. The compiler resolves which definition applies from the type of the root — no ambiguity:

```
szöveg-ből  hossz-val.
lista-ból   hossz-val.

szó-be    "ragul"-t.
elemek-be  [1,2,3]-t.

szó-hossz-ből    kimenet-be  ír-va.    // 5  (Szöveg → Szám)
elemek-hossz-ből  kimenet-be  ír-va.   // 3  (Lista → Szám)
```

If both modules are imported, the compiler selects the correct `-hossz` from the root's type. If the type is ambiguous, the compiler reports an error and asks for a bridge or explicit type annotation.

### 12.7 Standard Library Module Summary

| Module | Import | Contents |
|---|---|---|
| *(core)* | *(always available)* | Arithmetic, comparison, equality, logical, `-összefűz` |
| `matematika` | `matematika-ból` | Advanced maths, `-szöveggé` bridge |
| `szöveg` | `szöveg-ből` | String operations, `-számmá` bridge |
| `lista` | `lista-ból` | Collection operations |

I/O channels (`képernyőre`, `fájlra`, `hálózatra`, etc.) are built-in effect scopes, available without import inside any `-hatás` scope — documented fully in section 9.

---

## 13. Concurrency

### 13.1 Design Principle

Ragul's concurrency model is **implicit parallelism** — the runtime automatically evaluates independent roots in parallel, derived directly from the dependency graph already constructed during compilation. No new syntax, no new concepts, nothing for the programmer to learn or configure.

This falls out of lazy evaluation for free. The compiler already knows which roots depend on which — roots with no shared dependencies are by definition safe to evaluate concurrently.

### 13.2 Implicit Parallelism

Independent sentences within a scope — those that neither read from nor write to the same roots — are evaluated in parallel by the runtime automatically:

```
// These three are independent — runtime evaluates in parallel
a-be  hosszú-számítás-1-t.
b-be  hosszú-számítás-2-t.
c-be  hosszú-számítás-3-t.

// This must wait for a, b, and c — dependency is explicit in the graph
eredmény-be  a-b-c-összesít-t.
```

The programmer writes normal Ragul. The runtime parallelises wherever the dependency graph allows. No annotations, no async/await, no thread management.

### 13.3 Parallel Write Detection

The compiler enforces one rule to make implicit parallelism safe: **two independent branches cannot write to the same root**. This is a compile-time error — data races are structurally impossible at runtime because they are caught before execution:

```
// Legal — independent roots, parallel safe
a-be  számítás-1-t.
b-be  számítás-2-t.

// Compile error — both sentences write to x
// parallel write conflict detected
x-be  számítás-1-t.
x-be  számítás-2-t.
```

The compiler detects this during dependency graph construction — the same phase that resolves word order. No additional analysis pass is needed.

### 13.4 Interaction with `-hatás`

Inside a `-hatás` scope, execution is **eager and sequential** — sentences run top to bottom in order, unconditionally. Implicit parallelism does not apply inside `-hatás`. This is consistent with the existing model: `-hatás` already surrenders lazy evaluation in exchange for ordered side effects, and concurrent I/O would undermine that ordering guarantee.

Pure scopes benefit from implicit parallelism. Effect scopes are sequential. The boundary is already enforced — no new rules needed.

### 13.5 Future Concurrency (Post-MVP)

Two extensions are deferred to later versions:

**Explicit parallel scopes** — a `-párhuzam` (parallel) scope that signals all children run concurrently and the scope completes when all finish, similar to `Promise.all`. Useful for explicit fan-out patterns like multiple API calls.

**Message passing** — long-running concurrent processes that communicate via channels, for server loops and producers/consumers. This would require new primitives and is the most complex extension.

Neither is needed for v1. Implicit parallelism covers the common case; the explicit extensions are additive when needed.

### 13.6 Summary

| Feature | v1 |
|---|---|
| Implicit parallelism | ✓ — automatic from dependency graph |
| Parallel write detection | ✓ — compile-time error |
| `-hatás` stays sequential | ✓ — no change to existing model |
| Explicit `-párhuzam` scope | Future |
| Message passing / channels | Future |

---

## 14. Tooling

### 14.1 Overview

Ragul's tooling is intentionally minimal for v1. Three components: the compiler with structured error messages, a TOML project config file, and a simple module path system. No build tool, no package registry, no code formatter in the first version — those are future additions.

---

### 14.2 Compiler Error Messages

The compiler produces structured, human-readable errors in English. Because Ragul encodes rich information in every suffix chain — layer position, type guard level, expected vs actual type — errors are precise by design.

**Error format:**

```
ERROR  [file]:[line]  [error code]
  [what went wrong — one sentence]
  [the offending word or sentence]
  [what was expected vs what was found]
  [suggestion, if one exists]
```

**Examples:**

Root guard failure — wrong type for suffix:
```
ERROR  main.ragul:12  E001
  Suffix -felett expects Szám, but root is Szöveg.
    "hello"-felett-ból  5-val  kimenet-ba.
    ^^^^^^^^
  Root "hello" is Szöveg — use a Szám root or add a -számmá bridge first.
```

Suffix layer order violation — suffix in wrong position:
```
ERROR  main.ragul:7  E002
  Case suffix -ból appears before action suffix -va in chain.
    adat-ból-összefűz-va-t.
         ^^^
  Case suffix must be outermost. Expected order: root-aspect-action-case.
```

Parallel write conflict — same root written twice:
```
ERROR  main.ragul:15  E003
  Root x is written by two independent sentences — parallel write conflict.
    x-be  számítás-1-t.   (line 15)
    x-be  számítás-2-t.   (line 16)
  Two independent branches cannot write to the same root.
  Rename one target root or sequence these sentences with a dependency.
```

Effectful call from pure scope:
```
ERROR  main.ragul:9  E004
  Effectful suffix -képernyőre called from pure scope tiszta-számítás.
    x-képernyőre-va.
    ^^^^^^^^^^^^^^^^
  Effect suffixes can only be called from -hatás scopes.
  Wrap this scope with -nk-hatás or remove the effectful call.
```

Unhandled `vagy` type:
```
ERROR  main.ragul:22  E005
  Root tartalom is vagy-Szöveg-vagy-Hiba — both cases must be handled.
    tartalom-be  "adat.txt"-fájlolvasó-va.
  Use -va-e to propagate the error upward, or handle -hibára explicitly.
```

**Error code reference:**

| Code | Category | Description |
|---|---|---|
| E001 | Type | Root guard failure — wrong type for suffix |
| E002 | Syntax | Suffix layer order violation |
| E003 | Concurrency | Parallel write conflict |
| E004 | Effect | Effectful call from pure scope |
| E005 | Type | Unhandled `vagy` type |
| E006 | Scope | Root referenced outside its scope |
| E007 | Module | Module name cannot be resolved |
| E008 | Type | Suffix contract violation — argument type mismatch |
| E009 | OOP | Field mutation outside `-hatás` scope |
| W001 | Harmony | Type harmony warning — chain crosses types without bridge |

Warnings (`W`) respect the `harmony` config setting. Errors (`E`) always halt compilation.

---

### 14.3 `ragul.config`

Every Ragul project has a `ragul.config` file in the project root, written in TOML. All keys are optional — the compiler uses documented defaults when a key is absent.

**Full `ragul.config` reference:**

```toml
# ragul.config

[projekt]
nev   = "en-projektom"   # project name
verzio = "0.1.0"          # project version
belepes = "main.ragul"    # entry point file (default: main.ragul)

[fordito]
cel     = "bytecode"      # compilation target: "bytecode" | "interpret" (default: interpret)
python  = "3.11"          # minimum Python version for the runtime

[modulok]
utvonalak = [             # module search paths, in priority order
  "./lib",
  "./vendor"
]

[ellenorzes]
harmonia = "warn"         # "warn" | "strict" | "off"  (default: warn)
tipus    = "warn"         # "warn" | "strict" | "off"  (default: warn)

[hibak]
nyelv = "en"              # error message language: "en" (default, only option in v1)
```

**Minimal `ragul.config`** — for a simple single-file project, just this is enough:

```toml
[projekt]
nev = "helló-világ"
```

Everything else uses defaults.

---

### 14.4 Module Resolution

When the compiler encounters an import (`matematika-ból.`), it resolves the module name to a file using this search order:

1. Same directory as the importing file
2. Paths listed in `modulok.utvonalak`, in order
3. The Ragul standard library (built into the runtime)

The first match wins. If no match is found, the compiler raises `E007` before any type checking begins.

**File naming convention:** a module named `matematika` is expected in a file called `matematika.ragul`. The filename must match the module name declared inside the file with `-nk-modul`. If they differ, the compiler raises `E007` with a note suggesting the mismatch.

---

### 14.5 Running a Ragul Program

The compiler is invoked from the command line. Three modes for v1:

```bash
# Run directly (interpret mode — default for development)
ragul futtat main.ragul

# Check types and contracts without running
ragul ellenoz main.ragul

# Compile to bytecode
ragul fordít main.ragul
```

Command names are Hungarian, consistent with the language's identity. Each command accepts `--help` for usage details.

**Output and exit codes:**

| Condition | Exit code |
|---|---|
| Success | 0 |
| Compile error | 1 |
| Runtime error | 2 |
| Unhandled `Hiba` (fatal) | 3 |

---

### 14.6 Package Management (v1)

Package management in v1 is deliberately minimal — local modules and path configuration only. There is no package registry or install command in this version.

External dependencies are managed by placing `.ragul` files in a directory listed in `modulok.utvonalak`. The recommended convention is a `vendor/` directory committed alongside the project:

```
my-project/
  main.ragul
  ragul.config
  lib/
    segédeszközök.ragul    # local helper module
  vendor/
    külső-modul.ragul      # third-party module, vendored manually
```

```toml
# ragul.config
[modulok]
utvonalak = ["./lib", "./vendor"]
```

A full package manager — with a registry, versioning, and an install command — is a future addition. The vendoring model keeps v1 simple and reproducible without requiring network access or a registry.

---

### 14.7 Tooling Summary

| Component | v1 |
|---|---|
| Error messages | Structured English, error codes E001–E009, W001 |
| Config format | TOML — `ragul.config` in project root |
| CLI commands | `ragul futtat`, `ragul ellenőriz`, `ragul fordít` |
| Module resolution | Directory search via `modulok.utvonalak` |
| Package management | Manual vendoring — `vendor/` directory |
| Package registry | Future |
| Code formatter | Future |
| Language server (LSP) | Future |

---

## 15. Open Questions

No open design questions remain for v1. Future extensions noted throughout the spec:

- **Lazy evaluation** — full implementation after eager MVP is stable
- **Bytecode compiler** — after interpreter is proven
- **Explicit `-párhuzam` scope** — parallel fan-out for effect scopes
- **Message passing / channels** — long-running concurrent processes
- **User-defined generic suffixes** — `T` in user suffix contracts
- **Package registry** — versioned external dependencies
- **Code formatter** — canonical style enforcement
- **Language server (LSP)** — editor integration

---

## 16. Quick Reference

### Sentence structure
```
root-[possession]-[aspect(s)]-case  ...  .
```

### Assignment
```
name-be  value-t.
```

### Class definition
```
pont-unk
    x-ja-be  Szám-ként.     // field
    y-ja-be  Szám-ként.     // field
    távolság-nk        // method
        ...
```

### Instantiation
```
a-be  pont-új-t  3-val  4-val.
```

### Field access and method call
```
a-ja-x-ből  kimenet-be  ír-va.        // field
a-távolság-ből  kimenet-be  ír-va.    // method
```

### Composition
```
kör-alakzat-nk                        // kör as an alakzat
    sugár-ja-be  Szám-ként.
    terület-nk  ...
```

### Contract
```
alakzat-szerződés-unk
    terület-nk  Szám-ként.
    kerület-nk  Szám-ként.

kör-alakzat-nk  alakzat-szerződés-val
    ...
```

### Mutable field (inside -hatás only)
```
játék-nk-hatás
    játékos-be  pont-új-t  0-val  0-val.
    játékos-ja-x-be  5-t.
```

### Standard library imports
```
matematika-ból  négyzetgyök-val  hatvány-val.   // selective
szöveg-ből  hossz-val  feloszt-val.
lista-ból.                                       // whole module
```

### Module import
```
matematika-ból.                                    // whole module
matematika-ból  kétszeres-val  gyök-val.           // selective
matematika-ból  kétszeres-dupla-ként-val.          // aliased
```

### Scope / function definition
```
name-unk
    param-d.
    ...
```

### Scope with type annotations
```
name-unk
    param-d  Típus-ként.
    ...
    eredmény-t  Típus-ként.
```

### Fallible suffix declaration
```
name-unk
    param-d  Szöveg-ként.
    ...
    eredmény-t  vagy-Szöveg-vagy-Hiba-ként.
```

### Calling a scope as a suffix
```
output-be  data-name-t  arg-val.
```

### Conditional scope
```
név-nk-ha
    param-d.
    param-feltétel-ha
        // true branch
    -hanem
        // false branch

eredmény-be  x-név-ha-t.
```

### If / else-if / else chain
```
besoroló-nk-ha
    szám-d.
    szám-100-felett-ha
        "nagy"-t.
    -különben-ha  szám-50-felett-ha
        "közepes"-t.
    -hanem
        "kicsi"-t.
```

### While loop
```
x-be  x-növel-míg-t  x-100-alatt-ha.
```

### Until loop
```
x-be  x-növel-ig-t  x-100-felett-ha.
```

### For each
```
kimenet-be  lista-feldolgozó-mindegyik-t.
```

### Accumulate
```
kimenet-be  lista-összesítő-gyűjt-t  0-val.
```

### Effect scope (I/O)
```
program-nk-hatás
    x-be  "helló"-t.
    x-képernyőre-va.
```

### Custom I/O channel
```
csatorna-nk-hatás
    adat-d.
    // implementation

program-nk-hatás
    x-csatorna-va.
```

### Error propagation
```
eredmény-be  forrás-művelet-va-e.
// execute művelet — propagate error if failure
```

### Error handling boundary
```
program-nk-hatás
    adat-be  forrás-olvasó-va-e.
    adat-képernyőre-va.
    -hibára
        hiba-képernyőre-va.
```

---

## 17. Object-Oriented Programming

### 15.1 Design Principles

Ragul's OOP model emerges from the same mechanisms already present in the language — no new concepts are introduced, only new combinations of existing ones. An object is a named scope that owns data (`-ja` fields), owns behaviour (child scopes as methods), and can be instantiated (`-új`). Functional and object-oriented programming are not in tension in Ragul — they are the same model viewed from different angles.

The four pillars of Ragul OOP:

- **Fields** — roots owned by an instance via `-ja` / `-je`
- **Methods** — child scopes that operate on the instance's fields
- **Instantiation** — `-új` creates an independent live instance
- **Composition** — a scope inherits another's suffixes by naming convention, not hierarchy

### 15.2 Defining a Class

A class is a named scope whose child roots are marked with `-ja` / `-je` (its — belonging to this instance). Child scopes become methods:

```
pont-unk
    x-ja-be  Szám-ként.     // field — belongs to this instance
    y-ja-be  Szám-ként.     // field — belongs to this instance

    távolság-nk                              // method
        x-ja-x-ja-szoroz-y-ja-y-ja-szoroz-össze-négyzetgyök-t.

    eltol-nk                                 // method — returns new instance
        dx-d  Szám-ként.
        dy-d  Szám-ként.
        pont-új-t  x-ja-dx-össze-val  y-ja-dy-össze-val.
```

Fields declared with `-ja` are per-instance — each instantiation gets its own independent copies.

### 15.3 Instantiation — `-új`

`-új` (new) creates a live instance of a scope. Field values are passed via `-val` arguments in declaration order:

```
a-be  pont-új-t  3-val  4-val.
// a is a new pont with x=3, y=4

b-be  pont-új-t  0-val  0-val.
// b is a separate instance — fields independent of a
```

### 15.4 Accessing Fields and Calling Methods

Fields are accessed via `-ja` on the instance root. Methods are called as suffixes — exactly like any other named scope:

```
// Field access
a-ja-x-ből  kimenet-be  ír-va.         // 3
a-ja-y-ből  kimenet-be  ír-va.         // 4

// Method call as suffix
a-távolság-ből  kimenet-be  ír-va.     // 5.0

// Chaining methods
c-be  a-3-val-1-val-eltol-t.           // new pont at x=6, y=5
```

### 15.5 Mutability — Gated by `-hatás`

Ragul instances are **immutable by default**. Methods that "change" a field return a new instance — the original is untouched. This is consistent with Ragul's existing model: assignment replaces, never mutates.

```
// Pure context — immutable
a-be  pont-új-t  3-val  4-val.
b-be  a-3-val-1-val-eltol-t.     // new pont — a unchanged
```

Inside a `-hatás` scope, field mutation is permitted. The same firewall that contains I/O contains mutable state — mutation is not forbidden, it is *contained*:

```
játék-nk-hatás
    játékos-be  pont-új-t  0-val  0-val.

    // mutate field in place — only legal inside -hatás
    játékos-ja-x-be  5-t.
    játékos-ja-y-be  3-t.

    játékos-távolság-ből  kimenet-be  ír-va.
```

The compiler enforces this boundary — field mutation outside a `-hatás` scope is a compile error.

### 15.6 Composition — `B-A-nk`

Classical inheritance hierarchies do not suit Ragul. Instead, **scope composition** works by naming: a scope named `B-A-nk` automatically includes all of A's public suffixes. Reading naturally: *B, as an A, scope* — a circle acting as a shape.

```
// Base scope
alakzat-unk
    terület-unk
        0-t.     // default — override in composed scope

    kerület-unk
        0-t.     // default — override in composed scope

// Composed scope — kör is an alakzat
kör-alakzat-unk
    sugár-ja-be  Szám-ként.

    terület-nk                                          // overrides alakzat's terület
        sugár-ja-sugár-ja-szoroz-3.14159-szoroz-t.

    kerület-nk                                          // overrides alakzat's kerület
        sugár-ja-2-szoroz-3.14159-szoroz-t.
```

`kör` inherits all of `alakzat`'s suffixes and overrides those it redefines. Suffixes not overridden fall through to `alakzat`'s implementation. Multiple composition is expressed by chaining names:

```
mozgó-alakzat-nk     // inherits from both mozgó and alakzat
```

The compiler resolves conflicts (same suffix defined in both) by left-to-right priority — `mozgó`'s version wins over `alakzat`'s. If explicit control is needed, the composed scope defines its own override.

### 15.7 Contracts — `-szerződés`

Structural typing is Ragul's default — if a scope has the required suffixes, it satisfies any contract automatically. No declaration is needed. The compiler checks at the point of use.

For larger codebases where explicit contracts add clarity, **named contracts** can be declared with `-szerződés`:

```
alakzat-szerződés-unk
    terület-nk  Szám-ként.
    kerület-nk  Szám-ként.
```

A contract scope contains only type-annotated method signatures — no implementation. Any scope that implements those methods satisfies the contract; the compiler verifies this at the point of use.

Contracts are **always optional**. The compiler checks structurally regardless of whether a contract is declared. A contract is documentation with enforcement — useful for public APIs and shared libraries, unnecessary for internal helpers.

Attaching a contract to a scope for explicit verification:

```
kör-alakzat-nk  alakzat-szerződés-val
    sugár-ja-be  Szám-ként.
    terület-unk
        sugár-ja-sugár-ja-szoroz-3.14159-szoroz-t.
    kerület-unk
        sugár-ja-2-szoroz-3.14159-szoroz-t.
```

The compiler now verifies that `kör` satisfies `alakzat-szerződés` — missing or mistyped methods are caught at the class definition, not at the point of use.

### 15.8 A Complete Example

```
matematika-ból  négyzetgyök-val.

// Contract — what any alakzat must support
alakzat-szerződés-unk
    terület-nk  Szám-ként.
    kerület-nk  Szám-ként.
    leír-nk     Szöveg-ként.

// Base scope
alakzat-unk
    név-ja-be  Szöveg-ként.

    leír-unk
        név-ja-t  Szöveg-ként.

// kör — composed from alakzat, satisfies alakzat-szerződés
kör-alakzat-nk  alakzat-szerződés-val
    sugár-ja-be  Szám-ként.

    terület-unk
        sugár-ja-sugár-ja-szoroz-3.14159-szoroz-t  Szám-ként.

    kerület-unk
        sugár-ja-2-szoroz-3.14159-szoroz-t  Szám-ként.

// téglalap — composed from alakzat, satisfies alakzat-szerződés
téglalap-alakzat-nk  alakzat-szerződés-val
    szélesség-ja-be  Szám-ként.
    magasság-ja-be   Szám-ként.

    terület-unk
        szélesség-ja-magasság-ja-szoroz-t  Szám-ként.

    kerület-unk
        szélesség-ja-magasság-ja-össze-2-szoroz-t  Szám-ként.

// Program
program-nk-hatás
    k-be   kör-új-t        "kör"-val      5-val.
    t-be   téglalap-új-t   "téglalap"-val  4-val  6-val.

    k-terület-ből   kimenet-be  ír-va.    // 78.53...
    t-kerület-ből   kimenet-be  ír-va.    // 20
    k-leír-ből      kimenet-be  ír-va.    // "kör"
```

### 15.9 Conceptual Mapping

| OOP concept | Ragul equivalent |
|---|---|
| Class | Named scope with `-ja` fields |
| Field | `-ja` / `-je` root inside a scope |
| Method | Child scope |
| Constructor | `-új` with `-val` arguments |
| Instance | Live copy created by `-új` |
| Inheritance | `B-A-nk` composition by name |
| Interface | Optional `-szerződés` scope |
| `this` / `self` | Implicit — `-ja` fields resolve to the current instance |
| Mutable state | Field assignment inside `-hatás` only |
| Immutable method | Any method outside `-hatás` — returns new instance |

### 15.10 Key Observation

Ragul does not choose between functional and object-oriented. A scope is a function. A scope with `-ja` roots and `-új` is a class. A suffix chain is both method call and function composition. Mutation is contained by `-hatás` exactly as I/O is. Contracts are structural by default, explicit when useful. The language is one coherent model — OOP is not bolted on, it emerges.

---

*This document is a living spec. Sections will be added and revised as the language design develops.*
