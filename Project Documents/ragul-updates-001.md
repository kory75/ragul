# Ragul Design Updates — 001
**Date:** 2026-03-14  
**Status:** Adopted  
**Affects:** `ragul-spec.md` §2, §3 — `ragul-toolchain-plan.md` §4 Phase 1

---

## 1. Type Name Aliases

**Decision:** Type names follow the same alias model already used for suffixes. Hungarian canonical names remain primary; English aliases are treated as identical by the parser. Mixed usage within a file is permitted.

| Canonical | English alias | Notes |
|---|---|---|
| `Szám` | `Num` / `Number` | "string" is already used in Hungary, so `Num` keeps it short |
| `Szöveg` | `Str` / `Text` / `String` | `String` is acceptable given Hungarian usage |
| `Lista` | `List` | Nearly identical already |
| `Logikai` | `Bool` | Universal |
| `Hiba` | `Err` / `Error` | |
| `vagy` | `or` | Compound form: `or-Str-or-Error` |

The type alias table lives in `model.py` alongside the suffix alias table — one mechanism, consistent behaviour. A project may use all-English, all-Hungarian, or mixed. No enforcement either way.

**Spec change:** Add to §3.2 (Core Types) — a new "English alias" column in the type table, with a note that aliases are resolved at parse time to the canonical Hungarian form.

---

## 2. Numeric Literals in Suffix Chains

### 2.1 Float literals

Float literals (`3.14`, `0.5`, `-2.718`) are unambiguous in all positions. The lexer consumes digits, then an optional `.` followed by more digits, as a single `NUMBER` token before it looks for `-` suffix separators. The dot is never mistaken for anything else.

```
x-be  3.14-t.
y-be  0.5-t.

szám-3.14-szoroz-t.               // multiply by 3.14 — dot consumed as part of token
lista-szűrve-0.5-felett-val-t.
```

No special handling required. The lexer rule for numbers is: digits, optional (`.` + digits), optional exponent — then stop.

### 2.2 Negative number literals

**Decision:** Negative numbers are written with a leading `-`, exactly as expected. Inside a suffix chain they naturally produce a double dash (`--`), which is unambiguous by rule.

**The rule:** A `-` immediately following a letter or digit is always a **suffix separator**. A `-` immediately following another `-` and preceding a digit is always the start of a **negative number literal**. Because a suffix name can never begin with a digit, `--digit` has exactly one possible reading.

```
// Standalone
x-be  -7-t.
y-be  -3.14-t.

// Inside a list literal
lista-be  [1, -2, 3]-t.

// Inline in a suffix chain — double dash
szám--3-össze-t.                      // add -3 to szám
lista-szűrve--5-felett-val-t.         // filter elements above -5
```

### 2.3 Lexer rule (for toolchain-plan.md §4 Phase 1)

On seeing a `-` character, the lexer peeks ahead:

- Next char is `-` and the char after that is a digit → consume both dashes, then digits (and optional `.` + digits) as a `NUMBER` token with negative value.
- Next char is a letter → suffix separator, continue building the current word token.
- Next char is a digit (after whitespace / sentence start / `[` / `,`) → negative number literal, no double dash needed.

**Spec change:** Add to §2 (Syntax) — a named rule: *"Float literals are written as `3.14` and are consumed by the lexer as a single token before suffix separation occurs. Negative number literals are written as `-7`. Inside a suffix chain, the suffix separator and the literal sign together produce `--7`. The lexer resolves this deterministically: `--` followed by a digit is always separator + negative literal."*
