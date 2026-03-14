"""
ragul/tests/test_agents.py — Tests for the agent architecture.

Covers: Task/TaskResult protocol, all specialist agents, OrchestratorAgent pipelines.
Does NOT test DocsAgent (requires ANTHROPIC_API_KEY and live API).
"""

import pytest
from ragul.agents.task import Task, TaskResult
from ragul.agents.lexer_agent import LexerAgent
from ragul.agents.parser_agent import ParserAgent
from ragul.agents.typecheck_agent import TypeAgent
from ragul.agents.interpreter_agent import InterpAgent
from ragul.agents.orchestrator import OrchestratorAgent
from ragul.config import RagulConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_cfg() -> RagulConfig:
    return RagulConfig()


# ---------------------------------------------------------------------------
# Task / TaskResult
# ---------------------------------------------------------------------------

class TestTaskProtocol:

    def test_task_defaults(self):
        t = Task(kind="lex")
        assert t.filename == "<unknown>"
        assert t.source is None
        assert t.tokens is None
        assert t.scope_tree is None
        assert t.flags == {}

    def test_task_result_defaults(self):
        r = TaskResult(ok=True)
        assert r.exit_code == 0
        assert r.errors == []
        assert r.warnings == []
        assert r.ai_analysis is None


# ---------------------------------------------------------------------------
# LexerAgent
# ---------------------------------------------------------------------------

class TestLexerAgent:

    def test_lex_clean_source(self):
        agent  = LexerAgent()
        result = agent.run(Task(kind="lex", source="x-ba  3-t.", filename="<test>"))
        assert result.ok
        assert result.exit_code == 0
        assert result.payload is not None
        assert len(result.errors) == 0

    def test_lex_empty_source(self):
        agent  = LexerAgent()
        result = agent.run(Task(kind="lex", source=None))
        assert not result.ok
        assert result.exit_code == 1

    def test_lex_returns_tokens(self):
        from ragul.lexer import TT
        agent  = LexerAgent()
        result = agent.run(Task(kind="lex", source='y-ba  "hello"-t.'))
        assert result.ok
        types = [t.type for t in result.payload]
        assert TT.FULLSTOP in types


# ---------------------------------------------------------------------------
# ParserAgent
# ---------------------------------------------------------------------------

class TestParserAgent:

    def _lex(self, source: str):
        from ragul.lexer import lex
        tokens, _ = lex(source, "<test>")
        return tokens

    def test_parse_simple(self):
        agent  = ParserAgent()
        result = agent.run(Task(kind="parse", tokens=self._lex("x-ba  3-t.")))
        assert result.ok
        assert result.payload is not None   # Scope

    def test_parse_no_tokens(self):
        agent  = ParserAgent()
        result = agent.run(Task(kind="parse", tokens=None))
        assert not result.ok

    def test_parse_scope(self):
        source = "számítás-unk\n\tx-ba  3-t.\n"
        agent  = ParserAgent()
        result = agent.run(Task(kind="parse", tokens=self._lex(source)))
        assert result.ok
        assert any(c.name == "számítás" for c in result.payload.children)


# ---------------------------------------------------------------------------
# TypeAgent
# ---------------------------------------------------------------------------

class TestTypeAgent:

    def _scope(self, source: str):
        from ragul.lexer import lex
        from ragul.parser import parse
        tokens, _ = lex(source, "<test>")
        tree, _   = parse(tokens, "<test>")
        return tree

    def test_type_clean(self):
        agent  = TypeAgent()
        result = agent.run(Task(kind="typecheck",
                                scope_tree=self._scope("x-ba  3-t."),
                                config=make_cfg()))
        assert result.ok
        assert len(result.errors) == 0

    def test_type_no_tree(self):
        agent  = TypeAgent()
        result = agent.run(Task(kind="typecheck", scope_tree=None))
        assert not result.ok

    def test_type_e001_detected(self):
        agent  = TypeAgent()
        result = agent.run(Task(kind="typecheck",
                                scope_tree=self._scope('x-ba  "hello"-5-felett-t.'),
                                config=make_cfg()))
        assert not result.ok
        assert any(d.code == "E001" for d in result.errors)

    def test_type_e004_detected(self):
        agent  = TypeAgent()
        result = agent.run(Task(kind="typecheck",
                                scope_tree=self._scope("x-ba  3-t.\nx-képernyőre-va."),
                                config=make_cfg()))
        assert not result.ok
        assert any(d.code == "E004" for d in result.errors)


# ---------------------------------------------------------------------------
# InterpAgent
# ---------------------------------------------------------------------------

class TestInterpAgent:

    def _scope(self, source: str):
        from ragul.lexer import lex
        from ragul.parser import parse
        tokens, _ = lex(source, "<test>")
        tree, _   = parse(tokens, "<test>")
        return tree

    def test_interp_assignment(self):
        agent  = InterpAgent()
        result = agent.run(Task(kind="interpret",
                                scope_tree=self._scope("x-ba  42-t.")))
        assert result.ok
        assert result.exit_code == 0
        assert result.payload.get("x") == 42

    def test_interp_no_tree(self):
        agent  = InterpAgent()
        result = agent.run(Task(kind="interpret", scope_tree=None))
        assert not result.ok
        assert result.exit_code == 2

    def test_interp_arithmetic(self):
        agent  = InterpAgent()
        result = agent.run(Task(kind="interpret",
                                scope_tree=self._scope("x-ba  3-t.\ny-ba  x-4-össze-t.")))
        assert result.ok
        assert result.payload.get("y") == 7


# ---------------------------------------------------------------------------
# OrchestratorAgent
# ---------------------------------------------------------------------------

class TestOrchestratorAgent:

    def test_futtat_clean(self):
        orch   = OrchestratorAgent(config=make_cfg())
        result = orch.run("futtat", source="x-ba  5-t.", filename="<test>")
        assert result.ok
        assert result.exit_code == 0

    def test_ellenőriz_clean(self):
        orch   = OrchestratorAgent(config=make_cfg())
        result = orch.run("ellenőriz", source="x-ba  5-t.", filename="<test>")
        assert result.ok
        assert result.exit_code == 0

    def test_ellenőriz_type_error(self):
        orch   = OrchestratorAgent(config=make_cfg())
        result = orch.run("ellenőriz",
                          source='x-ba  "hello"-5-felett-t.',
                          filename="<test>")
        assert not result.ok
        assert any(d.code == "E001" for d in result.errors)

    def test_fordít_stub(self):
        orch   = OrchestratorAgent(config=make_cfg())
        result = orch.run("fordít", source="x-ba  1-t.")
        assert result.ok        # stub returns ok=True with a message

    def test_unknown_command(self):
        orch   = OrchestratorAgent(config=make_cfg())
        result = orch.run("nincs-ilyen")
        assert not result.ok

    def test_no_api_key_no_analysis(self, monkeypatch):
        """Without ANTHROPIC_API_KEY, ai_analysis stays None."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        orch   = OrchestratorAgent(config=make_cfg())
        result = orch.run("ellenőriz",
                          source='x-ba  "hello"-5-felett-t.',
                          filename="<test>")
        assert not result.ok
        assert result.ai_analysis is None

    def test_hello_world_effect_scope(self):
        source = 'program-nk-hatás\n\tx-ba  "helló világ"-t.\n\tx-képernyőre-va.\n'
        orch   = OrchestratorAgent(config=make_cfg())
        result = orch.run("futtat", source=source, filename="<test>")
        assert result.ok
        assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
