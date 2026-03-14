# Tooling & CLI

## Installation

Ragul is not yet on PyPI. Install from source:

```bash
git clone https://github.com/kory75/ragul.git
cd ragul
pip install -e ".[dev]"
```

---

## CLI Commands

All commands support Hungarian primary names and English aliases.

### `ragul futtat` / `ragul run`

Run a Ragul program:

```bash
ragul futtat hello.ragul
ragul run hello.ragul
ragul futtat main.ragul --config ragul.config
```

### `ragul ellenőriz` / `ragul check`

Type-check a file and report diagnostics without running it:

```bash
ragul ellenőriz hello.ragul
ragul check hello.ragul --strict
```

With `--strict`, harmony and type warnings become errors.

### `ragul fordít` / `ragul compile`

Compile to bytecode (not yet implemented in v0.1.0 — use `futtat` instead):

```bash
ragul fordít main.ragul --out ./build
```

### `ragul repl`

Start the interactive REPL:

```bash
ragul repl
```

```
>>> x-be  3-t.
>>> x-kétszeres-ból  kimenet-be  ír-va.
6
>>>
```

REPL special commands:

| Command | Action |
|---|---|
| `:kilep` / `:exit` | Quit |
| `:töröl` / `:clear` | Reset the environment |
| `:mutat` / `:show` | Print all bound roots and their types |
| `:help` / `:súgó` | Show help |

### `ragul lsp`

Start the LSP server for editor integration:

```bash
ragul lsp
```

Point your editor at this command to get diagnostics, hover types, completions, and go-to-definition. See [Editor Integration](#editor-integration) below.

---

## `ragul.config`

Place a `ragul.config` file at your project root. The format uses Hungarian TOML keys (dogfooding the language's design philosophy):

```toml
[projekt]
nev     = "my-project"
verzio  = "0.1.0"
belepes = "main.ragul"

[fordito]
cel    = "interpret"
python = "3.11"

[modulok]
utvonalak = ["./lib"]

[ellenorzes]
harmonia = "warn"    # "warn" | "strict" | "off"
tipus    = "warn"    # "warn" | "strict" | "off"

[hibak]
nyelv = "en"         # "en" | "hu"
```

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | Compile error (lexer, parser, or type checker) |
| `2` | Runtime error |
| `3` | Unhandled `Hiba` reached the program boundary |

---

## Compiler Error & Warning Codes

### Errors

| Code | Name | Description |
|---|---|---|
| E001 | Root guard failure | The root's type does not support this suffix |
| E002 | Suffix layer order | Suffix layers are out of order in the chain |
| E003 | Parallel write conflict | Same root written twice in a pure scope |
| E004 | Effect boundary violation | Effectful suffix called from a pure scope |
| E005 | Unhandled `vagy` type | Fallible result used without `-e` or `-hibára` |
| E009 | Field mutation outside `-hatás` | Mutation of a field outside an effect scope |

### Warnings

| Code | Name | Description |
|---|---|---|
| W001 | Harmony warning | Type boundary crossed without a bridge suffix |

---

## Editor Integration

### VS Code

Create `.vscode/settings.json` in your project:

```json
{
  "ragul.lsp.command": ["ragul", "lsp"]
}
```

A VS Code extension manifest pointing to `ragul lsp` as the server command enables full LSP support.

### Neovim

Add to your `nvim-lspconfig` setup:

```lua
require('lspconfig').ragul.setup {
  cmd = { 'ragul', 'lsp' },
  filetypes = { 'ragul' },
  root_dir = require('lspconfig.util').root_pattern('ragul.config'),
}
```

---

## Running Tests

```bash
pytest ragul/tests/ --tb=short
```

With type checking:

```bash
python -m mypy ragul/ --ignore-missing-imports
```
