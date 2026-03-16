# CSV Processing

Demonstrates the `adatok` module: parsing CSV data, extracting fields, and serializing back to CSV.

=== "English aliases"
    ```ragul
    program-ours-effect
        // Parse inline CSV (\n = newline)
        raw-into      "name,score\nAlice,92\nBob,78\nCarol,85"-it.
        records-into  raw-csv-it.

        // Record count
        count-into  records-len-it.
        count-print-doing.             // 3

        // Extract names from every record
        names-into  records-"name"-field-it.
        names-print-doing.             // ['Alice', 'Bob', 'Carol']

        // Extract scores (string values — use -tonum for arithmetic)
        scores-into  records-"score"-field-it.
        scores-print-doing.            // ['92', '78', '85']

        // First and last record
        first-into  records-first-it.
        last-into   records-last-it.

        first-"name"-field-print-doing.   // Alice
        last-"name"-field-print-doing.    // Carol

        // Serialize back to CSV
        out-into  records-tocsv-it.
        out-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        // CSV szöveg elemzése (\n = sorvége)
        csv_szoveg-ba  "nev,pont\nAlice,92\nBob,78\nCarol,85"-t.
        rekordok-ba    csv_szoveg-csv-t.

        // Rekordszám
        db-ba  rekordok-hossz-t.
        db-képernyőre-va.              // 3

        // Nevek kinyerése
        nevek-ba  rekordok-"nev"-mező-t.
        nevek-képernyőre-va.           // ['Alice', 'Bob', 'Carol']

        // Pontok kinyerése (szöveg értékek)
        pontok-ba  rekordok-"pont"-mező-t.
        pontok-képernyőre-va.          // ['92', '78', '85']

        // Első és utolsó rekord
        elso-ba   rekordok-első-t.
        utolso-ba rekordok-utolsó-t.

        elso-"nev"-mező-képernyőre-va.    // Alice
        utolso-"nev"-mező-képernyőre-va.  // Carol

        // Visszaalakítás CSV-vé
        csv_ki-ba  rekordok-csvné-t.
        csv_ki-képernyőre-va.
    ```

**Output:**

```
3
['Alice', 'Bob', 'Carol']
['92', '78', '85']
Alice
Carol
name,score
Alice,92
Bob,78
Carol,85
```

---

## How CSV parsing works

`-csv` parses a CSV string using the first line as the header row. Each subsequent line becomes a dict mapping field names to string values.

!!! note "CSV values are always strings"
    Unlike JSON, CSV has no type information. Every value is a string after parsing.
    Use `-tonum` / `-számmá` to convert to a number before arithmetic.

=== "English aliases"
    ```ragul
    // Read from a file then parse
    content-into  "orders.csv"-filein-it.
    records-into  content-csv-it.

    // Or chain the operations
    records-into  "orders.csv"-filein-csv-it.
    ```

=== "Hungarian"
    ```ragul
    // Fájlból olvasás és elemzés
    tartalom-ba  "orders.csv"-fájlból-t.
    rekordok-ba  tartalom-csv-t.

    // Vagy láncolt formában
    rekordok-ba  "orders.csv"-fájlból-csv-t.
    ```

---

## Suffix reference

| Hungarian | English | Input | Output | Description |
|---|---|---|---|---|
| `-csv` | `-csv` | `Szöveg` | `Lista` / `Hiba` | Parse CSV string (first row = headers) |
| `-csvné` | `-tocsv` | `Lista` | `Szöveg` | Serialize list of records to CSV |
| `-mező` | `-field` | dict or list | any | Field access (polymorphic) |
| `-mezők` | `-fields` | dict | `Lista-Szöveg` | List all field names |

---

[Download — English](https://github.com/kory75/ragul/blob/master/examples/en/09_csv.ragul) · [Download — Hungarian](https://github.com/kory75/ragul/blob/master/examples/hu/09_csv.ragul)
