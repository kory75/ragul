# Ragul — Strategic Direction & Ecosystem Roadmap
**Date:** 2026-03-15
**Status:** Planning document — not yet reflected in milestones

---

## 1. What Kind of Language Is Ragul?

Ragul's core mechanic — **suffix chains are pipelines** — defines its natural domain. Every suffix chain is a transformation: take a value, apply a step, pass the result to the next step. This is not a pattern bolted on; it is the grammar itself.

This makes Ragul a **pipeline scripting language**: a language whose primary purpose is expressing data transformation workflows clearly and safely.

### What a pipeline scripting language is

A pipeline passes data through a chain of transformations where the output of each step becomes the input of the next. In Unix shell:

```bash
cat access.log | grep "ERROR" | cut -d' ' -f1 | sort | uniq -c
```

In Ragul the same idea is expressed without a pipe operator — the chain lives inside the word:

```ragul
napló-ba  "errors.log"-ból  sorok-ba  "ERROR"-tartalmaz-szűrve-t.
```

The suffix chain `-ból ... -szűrve-t` *is* the pipeline. Transformation is encoded in syntax, not in a library pattern.

### The SQL analogy

SQL is the most successful domain-specific language ever built and is a useful comparison:

| Property | SQL | Ragul |
|---|---|---|
| Declarative — describe *what*, not *how* | Yes | Yes |
| Domain-specific (one job done well) | Relational queries | Transformation pipelines |
| Embedded in host languages | Always | Planned (via transpiler) |
| Free "word order" / role-based grammar | Declarative but fixed clause order | Genuinely free word order |
| Type safety on data shape | Schema | Type checker + harmony system |
| Not suitable for full applications alone | Correct | Correct (for now) |

The difference: SQL is *only* embeddable. Ragul can stand alone and could be embedded. Once the transpiler is built, the story becomes concrete: write a `.ragul` transformation, compile to `.py`, import it from Python. Ragul code becomes a typed readable pipeline that lives inside a larger system — exactly as SQL queries live inside a Django app.

---

## 2. Where Ragul Fits Best

### Strong fit

| Domain | Why |
|---|---|
| **Data transformation / ETL** | Suffix chains are pipelines; free word order is declarative; type checker catches shape errors before running |
| **API scripting / HTTP glue** | Fetch → parse → filter → transform → output is a pure pipeline; effect isolation marks I/O clearly |
| **Text processing** | String stdlib already strong; agglutinative model mirrors NLP preprocessing |
| **Log analysis** | Filter, extract, aggregate — all natural suffix operations |
| **Configuration / rule engines** | Declarative style reads like natural-language rules |
| **CLI tooling / automation** | `ragul futtat` workflow already suits small focused tools |
| **Education** | Teaches pipeline thinking and effect isolation as first principles, not library patterns |

### Poor fit (currently)

| Domain | Why not |
|---|---|
| Web applications | No HTTP library, no async, no routing, no template engine |
| GUI applications | No widget library |
| Real-time / concurrent systems | No concurrency primitives yet |
| Systems programming | Interpreted, Python-backed |
| Large-scale OOP | Object model is minimal |

---

## 3. The Web Story

There are two distinct things people mean by "web" and Ragul's fit differs sharply between them.

### HTTP client — strong fit

API scripting is just a pipeline. Fetch → parse → filter → transform → output.

```ragul
válasz-ba        "https://api.example.com/orders"-ból  lekér-va.
rendelések-ba    válasz-json-ból  "orders"-mező-t.
magas-ba         rendelések-ba  100-felett-szűrve-t.
nevek-ba         magas-ba  "customer"-mező-térképezve-t.
nevek-képernyőre-va.
```

Each line is one transformation. The type checker verifies every step. No callbacks, no promise chains, no nested lambdas.

### HTTP server — limited fit

A request handler maps to a Ragul effect scope naturally (input → transform → output). But production web server use requires routing, middleware, sessions, async, and database access — none of which exist yet and some of which conflict with the pure/effect scope model.

### The realistic web position

**Not:** "build your web app in Ragul."
**Yes:** "write your API glue scripts in Ragul instead of throwaway Python."

| Use case | Fit |
|---|---|
| API client scripting | Excellent |
| Data pipelines over HTTP | Excellent |
| Webhook processing | Good |
| Simple stateless endpoint | Possible |
| Full web application | Poor (for now) |

---

## 4. Ragul → Python Transpiler

Currently `ragul futtat` interprets directly. A transpiler would instead output `.py` source:

```
ragul fordít hello.ragul  →  hello.py
```

**Why this matters:**
- Ship Ragul programs anywhere Python runs, with no Ragul dependency
- Call Ragul transformation functions from existing Python projects
- Access Python's entire ecosystem from Ragul by compiling and importing
- Forces precise semantics: if a construct cannot be translated unambiguously, it is not well-defined

The `fordít` command is already stubbed in the CLI. Completing it is the path to embedding.

---

## 5. Jupyter Kernel

Jupyter notebooks communicate with a **kernel** — a background process that receives code cells, runs them, and returns output — over a standard protocol. The kernel is the language-specific part.

Ragul's REPL already has the right shape: persistent environment across sentences, one evaluation per input. A Jupyter kernel wraps this so notebook cells become REPL round-trips.

**Why this matters for Ragul specifically:** the target audience (data transformation, text processing) overlaps almost perfectly with the Jupyter audience. It lets data practitioners explore Ragul interactively without leaving the tool they already use. Implementation work is relatively small — mainly a ZeroMQ wrapper around the existing REPL session model.

---

## 6. Competitive Landscape

### Direct pipeline scripting competitors

| Language | Maturity | Pipeline model | Effect system | Embeddable |
|---|---|---|---|---|
| **Nushell** | Production | Excellent — structured shell | None | No |
| **jq** | Production | Excellent — JSON only | None | Yes |
| **PowerShell** | Production | Good — objects through pipes | None | Limited |
| **R + tidyverse** | Production | Good — `%>%` operator | None | Limited |
| **Elixir** | Production | Good — `\|>` operator | None formal | No |
| **Dhall** | Stable | None | None | Yes |
| **Ragul** | Alpha | Excellent — grammar-native | First-class | Planned |

### Where Ragul is genuinely differentiated

Three things no competitor has simultaneously:

1. **The pipeline is the grammar, not an operator.** In Elixir you write `data |> filter() |> sort()`. In Ragul the pipeline *is* the word: `adat-szűrve-rendezve`. No pipe character — the suffix chain expresses the transformation at the morphological level.

2. **First-class effect/pure separation without a monad.** Haskell has `IO`. Koka has algebraic effects. Ragul has `-hatás` scopes. The same idea expressed as a scope annotation rather than a type wrapper — more approachable, and it falls naturally out of the suffix grammar.

3. **Free word order.** No other programming language has this. The same computation can be written in whatever reading order feels most natural to the author.

### The risk

These differentiators are interesting to language designers but invisible to practitioners who just want to filter a CSV. The path to relevance is making practical pipeline scripting excellent first, so the linguistic novelty becomes a bonus people discover rather than a reason they had to try.

---

## 7. The Path to Relevance

### What "excellent" means for a scripting tool

The bar is not "technically capable." It is: **a developer facing a real task picks Ragul because it is the clearest way to express the solution.**

That bar has four components.

#### Component 1: You can do the common tasks without fighting the language

The most common pipeline scripting tasks are currently blocked:

```
Read a CSV file          → no file I/O module
Parse JSON from an API   → no JSON module
Match lines with regex   → no pattern module
Write results to a file  → no file write
```

Minimum viable modules, in priority order:

| Module | Hungarian name | What it unblocks |
|---|---|---|
| File read/write, line iteration | `fájl` | Every file-based task |
| JSON parse/emit, CSV parse/emit | `adatok` | API scripting, data files |
| Regex match, capture, replace | `minta` | Log processing, text extraction |
| Date parse, format, arithmetic | `dátum` | Any data with timestamps |

Until these four exist, Ragul competes with a 5-line Python script and loses on every practical measure.

#### Component 2: The happy path is shorter than the alternative

**Python** — read a CSV, filter rows, print a field:

```python
import csv
with open("orders.csv") as f:
    for row in csv.DictReader(f):
        if float(row["total"]) > 100:
            print(row["customer"])
```

**Ragul** with `fájl` + `adatok` modules:

```ragul
sorok-ba     "orders.csv"-ból  csv-t.
magas-ba     sorok-ba  "total"-mező-100-felett-szűrve-t.
nevek-ba     magas-ba  "customer"-mező-térképezve-t.
nevek-képernyőre-va.
```

Four lines vs six. Each line states exactly one transformation. No `with` block, no loop, no hidden `float()` cast. The type checker already knows `"total"` is a number after CSV parse — the `felett` suffix just works. This is the argument for Ragul, but it only lands if the modules exist.

#### Component 3: When it breaks, you know exactly why

The type checker already catches errors before running. But error messages need to reach this quality:

```
E001  orders.csv:3  — "total"-mező returns Szöveg, but -felett requires Szám
      Hint: add -számmá to convert first: "total"-mező-számmá-100-felett-szűrve
```

The error names the suffix that failed, the types involved, and suggests the fix. This is better than Python's runtime `TypeError` — it fires before execution, with actionable guidance. This is a genuine competitive advantage if the error messages are written to this standard.

#### Component 4: One compelling demo that travels

Every language that got adopted had a moment where someone saw it and thought "I couldn't do that as cleanly in anything else."

- **jq:** `curl api | jq '.[] | .name'` — one line, structured
- **Nushell:** `ls | sort-by size | reverse | first 5` — the shell *is* the pipeline
- **dplyr:** `flights %>% filter(dep_delay > 0) %>% group_by(carrier) %>% summarise(mean_delay = mean(dep_delay))` — reads like English

Ragul's candidate:

```ragul
// top-customers.ragul — top 5 customers by total order value

rendelések-ba    "orders.json"-ból  json-t.
vásárlók-ba      rendelések-ba  "customer_id"-csoportosítva-t.
összegzett-ba    vásárlók-ba  "total"-összeadva-térképezve-t.
top5-ba          összegzett-ba  rendezve-fordítva-5-első-t.
top5-képernyőre-va.
```

Each line is a named transformation step. Readable top to bottom like a recipe. Type-checked at every step. No lambdas, no method chaining, no intermediate types to track manually. This is the demo — but only works when all referenced suffixes exist and behave as described.

---

## 8. Library & Tooling Roadmap

### Tier 1 — Core pipeline scripting (v0.2.0–v0.3.0)

Solidifies the primary sweet spot.

| Module / Tool | What it adds |
|---|---|
| `fájl` module | File read/write, line iteration, directory listing, path operations |
| `adatok` module | JSON parse/emit, CSV parse/emit, basic tabular field access |
| `minta` module | Regex match, capture groups, replace, split |
| `dátum` module | Date/time parse, format, arithmetic |
| `ragul formáz` / `fmt` | Auto-formatter: canonical suffixes, consistent indentation, blank lines between scopes |
| `ragul teszt` / `test` | Test runner: `.ragul` test files with assertion suffixes |
| Error message quality pass | Every E00x error gets a message, type context, and a hint line |

### Tier 2 — Web / API scripting (v0.4.0)

Unlocks HTTP pipeline use cases.

| Module / Tool | What it adds |
|---|---|
| `háló` module (HTTP client) | GET/POST/headers as suffixes; wraps `httpx` |
| `kódolás` module | JSON encode/decode, base64, URL encoding |
| `napló` module | Structured logging: levels, timestamps, output routing |

### Tier 3 — Developer experience & ecosystem (v0.5.0+)

Needed for community adoption.

| Tool | What it adds |
|---|---|
| `ragul doc` | Inline doc comment extraction |
| `ragul info` | Version, config values, detected entry point |
| `ragul tisztít` / `clean` | Remove build artefacts and caches |
| Package registry | Publish/install community modules |
| Ragul → Python transpiler | Complete `ragul fordít`; enables embedding in Python projects |

### Tier 4 — Stretch / long-term

| Idea | Notes |
|---|---|
| Jupyter kernel | Wrap the REPL session in the `ipykernel` ZeroMQ protocol; low implementation cost, high audience reach |
| HTTP server (`végpont` module) | Minimal stateless route handler; needs async foundations first |
| Implicit parallelism | Implement topological sort in interpreter; pure scopes become automatically parallel |
| VS Code extension (Marketplace) | Already in v0.1.1 plan |
| Concurrency primitives | Required before any real-time or server use case |

---

## 9. Documentation Quality for International Reach

Three issues were identified that affect how accessible the docs are to international (non-Hungarian) users. All three were addressed on 2026-03-15.

### Issue 1 — Opening paragraph led with the exotic angle (fixed)

**Before:** The first sentence of `index.md` named agglutinative grammar and Hungarian before explaining what Ragul actually *does*. For a practising engineer, this reads as "linguistics experiment" before they understand the value.

**After:** The opening now leads with "pipeline scripting language" and "transformation is built into the syntax itself." The Hungarian inspiration is explained in the second paragraph as the *source* of the design, not the headline.

**Rule going forward:** When writing about Ragul — docs, README, announcements — lead with the pipeline/transformation concept. Mention Hungarian as the design inspiration, not as the primary identity.

### Issue 2 — Hungarian was the default tab (fixed)

**Before:** All 17 docs pages with tabbed examples showed `=== "Hungarian"` first. In MkDocs Material, the first tab is the one selected by default — so international readers were landing on Hungarian code every time.

**After:** All 17 pages now show `=== "English aliases"` first.

**Rule going forward:** New tabbed examples should always put English aliases first.

### Issue 3 — Hungarian variable names in English examples (fixed)

**Before:** Several English alias examples still used Hungarian words as variable/scope names (`kétszeres`, `szám`, `üdvözlet`, `adat`, `tartalom`). Suffixes were in English but the roots were not — defeating the purpose of the English tab.

**After:** All English alias tabs now use English root names throughout. Key replacements:

| File | Hungarian root | English replacement |
|---|---|---|
| `index.md` | `kétszeres` (double) | `double` |
| `index.md` | `szám` (number) | `num` |
| `01_hello.md` | prose used `üdvözlet` | prose now uses `greeting` |
| `07_error_handling.md` | `"adat.txt"` | `"data.txt"` |
| `07_error_handling.md` | `-fájlolvasó` | `-readfile` |
| `07_error_handling.md` | `-elemző` | `-parse` |

**Rule going forward:** English alias examples must use English words for *all* roots and variable names, not just for suffixes. Hungarian roots are fine in the Hungarian tab; they should not appear in the English tab.

### Remaining documentation work

- [ ] Audit the 9 reference pages (`syntax.md`, `types.md`, `functions.md`, `control.md`, `effects.md`, `errors.md`, `modules.md`, `stdlib.md`, `tooling.md`) for any remaining Hungarian variable names in English alias tabs
- [ ] Update `igaz` / `hamis` (boolean literals): consider adding `true` / `false` as language-level aliases so the English tab does not need to explain them as keywords without aliases
- [ ] Review `glossary.md` to ensure English-first ordering in the suffix table

---

## 10. Recommended Version Targets

| Version | Theme | Key deliverables |
|---|---|---|
| **v0.2.0** | Unblock | `fájl` + `adatok` modules; real file and JSON tasks now possible |
| **v0.2.x** | Polish | Error message quality pass; every error gets a hint line |
| **v0.3.0** | Extend | `minta` + `dátum`; log processing and timestamped data work |
| **v0.3.x** | Demo + formatter | 5–10 real worked examples published; `ragul formáz` implemented |
| **v0.4.0** | Web | `háló` + `kódolás` + `napló`; API scripting use case complete |
| **v0.5.0** | Ecosystem | Test runner, doc generator, package registry foundations |
| **v1.0.0** | Platform | Transpiler, Jupyter kernel, Marketplace extension, implicit parallelism |

---

*End of document.*
