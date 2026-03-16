# Regex Patterns (`minta` module)

The `minta` module adds five suffix-based wrappers around Python's `re` library.

Import the module once at the top of your file:

=== "English aliases"
    ```ragul
    minta-from.
    ```

=== "Hungarian"
    ```ragul
    minta-ból.
    ```

---

## Suffix reference

| Hungarian | English | Signature | Description |
|---|---|---|---|
| `-minta` | `-match` | `Szöveg → Logikai` | True if the string contains a match |
| `-egyezés` | `-capture` | `Szöveg → vagy-Szöveg-vagy-Hiba` | First match (full match, single group, or list of groups) |
| `-egyezések` | `-findall` | `Szöveg → Lista-Szöveg` | All non-overlapping matches |
| `-mintacsere` | `-resub` | `Szöveg → Szöveg` | Replace every match; backreferences (`\1` …) supported |
| `-mintafeloszt` | `-resplit` | `Szöveg → Lista-Szöveg` | Split on every match |

All patterns follow standard Python `re` syntax.

---

## 1. `-minta` / `-match` — check for a match

Returns `igaz` / `true` if the pattern occurs anywhere in the string.

=== "English aliases"
    ```ragul
    minta-from.

    program-ours-effect
        has_num-into  "price: 1990 Ft"-match-it  "\d+"-with.
        has_num-print-doing.                 // True

        letters_only-into  "no digits here"-match-it  "\d+"-with.
        letters_only-print-doing.            // False
    ```

=== "Hungarian"
    ```ragul
    minta-ból.

    program-nk-hatás
        van_szam-ba  "ár: 1990 Ft"-minta-t  "\d+"-val.
        van_szam-képernyőre-va.              // True

        csak_betu-ba  "nincs szám"-minta-t  "\d+"-val.
        csak_betu-képernyőre-va.             // False
    ```

---

## 2. `-egyezés` / `-capture` — first match

- **No capture groups** — returns the full matched substring.
- **One capture group** — returns that group as a string.
- **Multiple capture groups** — returns a list of group strings.
- **No match** — returns a `Hiba` / `Error` value (handle with `-hibára` / `-catch`).

=== "English aliases"
    ```ragul
    minta-from.

    program-ours-effect
        text-into  "Date: 2026-03-16"-it.

        // no groups → full match
        date-into  text-capture-it  "\d{4}-\d{2}-\d{2}"-with.
        date-print-doing.                    // 2026-03-16

        // one group → that group
        year-into  text-capture-it  "(\d{4})-\d{2}-\d{2}"-with.
        year-print-doing.                    // 2026

        // no match → Error
        result-into  "letters only"-capture-it  "\d+"-with.
        result-print-doing.                  // Hiba(...)
    ```

=== "Hungarian"
    ```ragul
    minta-ból.

    program-nk-hatás
        szöveg-ba  "Dátum: 2026-03-16"-t.

        // csoport nélkül → teljes egyezés
        datum-ba  szöveg-egyezés-t  "\d{4}-\d{2}-\d{2}"-val.
        datum-képernyőre-va.                 // 2026-03-16

        // egy csoport → a csoport tartalma
        ev-ba  szöveg-egyezés-t  "(\d{4})-\d{2}-\d{2}"-val.
        ev-képernyőre-va.                    // 2026

        // nincs egyezés → Hiba
        eredmeny-ba  "csak betűk"-egyezés-t  "\d+"-val.
        eredmeny-képernyőre-va.              // Hiba(...)
    ```

---

## 3. `-egyezések` / `-findall` — all matches

Returns a list of every non-overlapping match. Empty list if nothing matches.

=== "English aliases"
    ```ragul
    minta-from.

    program-ours-effect
        sentence-into  "1 apple, 2 pears, 3 plums"-it.
        numbers-into   sentence-findall-it  "\d+"-with.
        numbers-print-doing.                 // ['1', '2', '3']

        none-into  "no digits"-findall-it  "\d+"-with.
        none-print-doing.                    // []
    ```

=== "Hungarian"
    ```ragul
    minta-ból.

    program-nk-hatás
        mondat-ba  "1 alma, 2 körte, 3 szilva"-t.
        szamok-ba  mondat-egyezések-t  "\d+"-val.
        szamok-képernyőre-va.                // ['1', '2', '3']

        semmi-ba  "nincs szám"-egyezések-t  "\d+"-val.
        semmi-képernyőre-va.                 // []
    ```

---

## 4. `-mintacsere` / `-resub` — regex replace

Replaces every match with the replacement string. Backreferences (`\1`, `\2`, …) refer to capture groups in the pattern.

=== "English aliases"
    ```ragul
    minta-from.

    program-ours-effect
        // collapse whitespace runs to a single space
        source-into  "  lots   of   spaces  "-it.
        clean-into   source-resub-it  "\s+"-with  " "-with.
        clean-print-doing.                   //  lots of spaces

        // reformat a date: YYYY-MM-DD → DD/MM/YYYY
        date-into    "2026-03-16"-it.
        flipped-into date-resub-it  "(\d+)-(\d+)-(\d+)"-with  "\3/\2/\1"-with.
        flipped-print-doing.                 // 16/03/2026
    ```

=== "Hungarian"
    ```ragul
    minta-ból.

    program-nk-hatás
        // szóközök összevonása
        forras-ba     "  sok   szóköz   van  "-t.
        normalizalt-ba  forras-mintacsere-t  "\s+"-val  " "-val.
        normalizalt-képernyőre-va.           //  sok szóköz van

        // dátumformátum: ÉÉÉÉ-HH-NN → NN/HH/ÉÉÉÉ
        datum-ba      "2026-03-16"-t.
        fordított-ba  datum-mintacsere-t  "(\d+)-(\d+)-(\d+)"-val  "\3/\2/\1"-val.
        fordított-képernyőre-va.             // 16/03/2026
    ```

---

## 5. `-mintafeloszt` / `-resplit` — regex split

Splits the string at every occurrence of the pattern. Equivalent to Python's `re.split`.

=== "English aliases"
    ```ragul
    minta-from.

    program-ours-effect
        // split on any whitespace run
        words-into  "one  two   three"-resplit-it  "\s+"-with.
        words-print-doing.                   // ['one', 'two', 'three']

        // split on multiple delimiters at once
        mixed-into  "apple;pear  plum,apricot"-resplit-it  "[;,\s]+"-with.
        mixed-print-doing.                   // ['apple', 'pear', 'plum', 'apricot']
    ```

=== "Hungarian"
    ```ragul
    minta-ból.

    program-nk-hatás
        // szétválasztás szóközökön
        szavak-ba  "egy  kettő   három"-mintafeloszt-t  "\s+"-val.
        szavak-képernyőre-va.                // ['egy', 'kettő', 'három']

        // több elválasztó egyszerre
        vegyes-ba  "alma;körte  szilva,barack"-mintafeloszt-t  "[;,\s]+"-val.
        vegyes-képernyőre-va.                // ['alma', 'körte', 'szilva', 'barack']
    ```
