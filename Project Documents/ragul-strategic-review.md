# Ragul Strategic Review & Recommendations
**Date:** 2026-03-16 | **Based on:** v0.3.0

---

## 1. Executive Summary

The core toolchain is solid and ahead of schedule — three releases shipped in one day (v0.2.0, v0.2.1, v0.3.0), completing most Tier 1 deliverables.

**Core recommendation:** reposition from "pipeline scripting language" (competing with jq/Nushell) toward a **typed graph analysis language for data scientists**. Bring the Jupyter kernel and a `gráf` module forward from Tier 4 to Tier 2.

---

## 2. Current State

### 2.1 Delivery Status

| Item | Status | Notes |
|---|---|---|
| Lexer, parser, type checker, interpreter | ✅ Done | Full toolchain |
| CLI (futtat/run, ellenőriz/check, repl) | ✅ Done | Bilingual; PyPI published |
| LSP (diagnostics, hover, completion) | ✅ Done (basic) | pygls-based |
| MkDocs docs site | ✅ Done | GitHub Pages |
| ragul new project/module scaffold | ✅ Done | |
| true/false aliases, I/O channels | ✅ Done | netin/netout stubs present |
| adatok module (JSON + CSV) | ✅ Done | |
| Bilingual error messages (E001–E009, W001) | ✅ Done | |
| -val binding resolution | ✅ Done | Was stub; now functional |
| Fold-as-suffix | ✅ Done | Fixed and tested |
| minta module (regex, 5 suffixes) | ✅ Done | 16 tests |
| dátum module | ⚠️ Pending | Listed in v0.3.0; not shipped |
| OOP / -ja syntax in parser (E009) | ⚠️ Pending | Check exists but unreachable |
| ragul formáz formatter | ⚠️ Pending | |
| stdlib module splitting | ⚠️ Pending | All in modules.py |
| English module name aliases (math-from.) | ⚠️ Pending | |
| háló module (HTTP client) | ⏳ Planned v0.4.0 | |
| gráf module | ❌ Not on roadmap | **Recommend: add Tier 2** |
| tároló module (storage) | ❌ Not on roadmap | **Recommend: add Tier 2** |
| Jupyter kernel | ⏳ Planned Tier 4 | **Recommend: promote to Tier 2** |
| Ragul → Python transpiler | ⏳ Planned Tier 3 | |

### 2.2 Known Issues

- **Dependency graph not implemented** — sentences execute in written order, not DAG order; implicit parallelism promised in spec is not enforced. Required before v1.0.0.
- **E009 unreachable** — field mutation check exists in typechecker.py but `word.possession == "-ja"` can never be True until OOP syntax is parsed. Blocked on -ja parser work.

### 2.3 Open Documentation Items

- Audit 9 reference pages (syntax, types, functions, control, effects, errors, modules, stdlib, tooling) for Hungarian variable names in English alias tabs
- Add `true`/`false` as language-level aliases for `igaz`/`hamis`
- Review glossary.md for English-first ordering

---

## 3. The Discovered Niche

### 3.1 Why Current Positioning Is Weak

"Pipeline scripting language" benchmarks against jq, Nushell, PowerShell — all production-stable with large ecosystems. No concrete reason to choose Ragul over them.

### 3.2 Competitive Gap Ragul Can Own

| Tool | Composable pipelines | Graph support | Static type safety | Jupyter |
|---|---|---|---|---|
| jq | Excellent (JSON) | None | None | No |
| Nushell | Excellent | None | Partial | No |
| Python + NetworkX | Verbose | Good | None (runtime) | Yes |
| R + igraph | Good (magrittr) | Basic | Weak | Yes |
| Cypher (Neo4j) | Non-composable | Excellent | Schema-level | No |
| **Ragul (proposed)** | **Grammar-native** | **Planned** | **Static + structural** | **Planned** |

The gap: no tool is simultaneously composable at the grammar level, statically typed for graph structural properties, and Jupyter-native. Ragul can own all three.

### 3.3 Why Graph Analysis Specifically Fits Ragul

**Traversal is a suffix chain.** Graph traversal is a recursive transformation — take a collection, follow edges, return a collection. This is what the suffix model expresses natively:

```ragul
neighbours-into    node-it  1-depth-traverse-it.
two-hops-into      node-it  2-depth-traverse-it.
centrality-into    graph-it  "weight"-betweenness-it.
top10-into         centrality-it  sorted-reversed-10-first-it.
```

**Type checker catches structural mismatches.** In NetworkX, applying weighted centrality to an unweighted graph is a silent wrong-result error. Ragul catches it statically using the existing dual-guard mechanism, extended to graph type properties:

```
graph-into    edge-list-from  undirected-graph-it.  // Graph-Undirected-Unweighted
centrality-into    graph-it  "weight"-betweenness-it.
// E001: -betweenness-weighted expects Graph-Weighted, got Graph-Unweighted
// Hint: use -betweenness-equal for unweighted graphs
```

**Jupyter cells map to Ragul sentences.** Each cell is one transformation step. Ragul's dependency model would invalidate downstream cells when an upstream cell reruns — a structural improvement over Python notebook state management.

### 3.4 NoSQL Database Fit Summary

| Type | Fit | Key insight | Tier |
|---|---|---|---|
| Key-value (Redis) | Excellent | Two-suffix read/write maps to directional I/O channels | Tier 2 (tároló) |
| Document (MongoDB) | Good | Schema projection at boundary resolves type mismatch | Tier 3 |
| Graph (Neo4j) | Excellent | Traversal is a suffix chain; type system verifies structural properties | Tier 2 (gráf) |
| Relational (SQL) | Good | SELECT = filter+project+sort; JOINs and transactions need new design | Tier 3 |
| Eventual consistency | Poor | Requires new language-level primitives (consistency annotations on channels) | Post-v1 |

**Design principle to enforce:** from the caller's perspective, the pipeline shape should look identical regardless of whether the source is a file, key-value store, document store, or graph database. The channel differs; the suffix chain shape does not.

---

## 4. Roadmap Recommendations

### 4.1 Complete v0.3.x Before v0.4.0

| Item | Effort |
|---|---|
| dátum module | Low — wraps Python datetime |
| -ja field syntax in parser (unblocks E009 + OOP) | Medium |
| ragul formáz formatter | Medium |
| stdlib module splitting | Low |
| English module name aliases (math-from., pattern-from.) | Low |
| 3 open doc audit items | Low |

### 4.2 Revised Tier Structure

**Tier 1 (v0.3.x) — no structural change, complete open items above**

**Tier 2 (v0.4.0) — EXPAND to include graph/data-science deliverables**

| Module / Tool | What it adds | Change |
|---|---|---|
| háló (HTTP client) | GET/POST/headers as suffixes | Existing |
| **gráf module** | Load from edge list, traverse, filter by degree, basic centrality | **NEW — promoted from not-on-roadmap** |
| **tároló module** | Key-value + document store interface (same pipeline shape as file I/O) | **NEW** |
| **Jupyter kernel** | ipykernel ZeroMQ wrapper around existing REPL | **Promoted from Tier 4** |

**Tier 3 (v0.5.0) — developer experience + graph type system**

| Item | Notes |
|---|---|
| Graph type properties in type checker | Directed/undirected, weighted/unweighted propagation; E001-class errors for structural mismatches |
| ragul doc generator | Inline doc comment extraction |
| ragul test runner | Built-in test runner |
| Package registry foundations | |
| Ragul → Python transpiler | Complete ragul fordít |

**Tier 4 / Post-v1 — unchanged**
- Eventual consistency database primitives
- HTTP server (végpont) — needs async foundations
- Implicit parallelism (topological sort)
- VS Code Marketplace
- SQL/relational module (JOIN semantics require new design)

### 4.3 Revised Version Targets

| Version | Theme | Key deliverables |
|---|---|---|
| v0.3.2 | Complete (PyPI release) | dátum; képernyő; idő; game; 171 tests |
| v0.3.5 | Polish & OOP foundations | -ja field syntax (E009); formáz; module splitting; English module aliases; docs audit |
| v0.4.0 | Data science unlock | háló; gráf module; tároló module; Jupyter kernel |
| v0.4.x | Graph type system | Typed graph structural properties in type checker; E001-class graph errors |
| v0.5.0 | Ecosystem | ragul test; ragul doc; package registry; transpiler |
| v1.0.0 | Platform | VS Code Marketplace; implicit parallelism; SQL module if demand exists |

---

## 5. The One Compelling Demo

**Replace** the top-5-customers CSV demo as the headline demo.

**New target:** citation network analysis in a Jupyter notebook — load a graph from an edge list, compute community structure, find top-10 most central papers by weighted betweenness, print a summary. Each step one Ragul sentence, each cell one transformation, the type checker catching a structural mistake live.

Why this demo travels:
- Lives in Jupyter — the native environment of the target audience
- The type error catching is the headline differentiator — no competitor does this
- Each cell reads as a natural-language description — collaborators understand without implementation knowledge
- Citation network analysis appears in academic papers and research blogs — the demo reaches that audience organically

The CSV/customer demo stays as the introductory documentation example. The citation network demo is the external-facing headline.

---

## 6. Recommended Positioning Statement

> Ragul is a typed graph analysis language. Write graph transformations as readable suffix chains — each step named, each operation type-checked. Structural mistakes are caught before execution, not at runtime. Runs in Jupyter notebooks natively.

In all external communication: lead with graph analysis and Jupyter. The suffix-chain/pipeline explanation follows as "how it works" not "what it is."

---

## 7. Immediate Actions

**Before starting v0.4.0:**
- Ship dátum module
- Add -ja field syntax to parser (unblocks E009)
- Add English module name aliases
- Clear 3 open doc audit items

**When starting v0.4.0:**
- Design the gráf module API from the demo notebook outward — write the notebook first, let the API emerge from what needs to read cleanly
- Ship Jupyter kernel first, not last — it is the environment for iterating the graph module
- Design tároló so file, key-value, and document sources produce identical pipeline shapes

**In parallel:**
- Update README and docs index to lead with graph/data-science story
- Publish citation network demo notebook as a "coming soon" artefact — before the gráf module ships

---

## Appendix: Proposed gráf Module Suffix Surface

| Hungarian | English alias | Expects | Produces | Description |
|---|---|---|---|---|
| `-gráf` | `-graph` | Lista (edge list) | Gráf | Load graph from edge list |
| `-irányított` | `-directed` | Gráf | Gráf-Irányított | Mark as directed |
| `-irányítatlan` | `-undirected` | Gráf | Gráf-Irányítatlan | Mark as undirected |
| `-súlyozott` | `-weighted` | Gráf | Gráf-Súlyozott | Mark as weighted (arg: field name) |
| `-fokszám` | `-degree` | Csúcs | Szám | Degree of a node |
| `-fokszám-szűrve` | `-degree-filter` | Gráf | Gráf | Filter nodes by minimum degree |
| `-szomszédok` | `-neighbours` | Csúcs | Lista-Csúcs | Immediate neighbours |
| `-bejárás` | `-traverse` | Csúcs | Lista-Csúcs | BFS/DFS (arg: depth) |
| `-közbülső` | `-betweenness` | Gráf-Súlyozott | Lista-Szám | Weighted betweenness centrality |
| `-közbülső-egyenlő` | `-betweenness-equal` | Gráf-Irányítatlan | Lista-Szám | Unweighted betweenness centrality |
| `-pagerank` | `-pagerank` | Gráf-Súlyozott | Lista-Szám | PageRank (arg: damping factor) |
| `-közösségek` | `-communities` | Gráf | Lista-Lista-Csúcs | Community detection (Louvain) |
| `-klaszter` | `-clustering` | Gráf | Szám | Global clustering coefficient |
| `-részgráf` | `-subgraph` | Gráf + Lista-Csúcs | Gráf | Induced subgraph from node list |

Type names `Gráf`, `Csúcs` (node) and parameterised variants (`Gráf-Irányított`, `Gráf-Súlyozott`) follow the existing `Lista-T` generic notation. The compiler propagates structural properties through suffix chains using the existing dual-guard mechanism.
