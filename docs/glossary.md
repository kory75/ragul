# Glossary

Every Hungarian suffix and keyword, with its English alias and a brief pronunciation guide.

Aliases are resolved at lex time — the compiler treats all forms identically. Mix freely.

---

## Case Suffixes (Outermost Layer)

These encode the *grammatical role* of a word in the sentence.

| Hungarian | English | Symbol | Meaning |
|---|---|---|---|
| `-ba` / `-be` | `-into` | `->` | Target — the thing being written *into* |
| `-ból` / `-ből` | `-from` | `-<` | Source — reading *from* this root |
| `-val` / `-vel` | `-with` | `-&` | Instrument — argument passed *with* an operation |
| `-nál` / `-nél` | `-at` | `-@` | Context — situational scope |
| `-ként` | `-as` | `-:` | Role — acting *as* a type or alias |
| `-t` | `-obj` | `-*` | Object — the direct object (accusative) |
| `-ra` / `-re` | — | — | Onto — write direction (embedded in channel names) |
| `-ról` | — | — | From-surface — read direction |

---

## Action & Error Suffixes

| Hungarian | English | Symbol | Meaning |
|---|---|---|---|
| `-va` / `-ve` | `-doing` | `-!` | Action — execute the operation |
| `-e` | `-else-fail` | `-?` | Error propagation — propagate failure upward |

---

## Possession Suffixes (Innermost Layer)

These encode ownership / lifetime of the root.

| Hungarian | English | Meaning |
|---|---|---|
| `-unk` / `-nk` | `-ours` | This scope owns it |
| `-m` / `-em` | `-mine` | Immutable / bound |
| `-d` / `-ed` | `-yours` | Parameter (caller provides) |
| `-ja` / `-je` | `-its` | Instance field |

---

## Scope Modifiers

Used as part of a scope's name to declare its kind.

| Hungarian | English | Meaning |
|---|---|---|
| `-hatás` | `-effect` | Effect scope — executes eagerly, top to bottom |
| `-ha` | `-if` | Conditional scope |
| `-hanem` | `-else` | Else branch (sibling of `-ha`) |
| `-különben` | `-elif` | Else-if branch |
| `-hibára` | `-catch` | Error handler (sibling of a scope) |
| `-modul` | `-module` | Module scope |
| `-szerződés` | — | Contract definition |
| `-új` | — | Instantiation |

---

## Loop Suffixes

| Hungarian | English | Meaning |
|---|---|---|
| `-míg` | `-while` | While loop — runs while condition is true |
| `-ig` | `-until` | Until loop — runs until condition is true |
| `-mindegyik` | `-each` / `-every` | For-each loop |
| `-gyűjt` | `-fold` / `-reduce` | Fold/reduce loop |
| `-megszakít` | `-break` | Break out of current loop |

---

## Effect Channels

| Hungarian | English | Meaning |
|---|---|---|
| `-képernyőre` | `-print` | Write to stdout |

---

## Arithmetic Suffixes

All take one numeric argument inline in the chain.

| Hungarian | English | Operation |
|---|---|---|
| `-össze` | `-add` | Addition — `x-y-add` = x + y |
| `-kivon` | `-sub` | Subtraction — `x-y-sub` = x − y |
| `-szoroz` | `-mul` | Multiplication — `x-y-mul` = x × y |
| `-oszt` | `-div` | Division — `x-y-div` = x ÷ y |
| `-maradék` | `-rem` | Remainder — `x-y-rem` = x mod y |

---

## Comparison Suffixes

Take one numeric argument; produce `Logikai` (boolean).

| Hungarian | English | Operation |
|---|---|---|
| `-felett` | `-above` | Greater than — x > y |
| `-alatt` | `-below` | Less than — x < y |
| `-legalább` | `-atleast` | Greater than or equal — x ≥ y |
| `-legfeljebb` | `-atmost` | Less than or equal — x ≤ y |
| `-egyenlő` | `-eq` | Equal — x == y |
| `-nemegyenlő` | `-neq` | Not equal — x ≠ y |

---

## Logical Suffixes

Operate on `Logikai` (boolean) values.

| Hungarian | English | Operation |
|---|---|---|
| `-nem` | `-not` | Logical NOT |
| `-és` | `-and` | Logical AND |
| `-vagy` | `-or` | Logical OR |

---

## String Suffixes

### Core (always available)

| Hungarian | English | Args | Produces | Description |
|---|---|---|---|---|
| `-összefűz` | `-concat` | second string | `Szöveg` | Concatenate |

### `szöveg` Module

| Hungarian | English | Args | Produces | Description |
|---|---|---|---|---|
| `-hossz` | `-len` | — | `Szám` | Length |
| `-nagybetűs` | `-upper` | — | `Szöveg` | Uppercase |
| `-kisbetűs` | `-lower` | — | `Szöveg` | Lowercase |
| `-tartalmaz` | `-contains` | needle | `Logikai` | Contains substring |
| `-kezdődik` | `-startswith` | prefix | `Logikai` | Starts with |
| `-végződik` | `-endswith` | suffix | `Logikai` | Ends with |
| `-feloszt` | `-split` | separator | `Lista-Szöveg` | Split into list |
| `-formáz` | `-format` | value | `Szöveg` | Format string (`{}` placeholder) |
| `-szelet` | `-slice` | start, end | `Szöveg` | Substring slice |
| `-csere` | `-replace` | old, new | `Szöveg` | Replace all occurrences |
| `-számmá` | `-tonum` | — | `vagy-Szám-vagy-Hiba` | Parse as number |

---

## Math Suffixes (`matematika` Module)

| Hungarian | English | Args | Produces | Description |
|---|---|---|---|---|
| `-négyzetgyök` | `-sqrt` | — | `Szám` | Square root |
| `-hatvány` | `-pow` | exponent | `Szám` | Power |
| `-abszolút` | `-abs` | — | `Szám` | Absolute value |
| `-kerekítve` | `-round` | — | `Szám` | Round to nearest integer |
| `-padló` | `-floor` | — | `Szám` | Floor |
| `-plafon` | `-ceil` | — | `Szám` | Ceiling |
| `-log` | `-log` | base | `Szám` | Logarithm |
| `-sin` | `-sin` | — | `Szám` | Sine |
| `-cos` | `-cos` | — | `Szám` | Cosine |
| `-szöteggé` | `-tostr` | — | `Szöveg` | Convert number to string |

---

## List Suffixes (`lista` Module)

| Hungarian | English | Args | Produces | Description |
|---|---|---|---|---|
| `-hossz` | `-len` | — | `Szám` | Length |
| `-rendezve` | `-sorted` | — | `Lista-T` | Sort ascending |
| `-fordítva` | `-reversed` | — | `Lista-T` | Reverse |
| `-egyedi` | `-unique` | — | `Lista-T` | Remove duplicates |
| `-első` | `-first` | — | `T` | First element |
| `-utolsó` | `-last` | — | `T` | Last element |
| `-lapítva` | `-flat` | — | `Lista-T` | Flatten one level |
| `-szűrve` | `-filter` | condition | `Lista-T` | Filter by condition |
| `-hozzáad` | `-append` | element | `Lista-T` | Append element |
| `-eltávolít` | `-remove` | element | `Lista-T` | Remove first occurrence |
| `-tartalmaz` | `-contains` | element | `Logikai` | Contains element |
| `-szelet` | `-slice` | start, end | `Lista-T` | Slice |

---

## Type Keywords

These appear in type annotations and `vagy` expressions. They are not suffixes — they cannot be aliased.

| Hungarian | Meaning |
|---|---|
| `Szám` | Number (integer or float) |
| `Szöveg` | String |
| `Logikai` | Boolean |
| `Lista` | List (parameterised: `Lista-Szám`) |
| `Hiba` | Error value |
| `vagy` | Union type (`vagy-Szám-vagy-Hiba`) |

---

## Boolean Literals

| Hungarian | Meaning |
|---|---|
| `igaz` | True |
| `hamis` | False |

---

## Pronunciation Guide

| Letter / Cluster | Approximate sound |
|---|---|
| `á` | long "ah" (as in "father") |
| `é` | long "ay" (as in "they") |
| `í` | long "ee" |
| `ó` | long "oh" |
| `ö` | "ur" (rounded, like German ö) |
| `ő` | long "ur" (rounded) |
| `ú` | long "oo" |
| `ü` | "ew" (rounded, like French u) |
| `ű` | long "ew" (rounded) |
| `cs` | "ch" (as in "church") |
| `sz` | "s" (as in "sun") |
| `zs` | "zh" (as in "measure") |
| `gy` | "dy" (soft, like "dew" in British English) |
| `ny` | "ny" (as in "canyon") |
| `ly` | "y" (as in "yes") |

**Quick reference:** `-össze` ≈ "uh-seh", `-kivon` ≈ "kih-von", `-szoroz` ≈ "soh-roz", `-felett` ≈ "feh-lett", `-képernyőre` ≈ "kay-pehr-nyur-reh"
