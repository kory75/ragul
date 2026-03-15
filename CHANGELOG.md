# Changelog

All notable changes to `ragul-lang` are documented here.

---

## [0.1.1] — 2026-03-15

### Added
- `ragul new project <name>` / `ragul új projekt <name>` — scaffold a new project folder with `ragul.config`, `main.ragul`, `.gitignore`, and `README.md`
- `ragul new module <name>` / `ragul új modul <name>` — scaffold a new module file inside an existing project
- Bilingual example files: `examples/en/` (English aliases) and `examples/hu/` (Hungarian)
- English aliases for all branch openers: `-catch` (= `-hibára`), `-else` (= `-hanem`), `-elif` (= `-különben`)
- MkDocs documentation site deployed to GitHub Pages

### Fixed
- Lexer now correctly alias-normalises standalone suffix-chain tokens that appear after string or number literals (e.g. `"Hello"-it`, `s-"needle"-contains-it`, `"x"-tonum-doing-?`)
- pygls 2.0 LSP compatibility (`text_document_publish_diagnostics` + `PublishDiagnosticsParams`)
- Windows console encoding: replaced non-ASCII characters in CLI output

### Changed
- English aliases tab is now the default (first) tab in all documentation examples
- `examples/` reorganised into `examples/en/` and `examples/hu/` subdirectories
- README rewritten with English-alias examples and PyPI install as primary install path
- `-obj` English alias renamed to `-it` (more natural, avoids OOP connotations)
- `->` shorthand replaced with `-into` in all documentation and examples

---

## [0.1.0] — 2026-03-13

### Added
- Full language toolchain: lexer, parser, type checker, tree-walking interpreter
- Suffix alias normalisation at lex time — English aliases map silently to canonical Hungarian forms
- CLI: `ragul run`, `ragul check`, `ragul repl`, `ragul lsp`
- Interactive REPL with persistent environment and `:help`, `:show`, `:clear`, `:exit` commands
- pygls LSP server: diagnostics, hover (inferred type), completion (suffix trigger on `-`), go-to-definition
- Standard library: arithmetic, comparison, logical, string, and list operations
- Agent architecture: `OrchestratorAgent` + 7 specialist agents; optional Claude Opus 4.6 AI error analysis
- GitHub Actions CI (pytest + mypy) and docs deployment workflow
- `ragul.config` dogfood project config at repo root
