# Terminal & Game — képernyő / idő

This example introduces the `képernyő` (terminal I/O) and `idő` (timing) modules, together with the `lista` suffixes that support framebuffer-style grid manipulation. These are the building blocks used in the Téglatörő / Brickbash game (`examples/games/`).

---

## Terminal output without a newline

`-nyomtat` / `-write` writes its value to stdout with no trailing newline, unlike the standard `-képernyőre` / `-print` effect channel.

=== "English"
    ```ragul
    program-ours-effect
        "Row 1: "-write-doing.
        "A"-write-doing.
        " B"-write-doing.
        " C\n"-write-doing.    // newline added explicitly
    // prints: Row 1: A B C
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        "1. sor: "-nyomtat-va.
        "A"-nyomtat-va.
        " B"-nyomtat-va.
        " C\n"-nyomtat-va.
    // kiírja: 1. sor: A B C
    ```

---

## Timed output with `-sleep` / `-vár`

`-sleep` / `-vár` pauses for N milliseconds and is pass-through — it returns its input unchanged.

=== "English"
    ```ragul
    program-ours-effect
        "3"-write-doing.
        0-sleep-it  800-with.
        " 2"-write-doing.
        0-sleep-it  800-with.
        " 1"-write-doing.
        0-sleep-it  800-with.
        " Go!\n"-write-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        "3"-nyomtat-va.
        0-vár-t  800-val.
        " 2"-nyomtat-va.
        0-vár-t  800-val.
        " 1"-nyomtat-va.
        0-vár-t  800-val.
        " Rajt!\n"-nyomtat-va.
    ```

---

## Building a grid with `-repeat`, `-set`, `-index`, and `-chars`

A framebuffer is a `List[List[str]]` — a 2-D grid of single characters. These four suffixes build and manipulate it.

| Suffix | Role |
|---|---|
| `-repeat` / `-ismét` | Fill a row with N copies of a character |
| `-chars` / `-karakterek` | Split a string into a character list (for loading from a file) |
| `-set` / `-beállít` | Non-mutating replace at index (returns a new list) |
| `-index` / `-index` | Read element at index |

=== "English"
    ```ragul
    program-ours-effect
        // Build a 5-column row of dots
        row-into  "."-repeat-it  5-with.
        row-print-doing.             // ['.', '.', '.', '.', '.']

        // Stamp an X in the middle
        row-into  row-set-it  2-with  "X"-with.
        row-print-doing.             // ['.', '.', 'X', '.', '.']

        // Read back the centre cell
        centre-into  row-index-it  2-with.
        centre-print-doing.          // X

        // Build a 3-row grid from strings
        grid-into  []-it.
        grid-into  grid-"###"-chars-append-it.
        grid-into  grid-"#.#"-chars-append-it.
        grid-into  grid-"###"-chars-append-it.

        // Replace centre cell of middle row
        mid-into   grid-index-it  1-with.     // ['#', '.', '#']
        mid-into   mid-set-it  1-with  "O"-with.
        grid-into  grid-set-it  1-with  mid-with.
        grid-print-doing.
        // [['#', '#', '#'], ['#', 'O', '#'], ['#', '#', '#']]
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        // 5 oszlopos sor pontokból
        sor-ba  "."-ismét-t  5-val.
        sor-képernyőre-va.           // ['.', '.', '.', '.', '.']

        // X a közepébe
        sor-ba  sor-beállít-t  2-val  "X"-val.
        sor-képernyőre-va.           // ['.', '.', 'X', '.', '.']

        // Középső cella visszaolvasása
        közép-ba  sor-index-t  2-val.
        közép-képernyőre-va.         // X

        // 3 soros rács szövegből
        rács-ba  []-t.
        rács-ba  rács-"###"-karakterek-hozzáad-t.
        rács-ba  rács-"#.#"-karakterek-hozzáad-t.
        rács-ba  rács-"###"-karakterek-hozzáad-t.

        // Középső sor közepének cseréje
        sor-ba   rács-index-t  1-val.     // ['#', '.', '#']
        sor-ba   sor-beállít-t  1-val  "O"-val.
        rács-ba  rács-beállít-t  1-val  sor-val.
        rács-képernyőre-va.
        // [['#', '#', '#'], ['#', 'O', '#'], ['#', '#', '#']]
    ```

---

## Rendering a framebuffer with `-render` / `-rajzol`

`-render` / `-rajzol` takes a `List[List[str]]`, enters the terminal **alternate screen buffer** (on first call), and draws each row as a line.
`-clear` / `-töröl` exits the alternate screen so the game-over message appears in the normal shell history.

=== "English"
    ```ragul
    program-ours-effect
        // Build a tiny 3 × 5 grid
        empty-into  " "-repeat-it  5-with.
        grid-into   empty-repeat-it  3-with.

        // Draw a cross
        r1-into   grid-index-it  1-with.
        r1-into   r1-set-it  2-with  "+"-with.
        grid-into grid-set-it  1-with  r1-with.

        // Render loop — 10 frames
        i-into  0-it.
        loop-ours-while
            i-10-below-it.
            grid-render-doing.
            0-sleep-it  100-with.
            i-into  i-1-add-it.

        0-clear-doing.
        "Done.\n"-write-doing.
    ```

=== "Hungarian"
    ```ragul
    program-nk-hatás
        üres-ba   " "-ismét-t  5-val.
        rács-ba   üres-ismét-t  3-val.

        s1-ba     rács-index-t  1-val.
        s1-ba     s1-beállít-t  2-val  "+"-val.
        rács-ba   rács-beállít-t  1-val  s1-val.

        i-ba  0-t.
        ciklus-unk-míg
            i-10-alatt-t.
            rács-rajzol-va.
            0-vár-t  100-val.
            i-ba  i-1-össze-t.

        0-töröl-va.
        "Kész.\n"-nyomtat-va.
    ```

---

## The game

The full Téglatörő / Brickbash game combines all of the above — level loading from a file, a game loop driven by `-key` / `-billentyű`, grid cell updates with `-set` + `-index`, and rendering with `-render`. Run it from the project root:

```
ragul futtat examples/games/téglatörő.ragul    # Hungarian
ragul run    examples/games/en/brickbash.ragul  # English
```

Source: `examples/games/téglatörő.ragul` · `examples/games/hu/téglatörő.ragul` · `examples/games/en/brickbash.ragul`
