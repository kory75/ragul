# Standard Library

The standard library is loaded automatically — no import needed. All suffixes below are available in every Ragul program.

---

## Core — Arithmetic

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-össze` | `-add` | `Szám` | `Szám` | `Szám` | Add |
| `-kivon` | `-sub` | `Szám` | `Szám` | `Szám` | Subtract |
| `-szoroz` | `-mul` | `Szám` | `Szám` | `Szám` | Multiply |
| `-oszt` | `-div` | `Szám` | `Szám` | `Szám` | Divide |
| `-maradék` | `-rem` | `Szám` | `Szám` | `Szám` | Modulo (remainder) |

=== "English aliases"
    ```ragul
    x-into  10-it.
    y-into  x-3-add-it.            // 13
    z-into  x-3-mul-2-add-it.      // 32
    ```

=== "Hungarian"
    ```ragul
    x-be  10-t.
    y-be  x-3-össze-t.           // 13
    z-be  x-3-szoroz-2-össze-t.  // 32
    ```

---

## Core — Comparison

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-felett` | `-above` | `Szám` | `Szám` | `Logikai` | Greater than |
| `-alatt` | `-below` | `Szám` | `Szám` | `Logikai` | Less than |
| `-legalább` | `-atleast` | `Szám` | `Szám` | `Logikai` | Greater than or equal |
| `-legfeljebb` | `-atmost` | `Szám` | `Szám` | `Logikai` | Less than or equal |
| `-egyenlő` | `-eq` | any | any | `Logikai` | Equality |
| `-nemegyenlő` | `-neq` | any | any | `Logikai` | Not equal |

---

## Core — Logical

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-nem` | `-not` | `Logikai` | — | `Logikai` | Logical NOT |
| `-és` | `-and` | `Logikai` | `Logikai` | `Logikai` | Logical AND |
| `-vagy` | `-or` | `Logikai` | `Logikai` | `Logikai` | Logical OR |

---

## Core — String

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-összefűz` | `-concat` | `Szöveg` | `Szöveg` | `Szöveg` | Concatenate strings |

---

## matematika — Math

| Hungarian | English | Expects | Produces | Description |
|---|---|---|---|---|
| `-négyzetgyök` | `-sqrt` | `Szám` | `Szám` | Square root |
| `-hatvány` | `-pow` | `Szám` | `Szám` | Power (arg: exponent) |
| `-abszolút` | `-abs` | `Szám` | `Szám` | Absolute value |
| `-kerekítve` | `-round` | `Szám` | `Szám` | Round to nearest integer |
| `-padló` | `-floor` | `Szám` | `Szám` | Floor |
| `-plafon` | `-ceil` | `Szám` | `Szám` | Ceiling |
| `-log` | `-log` | `Szám` | `Szám` | Logarithm (arg: base) |
| `-sin` | `-sin` | `Szám` | `Szám` | Sine (radians) |
| `-cos` | `-cos` | `Szám` | `Szám` | Cosine (radians) |

=== "English aliases"
    ```ragul
    x-into  16-it.
    y-into  x-sqrt-it.           // 4.0
    z-into  x-pow-it  2-with.    // 256
    ```

=== "Hungarian"
    ```ragul
    x-be  16-t.
    y-be  x-négyzetgyök-t.     // 4.0
    z-be  x-hatvány-t  2-val.  // 256
    ```

---

## szöveg — Strings

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-hossz` | `-len` | `Szöveg` | — | `Szám` | Length |
| `-nagybetűs` | `-upper` | `Szöveg` | — | `Szöveg` | Uppercase |
| `-kisbetűs` | `-lower` | `Szöveg` | — | `Szöveg` | Lowercase |
| `-tartalmaz` | `-contains` | `Szöveg` | `Szöveg` | `Logikai` | Contains substring |
| `-kezdődik` | `-startswith` | `Szöveg` | `Szöveg` | `Logikai` | Starts with prefix |
| `-végződik` | `-endswith` | `Szöveg` | `Szöveg` | `Logikai` | Ends with suffix |
| `-feloszt` | `-split` | `Szöveg` | `Szöveg` | `Lista-Szöveg` | Split by separator |
| `-formáz` | `-format` | `Szöveg` | any | `Szöveg` | Format string (`{}` placeholder) |
| `-szelet` | `-slice` | `Szöveg` | `Szám`, `Szám` | `Szöveg` | Slice (start, end) |
| `-csere` | `-replace` | `Szöveg` | `Szöveg`, `Szöveg` | `Szöveg` | Replace all occurrences |
| `-számmá` | `-tonum` | `Szöveg` | — | `vagy-Szám-vagy-Hiba` | Parse string as number |
| `-karakterek` | `-chars` | `Szöveg` | — | `Lista-Szöveg` | Split string into list of single characters |

=== "English aliases"
    ```ragul
    s-into  "helló világ"-it.
    n-into  s-len-it.             // 11
    u-into  s-upper-it.           // "HELLÓ VILÁG"
    r-into  s-replace-it  "világ"-with  "Ragul"-with.  // "helló Ragul"
    ```

=== "Hungarian"
    ```ragul
    s-be  "helló világ"-t.
    n-be  s-hossz-t.            // 11
    u-be  s-nagybetűs-t.        // "HELLÓ VILÁG"
    r-be  s-csere-t  "világ"-val  "Ragul"-val.  // "helló Ragul"
    ```

---

## lista — Lists

| Hungarian | English | Expects | Produces | Description |
|---|---|---|---|---|
| `-rendezve` | `-sorted` | `Lista-T` | `Lista-T` | Sort ascending |
| `-fordítva` | `-reversed` | `Lista-T` | `Lista-T` | Reverse |
| `-első` | `-first` | `Lista-T` | `T` | First element |
| `-utolsó` | `-last` | `Lista-T` | `T` | Last element |
| `-egyedi` | `-unique` | `Lista-T` | `Lista-T` | Remove duplicates |
| `-lapítva` | `-flat` | `Lista-Lista-T` | `Lista-T` | Flatten one level |
| `-szűrve` | `-filter` | `Lista-T` | `Lista-T` | Filter (arg: condition) |
| `-hozzáad` | `-append` | `Lista-T` | `Lista-T` | Append element (arg: element) |
| `-eltávolít` | `-remove` | `Lista-T` | `Lista-T` | Remove element (arg: element) |
| `-hossz` | `-len` | `Lista-T` | `Szám` | Length |
| `-tartalmaz` | `-contains` | `Lista-T` | `Logikai` | Contains element |
| `-beállít` | `-set` | `Lista-T` | `Lista-T` | Replace element at index (non-mutating; args: index, value) |
| `-ismét` | `-repeat` | any | `Lista-any` | Build a list of N copies of a value (arg: N) |
| `-index` | `-index` | `Lista-T` | `T` | Element at index; works on strings too (arg: index) |

=== "English aliases"
    ```ragul
    lista-into  [3, 1, 4, 1, 5, 9, 2, 6]-it.
    sorted-into  lista-sorted-unique-it.          // [1, 2, 3, 4, 5, 6, 9]
    large-into  lista-filter-from  5-above-with  obj. // [9, 6]
    ```

=== "Hungarian"
    ```ragul
    lista-be  [3, 1, 4, 1, 5, 9, 2, 6]-t.
    rendezett-be  lista-rendezve-egyedi-t.      // [1, 2, 3, 4, 5, 6, 9]
    nagy-be  lista-szűrve-ből  5-felett-val  t. // [9, 6]
    ```

---

## minta — Regex Patterns

| Hungarian | English | Expects | Arg(s) | Produces | Description |
|---|---|---|---|---|---|
| `-minta` | `-match` | `Szöveg` | pattern | `Logikai` | True if the string contains a match (`re.search`) |
| `-egyezés` | `-capture` | `Szöveg` | pattern | `vagy-Szöveg-vagy-Hiba` | First match; returns group if one capture group, list if multiple, full match if none |
| `-egyezések` | `-findall` | `Szöveg` | pattern | `Lista-Szöveg` | All non-overlapping matches |
| `-mintacsere` | `-resub` | `Szöveg` | pattern, replacement | `Szöveg` | Replace every match (`re.sub`); backreferences (`\1`, `\2` …) supported |
| `-mintafeloszt` | `-resplit` | `Szöveg` | pattern | `Lista-Szöveg` | Split on every match (`re.split`) |

=== "English aliases"
    ```ragul
    minta-from.

    program-ours-effect
        text-into  "order #1042 placed 2026-03-16"-it.

        // check for a match
        has-into  text-match-it  "\d{4}-\d{2}-\d{2}"-with.
        has-print-doing.                   // True

        // extract first match
        date-into  text-capture-it  "\d{4}-\d{2}-\d{2}"-with.
        date-print-doing.                  // 2026-03-16

        // all numbers
        nums-into  text-findall-it  "\d+"-with.
        nums-print-doing.                  // ['1042', '2026', '03', '16']

        // replace digits with *
        masked-into  text-resub-it  "\d"-with  "*"-with.
        masked-print-doing.                // order #**** placed ****-**-**

        // split on non-word chars
        words-into  text-resplit-it  "\W+"-with.
        words-print-doing.                 // ['order', '1042', 'placed', '2026', '03', '16']
    ```

=== "Hungarian"
    ```ragul
    minta-ból.

    program-nk-hatás
        szöveg-ba  "rendelés #1042 rögzítve: 2026-03-16"-t.

        // egyezés ellenőrzése
        van-ba  szöveg-minta-t  "\d{4}-\d{2}-\d{2}"-val.
        van-képernyőre-va.                 // True

        // első egyezés
        dátum-ba  szöveg-egyezés-t  "\d{4}-\d{2}-\d{2}"-val.
        dátum-képernyőre-va.               // 2026-03-16

        // összes szám
        számok-ba  szöveg-egyezések-t  "\d+"-val.
        számok-képernyőre-va.              // ['1042', '2026', '03', '16']

        // számjegyek cseréje *-gal
        maszkolt-ba  szöveg-mintacsere-t  "\d"-val  "*"-val.
        maszkolt-képernyőre-va.            // rendelés #**** rögzítve: ****-**-**

        // szétválasztás nem-szókaraktereken
        szavak-ba  szöveg-mintafeloszt-t  "\W+"-val.
        szavak-képernyőre-va.              // ['rendelés', '1042', 'rögzítve', '2026', '03', '16']
    ```

---

## képernyő — Terminal I/O

Character-mode terminal output, input, and framebuffer rendering. All suffixes are **pass-through** — they return their input value unchanged so they can appear mid-pipeline.

| Hungarian | English | Expects | Arg(s) | Produces | Description |
|---|---|---|---|---|---|
| `-töröl` | `-clear` | any | — | any | Exit alternate screen (restores normal terminal); or `\033[2J\033[H` clear if not in alt-screen |
| `-nyomtat` | `-write` | any | — | any | Write `str(v)` to stdout — **no newline** |
| `-kurzor` | `-cursor` | any | row, col | any | Move cursor to (row, col) via ANSI escape `\033[row;colH` |
| `-billentyű` | `-key` | any | — | `Szöveg` | Non-blocking keypress; `''` if none pressed; arrow keys decoded (`"LEFT"`, `"RIGHT"`, `"UP"`, `"DOWN"`) |
| `-rajzol` | `-render` | `Lista-Lista-Szöveg` | — | `Lista-Lista-Szöveg` | Render a 2-D character framebuffer (`List[List[str]]`); enters alternate screen buffer on first call |

**Alternate screen buffer:** `-rajzol` enters `\033[?1049h` on first call and registers an `atexit` handler to restore the normal terminal. `-töröl` explicitly exits the alternate screen so game-over text appears in the normal shell history.

=== "English aliases"
    ```ragul
    program-ours-effect
        // clear screen, print a message, wait 1 s, then restore
        0-clear-doing.
        "Hello from Ragul!\n"-write-doing.
        0-sleep-it  1000-with.
        0-clear-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        0-töröl-va.
        "Helló Ragulból!\n"-nyomtat-va.
        0-vár-t  1000-val.
        0-töröl-va.
    ```

---

## idő — Timing

| Hungarian | English | Expects | Arg | Produces | Description |
|---|---|---|---|---|---|
| `-vár` | `-sleep` | any | ms | any | Pause execution for N milliseconds; pass-through (returns input unchanged) |

=== "English aliases"
    ```ragul
    "tick"-write-doing.
    0-sleep-it  500-with.
    " tock\n"-write-doing.
    ```

=== "Hungarian"
    ```ragul
    "tick"-nyomtat-va.
    0-vár-t  500-val.
    " tock\n"-nyomtat-va.
    ```

---

## dátum — Date/Time

PHP-style date formatting. The canonical pipeline start is `0-most-t.` — the `0` is a dummy value discarded by `-most`.

| Hungarian | English | Expects | Arg(s) | Produces | Description |
|---|---|---|---|---|---|
| `-most` | `-now` | any | — | datetime | Current local datetime (input ignored) |
| `-dátumformáz` | `-dateformat` | datetime | `Szöveg` | `Szöveg` | Format using PHP-style format string |
| `-dátumértelmez` | `-parse` | `Szöveg` | `Szöveg` | datetime\|`Hiba` | Parse string → datetime using PHP-style format; returns `Hiba` on failure or unsupported chars |
| `-év` | `-year` | datetime | — | `Szám` | Year (4-digit integer) |
| `-hónap` | `-month` | datetime | — | `Szám` | Month 1–12 |
| `-nap` | `-day` | datetime | — | `Szám` | Day 1–31 |
| `-óra` | `-hour` | datetime | — | `Szám` | Hour 0–23 |
| `-perc` | `-minute` | datetime | — | `Szám` | Minute 0–59 |
| `-másodperc` | `-second` | datetime | — | `Szám` | Second 0–59 |
| `-hétfőnap` | `-weekday` | datetime | — | `Szám` | ISO weekday: Mon=1 … Sun=7 |
| `-időbélyeg` | `-timestamp` | datetime | — | `Szám` | Unix timestamp (float) |
| `-időpontból` | `-fromseconds` | `Szám` | — | datetime | Local datetime from Unix timestamp |
| `-napok` | `-adddays` | datetime | `Szám` | datetime | Add N days (negative = subtract) |
| `-órák` | `-addhours` | datetime | `Szám` | datetime | Add N hours |
| `-különbség` | `-diffseconds` | datetime | datetime | `Szám` | `(arg − self)` in seconds; positive when arg is later |

**PHP format characters** (for `-dátumformáz` and `-dátumértelmez`):

| Char | Meaning | Example |
|---|---|---|
| `Y` | 4-digit year | `2026` |
| `y` | 2-digit year | `26` |
| `m` | Month, zero-padded | `03` |
| `n` | Month, no padding | `3` |
| `d` | Day, zero-padded | `07` |
| `j` | Day, no padding | `7` |
| `H` | Hour 0–23, zero-padded | `09` |
| `G` | Hour 0–23, no padding | `9` |
| `h` | Hour 1–12, zero-padded | `09` |
| `g` | Hour 1–12, no padding | `9` |
| `i` | Minute, zero-padded | `05` |
| `s` | Second, zero-padded | `07` |
| `A` | AM/PM | `AM` |
| `a` | am/pm | `am` |
| `D` | Day abbreviation | `Sat` |
| `l` | Full day name | `Saturday` |
| `M` | Month abbreviation | `Mar` |
| `F` | Full month name | `March` |
| `N` | ISO weekday (Mon=1, Sun=7) | `6` |
| `w` | PHP weekday (Sun=0, Sat=6) | `6` |
| `W` | ISO week number, zero-padded | `12` |
| `z` | Day of year, 0-based | `79` |
| `U` | Unix timestamp | `1742547907` |
| `t` | Days in the month | `31` |
| `L` | Leap year (`1`/`0`) | `0` |
| `\X` | Literal character `X` | `\Y` → `Y` |

**Parsing limitation:** `-dátumértelmez` supports `Y y m d H h i s A a D l M F` only. Characters `n G j w W z U t L` return `Hiba` when used as parse formats.

=== "English aliases"
    ```ragul
    program-ours-effect
        dt-into  0-now-it.
        dt-dateformat-it  "Y-m-d H:i:s"-with-print-doing.
        // → 2026-03-21 09:05:07

        tomorrow-into  dt-adddays-it  1-with.
        tomorrow-dateformat-it  "l, F j, Y"-with-print-doing.
        // → Sunday, March 22, 2026
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        dt-be  0-most-t.
        dt-dátumformáz-t  "Y-m-d H:i:s"-val-képernyőre-va.
        // → 2026-03-21 09:05:07

        holnap-ba  dt-napok-t  1-val.
        holnap-dátumformáz-t  "l, F j, Y"-val-képernyőre-va.
        // → Sunday, March 22, 2026
    ```

---

## Bridge Suffixes

Bridge suffixes convert between types and must be used when chaining across type boundaries:

| Hungarian | English | From | To | Fallible |
|---|---|---|---|---|
| `-szöveggé` | `-tostr` | `Szám` | `Szöveg` | No |
| `-számmá` | `-tonum` | `Szöveg` | `vagy-Szám-vagy-Hiba` | Yes |

=== "English aliases"
    ```ragul
    x-into  42-it.
    s-into  x-tostr-it.           // "42"

    n-into  "123"-tonum-doing-?.   // 123, or propagate error
    ```

=== "Hungarian"
    ```ragul
    x-be  42-t.
    s-be  x-szöveggé-t.         // "42"

    n-be  "123"-számmá-va-e.    // 123, or propagate error
    ```
