"""
cli/main.py — Ragul command-line interface.

Commands:
    ragul futtat   <file>    Run a Ragul program
    ragul ellenőriz <file>   Type-check without running
    ragul fordít   <file>    Compile to bytecode (stub for v1)
    ragul repl               Start the interactive REPL
    ragul új projekt <name>  Scaffold a new project folder
    ragul új modul   <name>  Scaffold a new module file

Hungarian commands are primary; English aliases (run, check, compile, new, project, module) accepted.
"""

from __future__ import annotations
import sys
import argparse
from pathlib import Path
from rich.markup import escape as _markup_escape

# Ensure stdout/stderr can handle Unicode (needed on Windows with legacy cp1252 console).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def _run(source_path: Path, strict: bool = False) -> int:
    """Lex → parse → interpret (via OrchestratorAgent)."""
    from ragul.agents.orchestrator import OrchestratorAgent
    from ragul.config import RagulConfig
    from rich.console import Console

    console  = Console(legacy_windows=False)
    source   = source_path.read_text(encoding="utf-8")
    filename = str(source_path)
    cfg      = RagulConfig.load()

    orch   = OrchestratorAgent(config=cfg)
    result = orch.run("futtat", source=source, filename=filename,
                      flags={"strict": strict})

    for d in result.errors:
        console.print(f"[bold red]{_markup_escape(d.format())}[/bold red]")
    for d in result.warnings:
        console.print(f"[yellow]{_markup_escape(d.format())}[/yellow]")

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

    console  = Console(legacy_windows=False)
    source   = source_path.read_text(encoding="utf-8")
    filename = str(source_path)
    cfg      = RagulConfig.load()

    orch   = OrchestratorAgent(config=cfg)
    result = orch.run("ellenőriz", source=source, filename=filename,
                      flags={"strict": strict})

    for d in result.errors:
        console.print(f"[bold red]{_markup_escape(d.format())}[/bold red]")
    for d in result.warnings:
        console.print(f"[yellow]{_markup_escape(d.format())}[/yellow]")

    if result.ai_analysis:
        console.print("\n[cyan]── AI Analysis ──────────────────────────────────────[/cyan]")
        console.print(result.ai_analysis)
        console.print("[cyan]─────────────────────────────────────────────────────[/cyan]\n")

    if result.ok and not result.errors:
        console.print(f"[bold green]✓ {filename}  —  no errors found[/bold green]")

    return result.exit_code


def _new_project(name: str) -> int:
    """Scaffold a new Ragul project folder."""
    from rich.console import Console
    console = Console(legacy_windows=False)

    target = Path.cwd() / name
    if target.exists():
        console.print(f"[bold red]Error:[/bold red] '{name}' already exists.")
        return 1

    target.mkdir(parents=True)

    # ragul.config
    (target / "ragul.config").write_text(
        f'[projekt]\n'
        f'nev     = "{name}"\n'
        f'verzio  = "0.1.0"\n'
        f'belepes = "main.ragul"\n'
        f'\n'
        f'[fordito]\n'
        f'cel    = "interpret"\n'
        f'python = "3.11"\n'
        f'\n'
        f'[modulok]\n'
        f'utvonalak = []\n'
        f'\n'
        f'[ellenorzes]\n'
        f'harmonia = "warn"\n'
        f'tipus    = "warn"\n'
        f'\n'
        f'[hibak]\n'
        f'nyelv = "en"\n',
        encoding="utf-8",
    )

    # main.ragul
    (target / "main.ragul").write_text(
        f'// main.ragul — {name}\n'
        f'\n'
        f'program-nk-hatás\n'
        f'\tüdvözlet-ba  "Helló, {name}!"-t.\n'
        f'\tüdvözlet-képernyőre-va.\n',
        encoding="utf-8",
    )

    # .gitignore
    (target / ".gitignore").write_text(
        "__pycache__/\n"
        "*.py[cod]\n"
        ".ragul_cache/\n"
        "dist/\n"
        "*.egg-info/\n",
        encoding="utf-8",
    )

    # README.md
    (target / "README.md").write_text(
        f"# {name}\n"
        f"\n"
        f"A [Ragul](https://github.com/korykilpatrick/ragul) project.\n"
        f"\n"
        f"## Run\n"
        f"\n"
        f"```sh\n"
        f"cd {name}\n"
        f"ragul futtat main.ragul\n"
        f"```\n",
        encoding="utf-8",
    )

    console.print(f"[bold green]OK[/bold green] Created project [bold]{name}/[/bold]")
    console.print(f"  [dim]ragul.config[/dim]")
    console.print(f"  [dim]main.ragul[/dim]")
    console.print(f"  [dim].gitignore[/dim]")
    console.print(f"  [dim]README.md[/dim]")
    console.print(f"\n  Run with: [bold]cd {name} && ragul futtat main.ragul[/bold]")
    return 0


def _new_module(name: str) -> int:
    """Scaffold a new Ragul module file in the current project."""
    from rich.console import Console
    console = Console(legacy_windows=False)

    # Strip .ragul extension if the user typed it
    if name.endswith(".ragul"):
        name = name[:-6]

    target = Path.cwd() / f"{name}.ragul"
    if target.exists():
        console.print(f"[bold red]Error:[/bold red] '{name}.ragul' already exists.")
        return 1

    target.write_text(
        f"// {name}.ragul — {name} module\n"
        f"\n"
        f"{name}-nk-hatás\n"
        f"\t// Add your code here.\n",
        encoding="utf-8",
    )

    console.print(f"[bold green]OK[/bold green] Created module [bold]{name}.ragul[/bold]")
    return 0


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

    # új / new
    new_p = sub.add_parser("új", aliases=["new"], help="Scaffold a new project or module")
    new_sub = new_p.add_subparsers(dest="new_command", metavar="WHAT")

    proj_p = new_sub.add_parser("projekt", aliases=["project"], help="Scaffold a new project folder")
    proj_p.add_argument("name", help="Project name")

    mod_p = new_sub.add_parser("modul", aliases=["module"], help="Scaffold a new module file")
    mod_p.add_argument("name", help="Module name")

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

    elif cmd in ("új", "new"):
        what = getattr(args, "new_command", None)
        if what in ("projekt", "project"):
            sys.exit(_new_project(args.name))
        elif what in ("modul", "module"):
            sys.exit(_new_module(args.name))
        else:
            new_p.print_help()
            sys.exit(1)

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
