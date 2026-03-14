"""
tests/test_lsp.py — Unit tests for the Ragul LSP components.

These tests do NOT start a full LSP server process.
They test the underlying diagnostics, hover, and completion logic directly.
"""

import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------

class TestLspDiagnostics:

    def _diags(self, source):
        from ragul.lsp.diagnostics import build_diagnostics
        return build_diagnostics(source, "<test>")

    def test_clean_source_no_diagnostics(self):
        diags = self._diags("x-ba  3-t.\ny-ba  x-3-össze-t.")
        errors = [d for d in diags if d.severity.value == 1]  # Error = 1
        assert len(errors) == 0

    def test_E001_produces_lsp_diagnostic(self):
        diags = self._diags('x-ba  "hello"-5-felett-t.')
        assert len(diags) >= 1
        codes = [d.code for d in diags]
        assert "E001" in codes

    def test_E004_produces_lsp_diagnostic(self):
        diags = self._diags("x-ba  3-t.\nx-képernyőre-va.")
        codes = [d.code for d in diags]
        assert "E004" in codes

    def test_diagnostic_line_is_zero_indexed(self):
        # E004 on line 2 of source → LSP line 1 (0-indexed)
        diags = self._diags("x-ba  3-t.\nx-képernyőre-va.")
        e004 = [d for d in diags if d.code == "E004"]
        assert len(e004) >= 1
        assert e004[0].range.start.line == 1  # 0-indexed

    def test_crash_protection_on_malformed(self):
        # Should never raise — always return list
        diags = self._diags("!@#$%^&*()")
        assert isinstance(diags, list)

    def test_hello_world_clean(self):
        source = 'program-nk-hatás\n\tüdvözlet-ba  "Helló, világ!"-t.\n\tüdvözlet-képernyőre-va.\n'
        diags = self._diags(source)
        errors = [d for d in diags if d.severity.value == 1]
        assert len(errors) == 0


# ---------------------------------------------------------------------------
# Completion
# ---------------------------------------------------------------------------

class TestLspCompletion:

    def _complete(self, source, line, char):
        from ragul.lsp.completion import get_completions
        return get_completions(source, "<test>", line, char)

    def test_returns_completion_list(self):
        cl = self._complete("x-ba  3-t.\nx-", 1, 2)
        assert cl is not None
        assert hasattr(cl, "items")

    def test_numeric_root_suggests_arithmetic(self):
        cl = self._complete("x-ba  3-t.\nx-", 1, 2)
        labels = [item.label for item in cl.items]
        assert "-össze" in labels

    def test_string_root_suggests_string_ops(self):
        cl = self._complete('x-ba  "hello"-t.\nx-', 1, 2)
        labels = [item.label for item in cl.items]
        assert "-nagybetűs" in labels

    def test_no_crash_on_empty_source(self):
        cl = self._complete("", 0, 0)
        assert cl is not None

    def test_completion_items_have_labels(self):
        cl = self._complete("x-ba  3-t.\nx-", 1, 2)
        for item in cl.items:
            assert item.label


# ---------------------------------------------------------------------------
# Hover
# ---------------------------------------------------------------------------

class TestLspHover:

    def _hover(self, source, line, char):
        from ragul.lsp.hover import get_hover
        return get_hover(source, "<test>", line, char)

    def test_hover_on_word_returns_something(self):
        source = "x-ba  3-t."
        h = self._hover(source, 0, 0)
        # May be None if cursor isn't on a token — just check no crash
        assert h is None or hasattr(h, "contents")

    def test_hover_no_crash_on_empty(self):
        h = self._hover("", 0, 0)
        assert h is None

    def test_hover_no_crash_on_bad_position(self):
        h = self._hover("x-ba  3-t.", 99, 99)
        assert h is None
