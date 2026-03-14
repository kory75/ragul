"""
ragul/repl/repl.py — Interactive REPL for the Ragul language.

Maintains a persistent root environment across sentences.
Multi-line scope definitions work via continuation (prompts '...' until '.').
"""

from __future__ import annotations
import sys

PROMPT     = ">>> "
PROMPT_CON = "... "

COMMANDS = {
    ":kilep":  "exit",
    ":exit":   "exit",
    ":töröl":  "clear",
    ":clear":  "clear",
    ":mutat":  "show",
    ":show":   "show",
    ":help":   "help",
    ":súgó":   "help",
}

HELP_TEXT = """
Ragul REPL — interactive session

  Type Ragul sentences (end with '.' to execute).
  Multi-line scopes are supported — keep typing until you close with '.'.

  Special commands:
    :kilep  / :exit   — quit
    :töröl  / :clear  — reset all bindings
    :mutat  / :show   — print all bound roots and their values
    :help   / :súgó   — this message
"""


def run_repl() -> int:
    """Entry point for the REPL.  Returns exit code."""
    from ragul.lexer import lex
    from ragul.parser import parse
    from ragul.interpreter import Interpreter, RagulRuntimeError, PropagateError
    from ragul.model import Scope

    # Persistent interpreter state
    root_scope  = Scope(name="__repl__")
    interpreter = Interpreter(root_scope, filename="<repl>")

    print("Ragul REPL  (type :help for commands, :kilep to quit)")
    print()

    buffer = ""
    depth  = 0   # track open scope depth for continuation

    while True:
        prompt = PROMPT_CON if buffer.strip() else PROMPT
        try:
            try:
                line = input(prompt)
            except EOFError:
                print()
                break

            # Special commands (only when not mid-continuation)
            if not buffer.strip() and line.strip() in COMMANDS:
                action = COMMANDS[line.strip()]
                if action == "exit":
                    break
                elif action == "clear":
                    interpreter.global_env._frames = [{}]
                    interpreter._user_scopes.clear()
                    print("  — bindings cleared —")
                elif action == "show":
                    bindings = interpreter.global_env.all_bindings()
                    if not bindings:
                        print("  (no bindings)")
                    else:
                        for name, val in sorted(bindings.items()):
                            print(f"  {name} = {val!r}")
                elif action == "help":
                    print(HELP_TEXT)
                continue

            buffer += line + "\n"

            # Count indent depth to detect continuation
            for ch in line:
                if ch == '\t':
                    depth += 1
            # Dedent detection
            stripped = line.strip()
            if not stripped and depth > 0:
                depth = 0

            # Only execute if the buffer contains a complete sentence ('.')
            # or we're not inside an open scope
            if '.' not in buffer and depth == 0 and stripped:
                continue

            if not buffer.strip():
                buffer = ""
                continue

            # Try to execute
            source = buffer.strip()
            buffer = ""
            depth  = 0

            tokens, lex_bag = lex(source, "<repl>")
            if lex_bag.has_errors:
                print(lex_bag.format_all())
                continue

            tree, parse_bag = parse(tokens, "<repl>")
            if parse_bag.has_errors:
                print(parse_bag.format_all())
                continue

            # Merge new scopes into interpreter's user scope registry
            for child in tree.children:
                interpreter._user_scopes[child.name] = child
                interpreter._collect_scopes(child)

            # Execute sentences in the root of the parsed tree
            last_val = None
            for sentence in tree.sentences:
                try:
                    last_val = interpreter.eval_sentence(sentence)
                except PropagateError as e:
                    print(f"Error: {e.hiba.message}")
                    last_val = None
                except RagulRuntimeError as e:
                    print(f"Runtime error: {e.ragul_message}")
                    last_val = None

            # Print result if there was one and it's not None
            if last_val is not None:
                print(repr(last_val))

        except KeyboardInterrupt:
            buffer = ""
            depth  = 0
            print("\n(interrupt — buffer cleared)")

    return 0
