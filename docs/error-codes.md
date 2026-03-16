# Error Code Examples

Each file in [`examples/error-codes/`](https://github.com/kory75/ragul/tree/master/examples/error-codes) contains a minimal program that triggers one specific compiler diagnostic. Run any of them with `ragul check` to see the exact error output.

---

## E001 — Root Guard Failure

Fires when a suffix is applied to a root whose type does not satisfy the suffix's type contract.

```bash
ragul check examples/error-codes/E001_root_guard.ragul
```

```ragul
program-ours-effect
    // ERROR — "hello" is a String; -above requires a Number
    result-into  "hello"-5-above-it.
    result-print-doing.
```

**Output:**

```
ERROR  E001  Suffix -felett (-above) expects Number (Szám), but root is String (Szöveg).
WARN   W001  Suffix chain crosses type boundary from String (Szöveg) to Number (Szám) without a bridge suffix.
```

**Fix:** Use a Number root directly (`42-5-above-it.`) or convert first with `-tonum` (`"42"-tonum-5-above-it.`).

---

## E003 — Parallel Write Conflict

Fires when two independent sentences in a pure (non-effect) scope both write to the same root.

```bash
ragul check examples/error-codes/E003_parallel_write.ragul
```

```ragul
// ERROR — x is written twice in the same pure scope
x-into  3-it.
x-into  5-it.
```

**Output:**

```
ERROR  E003  Root 'x' is written by two independent sentences — parallel write conflict.
```

**Fix:** Give each write a distinct name, or use an effect scope (`-ours-effect`) for sequential reassignment.

---

## E004 — Effectful Call from Pure Scope

Fires when an I/O or side-effect suffix is used outside a `-ours-effect` (`-nk-hatás`) scope.

```bash
ragul check examples/error-codes/E004_effect_pure_scope.ragul
```

```ragul
// ERROR — -print is an effect suffix; the top-level scope is pure
x-into  42-it.
x-print-doing.
```

**Output:**

```
ERROR  E004  Effectful suffix -képernyőre (-print) called from the top-level scope.
```

**Fix:** Wrap the program in an effect scope:

```ragul
program-ours-effect
    x-into  42-it.
    x-print-doing.
```

---

## E005 — Unhandled Fallible (`vagy`) Type

Fires when a `vagy` (fallible) result is used without first handling the error case.

```bash
ragul check examples/error-codes/E005_unhandled_fallible.ragul
```

```ragul
program-ours-effect
    // -tonum returns Number|Error — using the result without handling the error fires E005
    n-into  "abc"-tonum-doing.
    n-print-doing.
```

**Output:**

```
ERROR  E005  Root '"abc"' is Number|Error — both cases must be handled.
ERROR  E005  Root 'n' is Number|Error — both cases must be handled.
```

**Fix — propagate with `-doing-?`:**

```ragul
program-ours-effect
    n-into  "abc"-tonum-doing-?.
    n-print-doing.
```

**Fix — catch the error:**

```ragul
program-ours-effect
    n-into  "abc"-tonum-doing-?.
    n-print-doing.
    -catch
        "Could not parse as number"-print-doing.
```

---

## E006 — Scope Leak

Fires when a root defined inside a child scope is referenced in an outer scope where it does not exist.

```bash
ragul check examples/error-codes/E006_scope_leak.ragul
```

```ragul
calculator-ours-effect
    result-into  6-7-mul-it.   // 'result' lives inside 'calculator'
    result-print-doing.

program-ours-effect
    // ERROR — 'result' is defined inside 'calculator', not here
    summary-into  result-it.
    summary-print-doing.
```

**Output:**

```
ERROR  E006  Root 'result' is referenced outside its defining scope (scope 'calculator').
```

**Fix:** Either reference `result` from inside `calculator`, or define a scope that returns the value and bind the result in the outer scope.

---

## E007 — Module Not Found

Fires when a `-from` (`-ból`) import cannot be resolved to a `.ragul` file on the module search path.

```bash
ragul check examples/error-codes/E007_module_not_found.ragul
```

```ragul
program-ours-effect
    // ERROR — no geometry.ragul exists on the search path
    geometry-from.
    area-into  10-5-area-calc-it.
    area-print-doing.
```

**Output:**

```
ERROR  E007  Module 'geometry' cannot be resolved.
             Searched: 'examples/error-codes/geometry.ragul'
```

**Fix:** Create `geometry.ragul` in the same directory as your script, or add its directory to `modulok.utvonalak` in `ragul.config`.

---

## E009 — Field Mutation Outside Effect Scope

> **Planned for v0.3.0.** The diagnostic is implemented; OOP / record-update syntax is not yet in the parser. Until then, the equivalent enforcement is E003 (parallel write conflict in a pure scope).

Fires when a field on a data record is mutated from inside a pure scope.

**Intended pattern (v0.3.0):**

```ragul
// ERROR — field mutation outside an effect scope
person-name-into  "Bob"-it.
```

**Output (v0.3.0):**

```
ERROR  E009  Field 'name' is mutated outside a -hatás scope (in the top-level scope).
```

**Fix:** Move the mutation inside a `-ours-effect` scope, or return a new record with the updated field.

---

## W001 — Type Harmony Warning

Fires when a suffix changes the element type (e.g. String → List) without an explicit bridge suffix. This is a **warning**, not an error — the program still runs.

```bash
ragul check examples/error-codes/W001_harmony.ragul
```

```ragul
program-ours-effect
    sentence-into  "hello world"-it.
    // W001 — -split converts String → List without an explicit bridge
    words-into  sentence-split-" "-it.
    words-print-doing.
```

**Output:**

```
WARN  W001  Suffix chain crosses type boundary from String (Szöveg) to List[String (Szöveg)] without a bridge suffix.
```

**Suppressing W001:** Set `harmonia = "off"` in `ragul.config` to disable harmony checks, or `"strict"` to promote them to errors.

---

## Running All Examples

```bash
for f in examples/error-codes/*.ragul; do
    echo "=== $f ==="
    ragul check "$f"
done
```

See the [full error code reference](tooling.md#compiler-error--warning-codes) in the Tooling guide.
