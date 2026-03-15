# Ragul — Future Ideas

## VS Code Extension

- **Create project** — command that scaffolds a new Ragul project folder with `ragul.config`, `hello.ragul`, and `.gitignore`
- **Run project** — reads `ragul.config` for the entry point and runs it, no file selection needed
- **Snippets** — type `scope` → full `-unk` block scaffold, `loop` → `-mindegyik` block, etc.
- **Syntax theme** — dedicated colour theme making suffix chains visually distinct from roots
- **Status bar item** — persistent display of the inferred type of the word under the cursor
- **Problem matcher** — parse `ragul ellenőriz` output so errors appear in the VS Code Problems panel, not just the terminal

---

## CLI (`ragul` command)

- **`ragul új` / `ragul new`** — scaffold a new project: creates folder, `ragul.config`, `main.ragul`, `.gitignore`
- **`ragul formáz` / `ragul fmt`** — auto-formatter: normalise indentation, suffix spacing, and line endings
- **`ragul csomag` / `ragul pkg`** — package manager: install/publish Ragul modules from a registry
- **`ragul teszt` / `ragul test`** — built-in test runner for `.ragul` test files
- **`ragul doc`** — generate documentation from inline comments in `.ragul` source files
- **`ragul info`** — show version, config values, and detected entry point
- **`ragul tisztít` / `ragul clean`** — remove build artefacts and caches
- **`ragul frissít` / `ragul upgrade`** — self-update the ragul toolchain

---

## Other Tooling

- **Formatter (`ragul formáz`)** — auto-indent and normalise suffix spacing, usable as a pre-commit hook
- **Debugger** — step through a `.ragul` file sentence by sentence, inspect variable values at each step
- **Package registry** — a way to share and import Ragul modules (like PyPI but for `.ragul` packages)
- **Browser playground** — browser-based REPL built with PyScript or a small web server; shareable links
- **Tree-sitter grammar** — structural queries and better highlighting for Neovim, Helix, and other editors
- **Pre-commit hook** — run `ragul ellenőriz` + `ragul formáz` automatically before every git commit
