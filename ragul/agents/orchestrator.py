"""
ragul/agents/orchestrator.py — Top-level orchestrator for the Ragul toolchain.

The orchestrator:
  - Reads ragul.config
  - Receives a command: "futtat" | "ellenőriz" | "fordít" | "repl" | "lsp"
  - Builds the appropriate task pipeline (Lex → Parse → TypeCheck → Interpret)
  - Delegates every stage to the matching specialist agent via Task objects
  - Collects TaskResults and returns a final TaskResult to the caller

Claude integration (requires ANTHROPIC_API_KEY):
  When compiler diagnostics are found (errors or warnings), the orchestrator
  calls Claude Opus 4.6 to generate a plain-English explanation with actionable
  fix suggestions.  If the API key is absent the pipeline still works normally —
  the ai_analysis field of the returned TaskResult will simply be None.
"""

from __future__ import annotations
import os

from ragul.agents.task import Task, TaskResult
from ragul.agents.lexer_agent import LexerAgent
from ragul.agents.parser_agent import ParserAgent
from ragul.agents.typecheck_agent import TypeAgent
from ragul.agents.interpreter_agent import InterpAgent
from ragul.agents.repl_agent import ReplAgent
from ragul.agents.lsp_agent import LspAgent
from ragul.config import RagulConfig


_ANALYSIS_SYSTEM = """\
You are a Ragul language compiler assistant. Ragul is an experimental programming \
language modelled on agglutinative grammar (Hungarian suffix stacking).

When given Ragul source code and a list of compiler diagnostics, you analyse them \
and provide a clear, actionable explanation:

- What went wrong and why (in plain English, not jargon)
- The specific line(s) involved
- Exactly how to fix the problem
- A corrected code snippet where helpful

Be concise. Use the error codes (E001–E009, W001) as reference headings.
"""


class OrchestratorAgent:
    """
    Coordinates the full Ragul compilation/execution pipeline.

    Usage:
        orch   = OrchestratorAgent()
        result = orch.run("futtat", source="...", filename="main.ragul")

    The returned TaskResult carries:
        .ok          — True if the pipeline completed without errors
        .exit_code   — POSIX exit code to hand to sys.exit()
        .errors      — list of RagulDiagnostic objects
        .warnings    — list of RagulDiagnostic objects
        .ai_analysis — Claude's error explanation (str | None)
    """

    def __init__(self, config: RagulConfig | None = None) -> None:
        self.config  = config or RagulConfig.load()
        self._lexer  = LexerAgent()
        self._parser = ParserAgent()
        self._type   = TypeAgent()
        self._interp = InterpAgent()
        self._repl   = ReplAgent()
        self._lsp    = LspAgent()

    # ------------------------------------------------------------------
    # Public dispatch
    # ------------------------------------------------------------------

    def run(
        self,
        command: str,
        source: str | None = None,
        filename: str = "<unknown>",
        flags: dict | None = None,
    ) -> TaskResult:
        """
        Dispatch command to the appropriate pipeline.

        command: "futtat" | "run" | "ellenőriz" | "check" | "fordít" | "repl" | "lsp"
        source:  raw Ragul source text (required for futtat / ellenőriz / fordít)
        """
        flags = flags or {}

        if command in ("futtat", "run"):
            return self._pipeline_run(source or "", filename, flags)

        elif command in ("ellenőriz", "check"):
            return self._pipeline_check(source or "", filename, flags)

        elif command in ("fordít", "compile"):
            return TaskResult(
                ok=True,
                exit_code=0,
                ai_analysis=(
                    "Bytecode compilation is not yet implemented in v1.\n"
                    "Use 'ragul futtat' to run programs via the interpreter."
                ),
            )

        elif command == "repl":
            return self._repl.run(Task(kind="repl", config=self.config, flags=flags))

        elif command == "lsp":
            return self._lsp.run(Task(kind="lsp", config=self.config, flags=flags))

        else:
            return TaskResult(
                ok=False, exit_code=1,
                ai_analysis=f"Unknown command: '{command}'",
            )

    # ------------------------------------------------------------------
    # Pipelines
    # ------------------------------------------------------------------

    def _pipeline_run(self, source: str, filename: str, flags: dict) -> TaskResult:
        """Lex → Parse → Interpret."""
        lex_r = self._lex(source, filename)
        if not lex_r.ok:
            return self._with_analysis(lex_r, source, filename)

        parse_r = self._parse(lex_r.payload, filename)
        if not parse_r.ok:
            return self._with_analysis(parse_r, source, filename)

        interp_r = self._interp.run(Task(
            kind="interpret",
            source=source,
            filename=filename,
            scope_tree=parse_r.payload,
            config=self.config,
            flags=flags,
        ))
        if not interp_r.ok:
            return self._with_analysis(interp_r, source, filename)

        return interp_r

    def _pipeline_check(self, source: str, filename: str, flags: dict) -> TaskResult:
        """Lex → Parse → Type-check."""
        lex_r = self._lex(source, filename)
        if not lex_r.ok:
            return self._with_analysis(lex_r, source, filename)

        parse_r = self._parse(lex_r.payload, filename)
        if not parse_r.ok:
            return self._with_analysis(parse_r, source, filename)

        type_r = self._type.run(Task(
            kind="typecheck",
            source=source,
            filename=filename,
            scope_tree=parse_r.payload,
            config=self.config,
            flags=flags,
        ))

        # Request analysis for errors; warnings get analysis too when present
        if not type_r.ok or type_r.warnings:
            return self._with_analysis(type_r, source, filename)

        return type_r

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _lex(self, source: str, filename: str) -> TaskResult:
        return self._lexer.run(
            Task(kind="lex", source=source, filename=filename, config=self.config)
        )

    def _parse(self, tokens: list, filename: str) -> TaskResult:
        return self._parser.run(
            Task(kind="parse", tokens=tokens, filename=filename, config=self.config)
        )

    def _with_analysis(
        self, result: TaskResult, source: str, filename: str
    ) -> TaskResult:
        """
        Attach a Claude-generated AI analysis to the result.
        Silently skips if ANTHROPIC_API_KEY is not set or the call fails.
        """
        all_diags = result.errors + result.warnings
        if not all_diags:
            return result

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return result

        try:
            result.ai_analysis = self._call_claude(source, filename, all_diags, api_key)
        except Exception:
            pass  # never let Claude failure break the compiler pipeline

        return result

    def _call_claude(
        self, source: str, filename: str, diagnostics: list, api_key: str
    ) -> str:
        """
        Call Claude Opus 4.6 (streaming) to analyse compiler diagnostics.
        Returns the full analysis text.
        """
        import anthropic

        diag_text   = "\n".join(d.format() for d in diagnostics)
        user_prompt = (
            f"File: {filename}\n\n"
            f"Source code:\n```\n{source}\n```\n\n"
            f"Compiler diagnostics:\n```\n{diag_text}\n```\n\n"
            "Please analyse these diagnostics and explain how to fix them."
        )

        client   = anthropic.Anthropic(api_key=api_key)
        analysis = ""

        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=1024,
            system=_ANALYSIS_SYSTEM,
            messages=[{"role": "user", "content": user_prompt}],
        ) as stream:
            for text in stream.text_stream:
                analysis += text

        return analysis
