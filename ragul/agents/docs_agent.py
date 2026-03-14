"""
ragul/agents/docs_agent.py — Claude-powered agent for generating Ragul documentation examples.

Given a topic (e.g. "arithmetic pipeline", "error handling", "for-each loop"),
asks Claude to write a correct, idiomatic Ragul example program.

The full Ragul spec is sent as prompt-cached context, so repeat calls only pay
for the incremental prompt + response tokens.

Task.flags:
    "topic"   (str, required) — the feature to illustrate
    "section" (str, optional) — spec section hint, e.g. "§2.3"

TaskResult.payload — str: the generated .ragul source code
"""

from __future__ import annotations
import os
from pathlib import Path

from ragul.agents.base import BaseAgent
from ragul.agents.task import Task, TaskResult

_SPEC_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "Project Documents"
    / "ragul-spec.md"
)

_SYSTEM = """\
You are an expert Ragul programmer. Ragul is an experimental programming language \
whose core logic is modelled on agglutinative grammar — specifically the structural \
principles of Hungarian. Meaning is built by stacking suffixes onto a root; a \
suffix chain is a pipeline.

You will be given the full Ragul language specification. Your job is to write \
short, correct, idiomatic Ragul example programs that illustrate specific language \
features. Always:

- Include a one-line comment at the top (// ...) describing what the example demonstrates
- Use only features defined in the specification
- Keep examples concise (10–30 lines maximum)
- Follow exact syntax rules: suffix chains, full-stop sentence terminators,
  tab-based indentation for scopes, -nk-hatás for top-level effect scopes
- Return only the raw Ragul source code — no markdown fences, no prose
"""


class DocsAgent(BaseAgent):
    """
    Generates a Ragul example program for a given topic using Claude Opus 4.6.

    Uses adaptive thinking and prompt caching so the spec (74 KB) is only
    billed once per cache TTL (5 minutes by default).
    """

    def run(self, task: Task) -> TaskResult:
        import anthropic

        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            return TaskResult(
                ok=False,
                exit_code=1,
                ai_analysis=(
                    "ANTHROPIC_API_KEY is not set. "
                    "DocsAgent requires access to the Claude API."
                ),
            )

        topic   = task.flags.get("topic", "hello world")
        section = task.flags.get("section", "")

        # Load spec for cached context
        try:
            spec_text = _SPEC_PATH.read_text(encoding="utf-8")
        except FileNotFoundError:
            spec_text = "(Ragul spec not found — writing from general knowledge)"

        prompt = f"Write a Ragul example program demonstrating: **{topic}**"
        if section:
            prompt += f"  (spec {section})"
        prompt += "\n\nReturn only the raw Ragul source code."

        client    = anthropic.Anthropic(api_key=api_key)
        generated = ""

        with client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=2048,
            thinking={"type": "adaptive"},
            system=[
                {"type": "text", "text": _SYSTEM},
                {
                    "type": "text",
                    "text": f"# Ragul Language Specification\n\n{spec_text}",
                    "cache_control": {"type": "ephemeral"},
                },
            ],
            messages=[{"role": "user", "content": prompt}],
        ) as stream:
            for text in stream.text_stream:
                generated += text

        # Strip any accidental markdown fences
        lines = generated.splitlines()
        lines = [ln for ln in lines if not ln.startswith("```")]
        generated = "\n".join(lines).strip()

        return TaskResult(ok=True, payload=generated, exit_code=0)
