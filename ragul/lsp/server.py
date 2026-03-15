"""
ragul/lsp/server.py — pygls-based LSP server for the Ragul language.

Features:
  • Diagnostics  — type errors and warnings on every file change
  • Hover        — inferred type of token under cursor
  • Completion   — valid suffixes for the current root's type
  • Go-to-def    — jump to scope definition

Start via:  ragul lsp
Editor setup:
  VS Code:  set server command to "ragul lsp"
  Neovim:   nvim-lspconfig custom server pointing to "ragul lsp"
"""

from __future__ import annotations
import logging
try:
    from pygls.lsp.server import LanguageServer  # pygls >= 2.0
    _PYGLS2 = True
except ImportError:
    from pygls.server import LanguageServer  # type: ignore[attr-defined, no-redef]  # pygls 1.x
    _PYGLS2 = False
from lsprotocol.types import (
    TEXT_DOCUMENT_DID_OPEN,
    TEXT_DOCUMENT_DID_CHANGE,
    TEXT_DOCUMENT_DID_SAVE,
    TEXT_DOCUMENT_HOVER,
    TEXT_DOCUMENT_COMPLETION,
    TEXT_DOCUMENT_DEFINITION,
    DidOpenTextDocumentParams,
    DidChangeTextDocumentParams,
    DidSaveTextDocumentParams,
    HoverParams,
    CompletionParams,
    DefinitionParams,
    Location,
    Position,
    PublishDiagnosticsParams,
    Range,
    CompletionOptions,
)

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Server instance
# ---------------------------------------------------------------------------

server = LanguageServer(
    name="ragul-lsp",
    version="0.1.0",
)


# ---------------------------------------------------------------------------
# Helper: publish diagnostics for a document
# ---------------------------------------------------------------------------

def _publish_diagnostics(ls: LanguageServer, uri: str, source: str) -> None:
    from ragul.lsp.diagnostics import build_diagnostics
    filename = uri.replace("file://", "")
    diags = build_diagnostics(source, filename)
    if _PYGLS2:
        ls.text_document_publish_diagnostics(
            PublishDiagnosticsParams(uri=uri, diagnostics=diags)
        )
    else:
        ls.publish_diagnostics(uri, diags)  # type: ignore[attr-defined]


# ---------------------------------------------------------------------------
# textDocument/didOpen
# ---------------------------------------------------------------------------

@server.feature(TEXT_DOCUMENT_DID_OPEN)
def did_open(ls: LanguageServer, params: DidOpenTextDocumentParams) -> None:
    doc = params.text_document
    _publish_diagnostics(ls, doc.uri, doc.text)


# ---------------------------------------------------------------------------
# textDocument/didChange
# ---------------------------------------------------------------------------

@server.feature(TEXT_DOCUMENT_DID_CHANGE)
def did_change(ls: LanguageServer, params: DidChangeTextDocumentParams) -> None:
    uri    = params.text_document.uri
    source = params.content_changes[-1].text
    _publish_diagnostics(ls, uri, source)


# ---------------------------------------------------------------------------
# textDocument/didSave
# ---------------------------------------------------------------------------

@server.feature(TEXT_DOCUMENT_DID_SAVE)
def did_save(ls: LanguageServer, params: DidSaveTextDocumentParams) -> None:
    uri = params.text_document.uri
    doc = ls.workspace.get_text_document(uri)
    _publish_diagnostics(ls, uri, doc.source)


# ---------------------------------------------------------------------------
# textDocument/hover
# ---------------------------------------------------------------------------

@server.feature(TEXT_DOCUMENT_HOVER)
def hover(ls: LanguageServer, params: HoverParams):
    from ragul.lsp.hover import get_hover
    uri  = params.text_document.uri
    doc  = ls.workspace.get_text_document(uri)
    pos  = params.position
    return get_hover(doc.source, uri.replace("file://", ""), pos.line, pos.character)


# ---------------------------------------------------------------------------
# textDocument/completion
# ---------------------------------------------------------------------------

@server.feature(
    TEXT_DOCUMENT_COMPLETION,
    CompletionOptions(trigger_characters=["-"]),
)
def completion(ls: LanguageServer, params: CompletionParams):
    from ragul.lsp.completion import get_completions
    uri = params.text_document.uri
    doc = ls.workspace.get_text_document(uri)
    pos = params.position
    return get_completions(
        doc.source,
        uri.replace("file://", ""),
        pos.line,
        pos.character,
    )


# ---------------------------------------------------------------------------
# textDocument/definition
# ---------------------------------------------------------------------------

@server.feature(TEXT_DOCUMENT_DEFINITION)
def definition(ls: LanguageServer, params: DefinitionParams):
    """Go-to-definition: jump to the -unk scope that defines a suffix."""
    from ragul.lexer import lex, TT
    from ragul.parser import parse

    uri    = params.text_document.uri
    doc    = ls.workspace.get_text_document(uri)
    source = doc.source
    pos    = params.position

    try:
        tokens, _ = lex(source, uri.replace("file://", ""))
        tree, _   = parse(tokens, uri.replace("file://", ""))

        # Find the root name at cursor
        target_line = pos.line + 1
        root_name   = None
        for tok in tokens:
            if tok.type not in (TT.WORD, TT.SCOPE_OPEN):
                continue
            if tok.line != target_line:
                continue
            if tok.col <= pos.character <= tok.col + len(tok.value):
                root_name = tok.value.split("-")[0]
                break

        if root_name is None:
            return None

        # Find scope with that name in the tree
        def _find_scope(scope, name):
            for child in scope.children:
                if child.name == name:
                    return child
                found = _find_scope(child, name)
                if found:
                    return found
            return None

        target_scope = _find_scope(tree, root_name)
        if target_scope is None:
            return None

        # Find the token that opened this scope
        for tok in tokens:
            if tok.type == TT.SCOPE_OPEN and tok.value.startswith(root_name):
                def_line = tok.line - 1  # 0-indexed
                return Location(
                    uri=uri,
                    range=Range(
                        start=Position(line=def_line, character=tok.col),
                        end=Position(line=def_line, character=tok.col + len(tok.value)),
                    ),
                )

    except Exception as e:
        log.error("definition error: %s", e)

    return None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def run_lsp_server() -> None:
    """Start the LSP server in stdio mode."""
    logging.basicConfig(level=logging.WARNING)
    server.start_io()
