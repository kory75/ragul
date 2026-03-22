# Date & Time — `dátum` module

The `dátum` module adds PHP-style date/time formatting and arithmetic. All suffixes are always available — no import statement required.

Full runnable source:

- English: [`examples/en/18_date.ragul`](https://github.com/kory75/ragul/blob/master/examples/en/18_date.ragul)
- Hungarian: [`examples/hu/17_dátum.ragul`](https://github.com/kory75/ragul/blob/master/examples/hu/17_dátum.ragul)

---

## Quick suffix reference

| Hungarian | English | Input | Arg | Output | Description |
|---|---|---|---|---|---|
| `-most` | `-now` | any | — | datetime | Current local datetime (input discarded) |
| `-dátumformáz` | `-dateformat` | datetime | `Szöveg` | `Szöveg` | PHP-style format string |
| `-dátumértelmez` | `-parse` | `Szöveg` | `Szöveg` | datetime\|`Hiba` | Parse text with PHP format |
| `-év` | `-year` | datetime | — | `Szám` | Year (4-digit) |
| `-hónap` | `-month` | datetime | — | `Szám` | Month 1–12 |
| `-nap` | `-day` | datetime | — | `Szám` | Day 1–31 |
| `-óra` | `-hour` | datetime | — | `Szám` | Hour 0–23 |
| `-perc` | `-minute` | datetime | — | `Szám` | Minute 0–59 |
| `-másodperc` | `-second` | datetime | — | `Szám` | Second 0–59 |
| `-hétfőnap` | `-weekday` | datetime | — | `Szám` | ISO weekday Mon=1…Sun=7 |
| `-időbélyeg` | `-timestamp` | datetime | — | `Szám` | Unix timestamp (float) |
| `-időpontból` | `-fromseconds` | `Szám` | — | datetime | Datetime from Unix timestamp |
| `-napok` | `-adddays` | datetime | `Szám` | datetime | Add N days (positive or negative) |
| `-órák` | `-addhours` | datetime | `Szám` | datetime | Add N hours |
| `-különbség` | `-diffseconds` | datetime | datetime | `Szám` | `(arg − self)` in seconds |

!!! note "Argument syntax"
    String arguments (format strings, parse patterns) are passed as a separate **`-with` / `-val` word** in the sentence — not inline in the suffix chain:

    ```ragul
    // correct:  suffix-it  "format"-with.
    iso-into  now-dateformat-it  "Y-m-d"-with.

    // not:  now-"Y-m-d"-dateformat-it.   ← ambiguous when root is a variable
    ```

---

## 1. Getting and formatting the current datetime

`-now` / `-most` ignores its input and returns the current local datetime. Chain `-dateformat` / `-dátumformáz` with a PHP format string to produce text.

=== "English"
    ```ragul
    program-ours-effect
        now-into  0-now-it.

        // ISO timestamp: "2026-03-21 09:05:07"
        iso-into  now-dateformat-it  "Y-m-d H:i:s"-with.
        iso-print-doing.

        // Human-readable: "Saturday, March 21, 2026"
        long-into  now-dateformat-it  "l, F j, Y"-with.
        long-print-doing.

        // 12-hour clock: "9:05 AM"
        clock-into  now-dateformat-it  "g:i A"-with.
        clock-print-doing.

        // ISO week number only: "12"
        wk-into  now-dateformat-it  "W"-with.
        "Week: "-write-doing.  wk-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        most-ba  0-most-t.

        // ISO időbélyeg: "2026-03-21 09:05:07"
        iso-ba  most-dátumformáz-t  "Y-m-d H:i:s"-val.
        iso-képernyőre-va.

        // Emberi olvasható: "Saturday, March 21, 2026"
        hosszú-ba  most-dátumformáz-t  "l, F j, Y"-val.
        hosszú-képernyőre-va.

        // 12 órás: "9:05 AM"
        órajelzés-be  most-dátumformáz-t  "g:i A"-val.
        órajelzés-képernyőre-va.

        // ISO hétszám: "12"
        hétszám-ba  most-dátumformáz-t  "W"-val.
        "Hét: "-nyomtat-va.  hétszám-képernyőre-va.
    ```

### PHP format character reference

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
| `A` | AM / PM | `AM` |
| `a` | am / pm | `am` |
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
| `L` | Leap year: `1` if yes, `0` if no | `0` |
| `\X` | Literal character `X` (backslash escape) | `\Y` → `Y` |

!!! warning "Avoid format chars inside literal text"
    Every unescaped letter in the format string is checked against the table above.
    The word `"Week W"` produces `"12eek 12"` because both `W`s expand to the week number.
    Use a backslash to suppress expansion: `"\Week W"` → `"Week 12"`.

---

## 2. Extracting individual fields

Each extraction suffix takes a datetime and returns a `Szám` / number. Non-datetime input returns a `Hiba`.

=== "English"
    ```ragul
    program-ours-effect
        now-into  0-now-it.
        yr-into   now-year-it.      // 2026
        mo-into   now-month-it.     // 3
        dy-into   now-day-it.       // 21
        hr-into   now-hour-it.      // 9
        mn-into   now-minute-it.    // 5
        sc-into   now-second-it.    // 7
        wd-into   now-weekday-it.   // 6  (Saturday — Mon=1…Sun=7)

        "Year: "-write-doing.  yr-print-doing.
        "Day:  "-write-doing.  dy-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        most-ba      0-most-t.
        év-be        most-év-t.         // 2026
        hónap-ba     most-hónap-t.      // 3
        nap-ba       most-nap-t.        // 21
        óra-ba       most-óra-t.        // 9
        perc-be      most-perc-t.       // 5
        mperc-be     most-másodperc-t.  // 7
        hétfőnap-ba  most-hétfőnap-t.   // 6  (szombat — H=1…V=7)

        "Év:  "-nyomtat-va.  év-képernyőre-va.
        "Nap: "-nyomtat-va.  nap-képernyőre-va.
    ```

---

## 3. Date arithmetic

`-adddays` / `-napok` and `-addhours` / `-órák` add an integer offset to a datetime and return a new datetime. The original value is unchanged.

=== "English"
    ```ragul
    program-ours-effect
        now-into      0-now-it.
        tomorrow-into  now-1-adddays-it.
        nextweek-into  now-7-adddays-it.
        in3hrs-into    now-3-addhours-it.

        tm-into  tomorrow-dateformat-it  "Y-m-d"-with.
        nw-into  nextweek-dateformat-it  "Y-m-d"-with.
        hr-into  in3hrs-dateformat-it    "H:i"-with.

        "Tomorrow:  "-write-doing.  tm-print-doing.    // 2026-03-22
        "Next week: "-write-doing.  nw-print-doing.    // 2026-03-28
        "In 3 hrs:  "-write-doing.  hr-print-doing.    // 12:05
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        most-ba       0-most-t.
        holnap-ba     most-1-napok-t.
        jövőhéten-ba  most-7-napok-t.
        három-ba      most-3-órák-t.

        hf-ba  holnap-dátumformáz-t    "Y-m-d"-val.
        jh-ba  jövőhéten-dátumformáz-t "Y-m-d"-val.
        ho-ba  három-dátumformáz-t     "H:i"-val.

        "Holnap:      "-nyomtat-va.  hf-képernyőre-va.    // 2026-03-22
        "Jövő héten:  "-nyomtat-va.  jh-képernyőre-va.    // 2026-03-28
        "3 óra múlva: "-nyomtat-va.  ho-képernyőre-va.    // 12:05
    ```

!!! tip "Subtracting days"
    The inline literal syntax doesn't support negative number arguments directly. Compute the negative offset first:

    ```ragul
    // English
    neg-into    0-1-sub-it.
    yesterday-into  now-neg-adddays-it.

    // Hungarian
    mínusz-ba   0-1-kivon-t.
    tegnap-ba   most-mínusz-napok-t.
    ```

---

## 4. Unix timestamp round-trip

`-timestamp` / `-időbélyeg` converts a datetime to a float Unix timestamp. `-fromseconds` / `-időpontból` goes the other way. Both use local time, matching `-now` / `-most`.

=== "English"
    ```ragul
    program-ours-effect
        now-into  0-now-it.
        ts-into   now-timestamp-it.
        ts-print-doing.                      // e.g. 1774083907.0

        recovered-into  ts-fromseconds-it.
        rec-into  recovered-dateformat-it  "Y-m-d"-with.
        rec-print-doing.                     // same date as now
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        most-ba    0-most-t.
        bélyeg-be  most-időbélyeg-t.
        bélyeg-képernyőre-va.               // pl. 1774083907.0

        visszaállított-ba  bélyeg-időpontból-t.
        vf-ba  visszaállított-dátumformáz-t  "Y-m-d"-val.
        vf-képernyőre-va.                   // ugyanaz a dátum
    ```

---

## 5. Difference between two datetimes

`-diffseconds` / `-különbség` computes `(arg − self).total_seconds()`. The result is positive when the argument datetime is later than the input.

=== "English"
    ```ragul
    program-ours-effect
        now-into      0-now-it.
        nextweek-into  now-7-adddays-it.

        // nextweek − now = 7 × 86400 = 604800 seconds
        diff-into  now-nextweek-diffseconds-it.
        diff-print-doing.                    // 604800.0
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        most-ba       0-most-t.
        jövőhéten-ba  most-7-napok-t.

        // jövőhéten − most = 7 × 86400 = 604800 másodperc
        különbség-be  most-jövőhéten-különbség-t.
        különbség-képernyőre-va.             // 604800.0
    ```

---

## 6. Parsing a date string

`-parse` / `-dátumértelmez` converts a text string to a datetime using the same PHP format codes used for formatting. It returns a `Hiba` when the string does not match the format.

=== "English"
    ```ragul
    program-ours-effect
        // success → datetime
        parsed-into  "2000-01-01"-parse-it  "Y-m-d"-with.
        yr2k-into    parsed-year-it.
        "Millennium year: "-write-doing.  yr2k-print-doing.    // 2000

        // failure → Hiba value
        bad-into  "not-a-date"-parse-it  "Y-m-d"-with.
        bad-print-doing.    // Hiba("...time data 'not-a-date' does not match...")
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        // siker → datetime
        értelmezett-ba  "2000-01-01"-dátumértelmez-t  "Y-m-d"-val.
        ezredév-be      értelmezett-év-t.
        "Ezredév éve: "-nyomtat-va.  ezredév-képernyőre-va.    // 2000

        // hiba → Hiba érték
        rossz-ba  "nem-dátum"-dátumértelmez-t  "Y-m-d"-val.
        rossz-képernyőre-va.    // Hiba("...does not match...")
    ```

**Supported parse format chars:** `Y y m d H h i s A a D l M F`

**Unsupported for parsing** (return `Hiba`): `n G j w W z U t L` — these are output-only format codes.

---

## 7. Leap year and month length

`L` and `t` are output-only format characters useful for calendar logic.

=== "English"
    ```ragul
    program-ours-effect
        now-into  0-now-it.

        leap-into  now-dateformat-it  "L"-with.
        days-into  now-dateformat-it  "t"-with.

        "Leap year?     "-write-doing.  leap-print-doing.    // "0" or "1"
        "Days in month: "-write-doing.  days-print-doing.    // e.g. "31"
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        most-ba  0-most-t.

        szökőév-be       most-dátumformáz-t  "L"-val.
        hónap-hossza-ba  most-dátumformáz-t  "t"-val.

        "Szökőév?       "-nyomtat-va.  szökőév-képernyőre-va.       // "0" vagy "1"
        "Hónap hossza:  "-nyomtat-va.  hónap-hossza-képernyőre-va.  // pl. "31"
    ```
