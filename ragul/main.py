"""
cli/main.py — Ragul command-line interface.

Commands:
    ragul futtat   <file>    Run a Ragul program
    ragul ellenőriz <file>   Type-check without running
    ragul fordít   <file>    Compile to bytecode (stub for v1)
    ragul repl               Start the interactive REPL

Hungarian commands are primary; English aliases (run, check, compile) accepted.
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path


def _run(source_path: Path, strict: bool = False) -> int:
    """Lex → parse → interpret (via OrchestratorAgent)."""
    from ragul.agents.orchestrator import OrchestratorAgent
    from ragul.config import RagulConfig
    from rich.console import Console

    console  = Console()
    source   = source_path.read_text(encoding="utf-8")
    filename = str(source_path)
    cfg      = RagulConfig.load()

    orch   = OrchestratorAgent(config=cfg)
    result = orch.run("futtat", source=source, filename=filename,
                      flags={"strict": strict})

    for d in result.errors:
        console.print(f"[bold red]{d.format()}[/bold red]", file=sys.stderr)
    for d in result.warnings:
        console.print(f"[yellow]{d.format()}[/yellow]", file=sys.stderr)

    if result.ai_analysis:
        console.print("\n[cyan]── AI Analysis ──────────────────────────────────────[/cyan]")
        console.print(result.ai_analysis)
        console.print("[cyan]─────────────────────────────────────────────────────[/cyan]\n")

    return result.exit_code


def _check(source_path: Path, strict: bool = False) -> int:
    """Lex → parse → type-check (via OrchestratorAgent)."""
    from ragul.agents.orchestrator import OrchestratorAgent
    from ragul.config import RagulConfig
    from rich.console import Console

    console  = Console()
    source   = source_path.read_text(encoding="utf-8")
    filename = str(source_path)
    cfg      = RagulConfig.load()

    orch   = OrchestratorAgent(config=cfg)
    result = orch.run("ellenőriz", source=source, filename=filename,
                      flags={"strict": strict})

    for d in result.errors:
        console.print(f"[bold red]{d.format()}[/bold red]")
    for d in result.warnings:
        console.print(f"[yellow]{d.format()}[/yellow]")

    if result.ai_analysis:
        console.print("\n[cyan]── AI Analysis ──────────────────────────────────────[/cyan]")
        console.print(result.ai_analysis)
        console.print("[cyan]─────────────────────────────────────────────────────[/cyan]\n")

    if result.ok and not result.errors:
        console.print(f"[bold green]✓ {filename}  —  no errors found[/bold green]")

    return result.exit_code


def _repl() -> int:
    """Start the interactive REPL."""
    try:
        from ragul.repl.repl import run_repl
        return run_repl()
    except ImportError:
        print("REPL module not yet available.", file=sys.stderr)
        return 1


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ragul",
        description="Ragul — the agglutinative programming language",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    # futtat / run
    run_p = sub.add_parser("futtat",   aliases=["run"],     help="Run a Ragul program")
    run_p.add_argument("file", type=Path, help="Source file (.ragul)")
    run_p.add_argument("--strict", action="store_true", help="Treat warnings as errors")

    # ellenőriz / check
    chk_p = sub.add_parser("ellenőriz", aliases=["check"],  help="Type-check without running")
    chk_p.add_argument("file", type=Path)
    chk_p.add_argument("--strict", action="store_true")

    # fordít / compile
    cmp_p = sub.add_parser("fordít",   aliases=["compile"], help="Compile to bytecode (v1: stub)")
    cmp_p.add_argument("file", type=Path)

    # repl
    sub.add_parser("repl", help="Start the interactive REPL")

    # lsp
    sub.add_parser("lsp", help="Start the Language Server (stdio mode)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    cmd = args.command

    if cmd in ("futtat", "run"):
        sys.exit(_run(args.file, getattr(args, "strict", False)))

    elif cmd in ("ellenőriz", "check"):
        sys.exit(_check(args.file, getattr(args, "strict", False)))

    elif cmd in ("fordít", "compile"):
        print("Bytecode compilation is not yet implemented in v1.", file=sys.stderr)
        print("Use 'ragul futtat' to run programs via the interpreter.")
        sys.exit(0)

    elif cmd == "repl":
        sys.exit(_repl())

    elif cmd == "lsp":
        try:
            from ragul.lsp.server import run_lsp_server
            run_lsp_server()
            sys.exit(0)
        except ImportError as e:
            print(f"LSP server unavailable: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
