# JSON Parsing

Demonstrates the `adatok` module: parsing JSON, accessing fields, and serializing back to JSON.

=== "English aliases"
    ```ragul
    program-ours-effect
        // Parse a JSON array
        records-into  "[{\"name\": \"Alice\", \"score\": 92}, {\"name\": \"Bob\", \"score\": 78}, {\"name\": \"Carol\", \"score\": 85}]"-json-it.

        // Access fields from the first record
        first-into  records-first-it.
        name-into   first-"name"-field-it.
        score-into  first-"score"-field-it.

        name-print-doing.              // Alice
        score-print-doing.             // 92

        // Extract one field from every record (polymorphic -field on a list)
        names-into   records-"name"-field-it.
        names-print-doing.             // ['Alice', 'Bob', 'Carol']

        // Sum all scores
        scores-into  records-"score"-map-it.
        total-into   scores-sum-it.
        total-print-doing.             // 255

        // Record count
        count-into  records-len-it.
        count-print-doing.             // 3

        // Serialize back to JSON
        output-into  records-tojson-it.
        output-print-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        // JSON szöveg elemzése
        rekordok-ba  "[{\"nev\": \"Alice\", \"pont\": 92}, {\"nev\": \"Bob\", \"pont\": 78}, {\"nev\": \"Carol\", \"pont\": 85}]"-json-t.

        // Első rekord mezői
        elso-ba  rekordok-első-t.
        nev-ba   elso-"nev"-mező-t.
        pont-ba  elso-"pont"-mező-t.

        nev-képernyőre-va.             // Alice
        pont-képernyőre-va.            // 92

        // Egy mező kinyerése minden rekordból (polimorf -mező)
        nevek-ba   rekordok-"nev"-mező-t.
        nevek-képernyőre-va.           // ['Alice', 'Bob', 'Carol']

        // Pontok összeadása
        pontok-ba  rekordok-"pont"-mező-t.
        osszeg-ba  pontok-összeg-t.
        osszeg-képernyőre-va.          // 255

        // Rekordszám
        db-ba  rekordok-hossz-t.
        db-képernyőre-va.              // 3

        // Visszaalakítás JSON-né
        kimenet-ba  rekordok-jsonná-t.
        kimenet-képernyőre-va.
    ```

**Output:**

```
Alice
92
['Alice', 'Bob', 'Carol']
255
3
[{"name": "Alice", "score": 92}, {"name": "Bob", "score": 78}, {"name": "Carol", "score": 85}]
```

---

## How JSON parsing works

`-json` parses a JSON string into a native Ragul value. JSON objects become dicts, arrays become lists, numbers stay numbers, strings stay strings.

=== "English aliases"
    ```ragul
    data-into  "{\"x\": 1, \"y\": 2}"-json-it.   // dict
    arr-into   "[1, 2, 3]"-json-it.              // list
    n-into     "42"-json-it.                     // number
    ```

=== "Hungarian"
    ```ragul
    adat-ba  "{\"x\": 1, \"y\": 2}"-json-t.
    tomb-ba  "[1, 2, 3]"-json-t.
    n-ba     "42"-json-t.
    ```

On parse failure, `-json` returns a `Hiba` value.

---

## Field access — `-field` / `-mező`

`-field` accesses a named field. It is **polymorphic**: on a single dict it returns the value; on a list it extracts the field from every item.

=== "English aliases"
    ```ragul
    record-into  "{\"name\": \"Alice\", \"score\": 92}"-json-it.
    name-into    record-"name"-field-it.     // "Alice"

    // Polymorphic: list of dicts → list of field values
    names-into   records-"name"-field-it.   // ["Alice", "Bob", ...]
    ```

=== "Hungarian"
    ```ragul
    rekord-ba  "{\"nev\": \"Alice\", \"pont\": 92}"-json-t.
    nev-ba     rekord-"nev"-mező-t.          // "Alice"

    nevek-ba   rekordok-"nev"-mező-t.        // ["Alice", "Bob", ...]
    ```

---

## Suffix reference

| Hungarian | English | Input | Output | Description |
|---|---|---|---|---|
| `-json` | `-json` | `Szöveg` | any / `Hiba` | Parse JSON string |
| `-jsonná` | `-tojson` | any | `Szöveg` | Serialize to JSON string |
| `-mező` | `-field` | dict or list | any | Field access (polymorphic) |
| `-mezők` | `-fields` | dict | `Lista-Szöveg` | List all field names |
| `-térképezve` | `-map` | `Lista` | `Lista` | Extract a field from every item |
| `-összeg` | `-sum` | `Lista-Szám` | `Szám` | Sum a list of numbers |

---

[Download — English](https://github.com/kory75/ragul/blob/master/examples/en/08_json.ragul) · [Download — Hungarian](https://github.com/kory75/ragul/blob/master/examples/hu/08_json.ragul)
