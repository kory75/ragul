"""
ragul/interpreter.py — Tree-walking interpreter for Ragul.

MVP strategy: eager evaluation within pure scopes; -hatás scopes are
sequential and unconditional. Full lazy evaluation is a future extension.

The interpreter maintains an Environment (stack of dicts mapping root names
to Python values), evaluates each sentence in dependency order, and applies
suffix chains by looking up functions in the stdlib registry.
"""

from __future__ import annotations
import sys
from typing import Any, Callable
from ragul.model import Word, Sentence, Scope
from ragul.stdlib.core import SUFFIX_REGISTRY
from ragul.stdlib.modules import RagulHiba  # runtime error value
from ragul.errors import DiagnosticBag


# ---------------------------------------------------------------------------
# Runtime error types
# ---------------------------------------------------------------------------

class RagulRuntimeError(Exception):
    """A fatal runtime error (exit code 2)."""
    def __init__(self, message: str, line: int = 0) -> None:
        super().__init__(message)
        self.ragul_message = message
        self.line = line


class PropagateError(Exception):
    """An error value being propagated via -va-e."""
    def __init__(self, hiba: RagulHiba) -> None:
        self.hiba = hiba


class _BreakSignal(Exception):
    """Signal raised by -megszakít (break) inside a loop."""
    pass


# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

class Environment:
    """Lexical scope stack."""

    def __init__(self, parent: "Environment | None" = None) -> None:
        self._frames: list[dict[str, Any]] = [{}]
        self.parent = parent

    def set(self, name: str, value: Any) -> None:
        self._frames[-1][name] = value

    def get(self, name: str) -> Any:
        # Search from innermost frame outward
        for frame in reversed(self._frames):
            if name in frame:
                return frame[name]
        if self.parent:
            return self.parent.get(name)
        raise RagulRuntimeError(f"Undefined root: '{name}'")

    def has(self, name: str) -> bool:
        try:
            self.get(name)
            return True
        except RagulRuntimeError:
            return False

    def push(self) -> None:
        self._frames.append({})

    def pop(self) -> None:
        if len(self._frames) > 1:
            self._frames.pop()

    def all_bindings(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        if self.parent:
            result.update(self.parent.all_bindings())
        for frame in self._frames:
            result.update(frame)
        return result


# ---------------------------------------------------------------------------
# I/O channel implementations
# ---------------------------------------------------------------------------

def _channel_képernyőre(value: Any) -> None:
    print(value, end="\n")

def _channel_stderr(value: Any) -> None:
    print(value, file=sys.stderr)

def _channel_bemenetről() -> str:
    return input()

EFFECT_CHANNELS: dict[str, Callable[..., Any]] = {
    "képernyőre": _channel_képernyőre,
    "stderr":     _channel_stderr,
    "bemenetről": _channel_bemenetről,
}


# ---------------------------------------------------------------------------
# Interpreter
# ---------------------------------------------------------------------------

class Interpreter:
    """
    Walks a Scope tree and executes it.
    """

    def __init__(self, root_scope: Scope, filename: str = "<string>") -> None:
        self.root_scope = root_scope
        self.filename   = filename
        self.bag        = DiagnosticBag(filename)
        self.global_env = Environment()
        # Register user-defined scopes (functions/suffixes) by name
        self._user_scopes: dict[str, Scope] = {}
        self._collect_scopes(root_scope)

    def _collect_scopes(self, scope: Scope) -> None:
        """Walk the tree and register callable scopes (functions/modules).
        
        Loop and conditional scopes are NOT callable suffixes — they are
        control flow constructs that execute inline. Registering them as
        user_scopes would shadow same-named variables (e.g. i-míg shadowing i).
        """
        for child in scope.children:
            # Only register as callable if it's a named function/module scope
            # — i.e. NOT a loop, conditional, or anonymous block
            is_callable = (
                child.name
                and child.name != "__root__"
                and not child.is_loop
                and not child.is_conditional
            )
            if is_callable:
                self._user_scopes[child.name] = child
            self._collect_scopes(child)

    # ------------------------------------------------------------------
    # Public entry
    # ------------------------------------------------------------------

    def run(self) -> int:
        """Execute the program.  Returns exit code (0, 2, or 3)."""
        try:
            # Execute root-level sentences first
            self._exec_scope(self.root_scope, self.global_env)
            # Then execute all top-level executable scopes in order:
            # effect scopes, conditionals, and loops
            for child in self.root_scope.children:
                if child.is_effect or child.is_conditional or child.is_loop:
                    self._exec_scope(child, self.global_env)
            return 0
        except PropagateError as e:
            print(f"Unhandled error: {e.hiba.message}", file=sys.stderr)
            return 3
        except RagulRuntimeError as e:
            print(f"Runtime error: {e.ragul_message}", file=sys.stderr)
            return 2
        except Exception as e:
            print(f"Internal error: {e}", file=sys.stderr)
            return 2

    # ------------------------------------------------------------------
    # Scope execution
    # ------------------------------------------------------------------

    # Maximum loop iterations — safety guard
    MAX_ITERATIONS = 100_000

    def _exec_scope(self, scope: Scope, env: Environment,
                    args: dict[str, Any] | None = None) -> Any:
        """Execute all sentences in a scope and return the last value."""
        is_named = scope.name not in ("__root__", "__repl__")
        if is_named or args:
            local_env = Environment(parent=env)
        else:
            local_env = env

        if args:
            for name, val in args.items():
                local_env.set(name, val)

        last_value: Any = None

        # --- Conditional scope: -ha ---
        # Conditionals share the outer scope — bindings leak to parent (like Python if)
        if scope.is_conditional:
            last_value = self._exec_conditional(scope, env)
            return last_value

        # --- Loop scope: -míg / -ig / -mindegyik / -gyűjt ---
        # Loops also share the outer scope for variable mutation
        if scope.is_loop:
            last_value = self._exec_loop(scope, env)
            return last_value

        # --- Effect scope: -hatás ---
        if scope.is_effect:
            try:
                for sentence in scope.sentences:
                    last_value = self._exec_sentence(sentence, local_env, scope)
                for child in scope.children:
                    if child.is_effect or child.is_conditional or child.is_loop:
                        last_value = self._exec_scope(child, local_env)
            except PropagateError as e:
                if scope.error_handler:
                    handler_env = Environment(parent=local_env)
                    handler_env.set("hiba", e.hiba)
                    self._exec_scope(scope.error_handler, handler_env)
                    last_value = None
                else:
                    raise
            return last_value

        # --- Pure / function scope ---
        try:
            for sentence in scope.sentences:
                last_value = self._exec_sentence(sentence, local_env, scope)
            # Execute child conditional/loop scopes (they run inline)
            for child in scope.children:
                if child.is_conditional or child.is_loop:
                    last_value = self._exec_scope(child, local_env)
        except PropagateError as e:
            if scope.error_handler:
                handler_env = Environment(parent=local_env)
                handler_env.set("hiba", e.hiba)
                self._exec_scope(scope.error_handler, handler_env)
                last_value = None
            else:
                raise
        return last_value

    # ------------------------------------------------------------------
    # Conditional execution
    # ------------------------------------------------------------------

    def _exec_conditional(self, scope: Scope, env: Environment) -> Any:
        """
        Execute a -ha scope.
        Convention: the FIRST sentence is the condition expression.
        Remaining sentences are the body (executed when condition is truthy).
        The -hanem sibling (scope.else_branch) runs when condition is falsy.
        -különben branches are chained as elif_branches.
        """
        if not scope.sentences:
            return None

        # Evaluate condition (first sentence — the expression that returns Logikai)
        condition_sentence = scope.sentences[0]
        condition_value = self._eval_condition_sentence(condition_sentence, env)

        if condition_value:
            # Run the body (sentences 1..n)
            last_value: Any = None
            for sentence in scope.sentences[1:]:
                last_value = self._exec_sentence(sentence, env, scope)
            # Run nested child scopes
            for child in scope.children:
                last_value = self._exec_scope(child, env)
            return last_value
        else:
            # Check elif branches
            for elif_branch in scope.elif_branches:
                result = self._exec_conditional(elif_branch, env)
                if result is not None:
                    return result
            # Run -hanem branch
            if scope.else_branch:
                return self._exec_scope(scope.else_branch, env)
        return None

    def _eval_condition_sentence(self, sentence, env: Environment) -> bool:
        """Evaluate a condition sentence and return a Python bool."""
        # The condition sentence typically has the form: x-3-felett-t
        # or just a boolean root like: igaz-t
        for word in sentence.words:
            if word.case in ("-t", "-ból", "-ből", ""):
                val = self._eval_word(word, env)
                if isinstance(val, bool):
                    return val
                if isinstance(val, (int, float)):
                    return bool(val)
                return val is not None and val is not False
        return False

    # ------------------------------------------------------------------
    # Loop execution
    # ------------------------------------------------------------------

    def _exec_loop(self, scope: Scope, env: Environment) -> Any:
        """Dispatch to the right loop type."""
        kind = scope.loop_kind
        if kind == "míg":
            return self._exec_while(scope, env)
        elif kind == "ig":
            return self._exec_until(scope, env)
        elif kind == "mindegyik":
            return self._exec_foreach(scope, env)
        elif kind == "gyűjt":
            return self._exec_fold(scope, env)
        return None

    def _exec_while(self, scope: Scope, env: Environment) -> Any:
        """
        -míg loop: execute body while condition is truthy.
        First sentence is the condition; remaining are body.
        """
        if not scope.sentences:
            return None
        condition_sentence = scope.sentences[0]
        body_sentences     = scope.sentences[1:]
        last_value: Any    = None
        iterations = 0

        while True:
            if not self._eval_condition_sentence(condition_sentence, env):
                break
            iterations += 1
            if iterations > self.MAX_ITERATIONS:
                raise RagulRuntimeError(
                    f"Loop exceeded {self.MAX_ITERATIONS} iterations (infinite loop guard)",
                    line=scope.sentences[0].line,
                )
            try:
                for sentence in body_sentences:
                    last_value = self._exec_sentence(sentence, env, scope)
                for child in scope.children:
                    last_value = self._exec_scope(child, env)
            except _BreakSignal:
                break
        return last_value

    def _exec_until(self, scope: Scope, env: Environment) -> Any:
        """-ig loop: execute body UNTIL condition is truthy."""
        if not scope.sentences:
            return None
        condition_sentence = scope.sentences[0]
        body_sentences     = scope.sentences[1:]
        last_value: Any    = None
        iterations = 0

        while True:
            iterations += 1
            if iterations > self.MAX_ITERATIONS:
                raise RagulRuntimeError(
                    f"Loop exceeded {self.MAX_ITERATIONS} iterations",
                    line=scope.sentences[0].line,
                )
            try:
                for sentence in body_sentences:
                    last_value = self._exec_sentence(sentence, env, scope)
                for child in scope.children:
                    last_value = self._exec_scope(child, env)
            except _BreakSignal:
                break
            if self._eval_condition_sentence(condition_sentence, env):
                break
        return last_value

    def _exec_foreach(self, scope: Scope, env: Environment) -> Any:
        """
        -mindegyik loop: iterate over a list.

        The scope name is the list variable to iterate over.
        The FIRST sentence declares the element parameter (word with possession -d
        or bare word naming the loop variable).
        Remaining sentences are the body executed for each element.
        """
        # Get the iterable
        iterable: list = []
        if env.has(scope.name):
            val = env.get(scope.name)
            if isinstance(val, list):
                iterable = val
            elif hasattr(val, "__iter__") and not isinstance(val, str):
                iterable = list(val)

        if not scope.sentences:
            return None

        # The first sentence is the parameter declaration (e.g. "szám-d.")
        # The body is sentences[1:]
        param_sentence = scope.sentences[0]
        body_sentences = scope.sentences[1:]

        # Extract the element variable name from the first sentence
        param_name: str = "elem"  # default
        for word in param_sentence.words:
            if word.possession == "-d" or (word.root and not word.case and not word.aspects):
                param_name = word.root
                break

        last_value: Any = None
        for element in iterable:
            loop_env = Environment(parent=env)
            loop_env.set(param_name, element)
            try:
                for sentence in body_sentences:
                    last_value = self._exec_sentence(sentence, loop_env, scope)
                for child in scope.children:
                    last_value = self._exec_scope(child, loop_env)
            except _BreakSignal:
                break
        # Write back any vars that were mutated through parent env
        # (foreach writes go to loop_env, not outer env — intentional)
        # But common pattern is to accumulate into outer scope var.
        # We handle this by making accumulator writes target the outer env.
        # The loop_env.parent IS the outer env, so set() on a known outer
        # key propagates via the parent chain automatically through get().
        # But set() on loop_env always writes to loop_env._frames[0].
        # Fix: for each var in loop_env that also exists in outer env,
        # propagate the final value back.
        for frame in loop_env._frames:
            for key, val in frame.items():
                if env.has(key):
                    env.set(key, val)

        return last_value

    def _exec_fold(self, scope: Scope, env: Environment) -> Any:
        """
        -gyűjt fold: reduce a list to a single value.
        The scope name is the list root.
        First -d parameter = accumulator, second = current element.
        Initial value of accumulator comes from the first -val argument.
        """
        iterable = env.get(scope.name) if env.has(scope.name) else []
        if not isinstance(iterable, list):
            iterable = []

        params = self._extract_params(scope)
        acc_name  = params[0] if len(params) > 0 else "felhalmozott"
        elem_name = params[1] if len(params) > 1 else "elem"

        # Initial accumulator: look for a numeric literal in scope sentences
        accumulator: Any = 0  # default
        for sentence in scope.sentences:
            for word in sentence.words:
                if word.root not in (acc_name, elem_name) and word.case == "":
                    try:
                        accumulator = int(word.root)
                        break
                    except (ValueError, TypeError):
                        pass

        for element in iterable:
            fold_env = Environment(parent=env)
            fold_env.set(acc_name,  accumulator)
            fold_env.set(elem_name, element)
            for sentence in scope.sentences:
                val = self._exec_sentence(sentence, fold_env, scope)
                if val is not None:
                    accumulator = val
        return accumulator

    def _extract_first_param(self, scope: Scope) -> str | None:
        """Return the first -d parameter root name in a scope."""
        params = self._extract_params(scope)
        return params[0] if params else None

    def _exec_sentence(self, sentence: Sentence, env: Environment,
                       current_scope: Scope) -> Any:
        """
        Execute a single sentence.

        Determines the target (word with -ba/-be case) and source (word with -t / -ból),
        evaluates the source, and binds to the target.
        """
        words = sentence.words

        if not words:
            return None

        # Find target word (-ba/-be case)
        target_word: Word | None = None
        source_word: Word | None = None
        action_word: Word | None = None
        val_words:   list[Word]  = []

        for w in words:
            if w.case in ("-ba", "-be"):
                target_word = w
            elif w.case == "-t":
                source_word = w
            elif w.action in ("-va", "-ve") and w.case not in ("-ba", "-be", "-t"):
                action_word = w
            elif w.case == "-val":
                val_words.append(w)
            elif w.case in ("-ból", "-ből"):
                source_word = w

        # Determine the primary operative word and evaluate it
        operative = source_word or action_word
        if not operative and len(words) == 1:
            operative = words[0]

        if operative is None:
            # All-val sentence or bare effect call
            if action_word:
                self._eval_word(action_word, env, val_words)
            return None

        value = self._eval_word(operative, env, val_words)

        # Bind to target
        if target_word:
            env.set(target_word.root, value)

        return value

    # ------------------------------------------------------------------
    # Word evaluation
    # ------------------------------------------------------------------

    def _eval_word(self, word: Word, env: Environment,
                   extra_val_args: list[Word] | None = None) -> Any:
        """
        Evaluate a word by:
        1. Looking up the root value
        2. Applying each aspect suffix left-to-right
        3. Executing the action if present
        4. Propagating error if -e and result is RagulHiba
        """
        # Resolve root value
        root_val = self._resolve_root(word, env)

        # Apply aspect suffixes
        # Inline args (numeric/string aspects like -3 in x-3-össze) are
        # queued and consumed by the NEXT real suffix.
        val_arg_queue = list(word.val_args) + (extra_val_args or [])
        val_arg_iter  = iter(val_arg_queue)

        value = root_val
        inline_args: list[Any] = []   # pending inline literal arguments

        for aspect in word.aspects:
            bare = aspect.lstrip("-")

            # --- Inline string literal (e.g. __str__:hello) ---
            if aspect.startswith("__str__:"):
                inline_args.append(aspect[len("__str__:"):])
                continue

            # --- Inline numeric literal (e.g. -3, -10, -3.14) ---
            is_num = False
            try:
                if "." in bare:
                    inline_args.append(float(bare))
                else:
                    inline_args.append(int(bare))
                is_num = True
            except (ValueError, TypeError):
                pass

            if is_num:
                continue  # consumed as inline arg for next real suffix

            # --- Inline variable reference (e.g. -b in a-b-össze) ---
            # A bare word that isn't a known suffix is a variable name.
            if aspect not in SUFFIX_REGISTRY and aspect not in self._user_scopes                     and aspect not in EFFECT_CHANNELS and bare:
                # Try to resolve as a variable lookup
                if env.has(bare):
                    inline_args.append(env.get(bare))
                    continue
                # Unknown — leave for suffix to handle (lenient)

            # --- Real suffix ---
            if aspect in SUFFIX_REGISTRY:
                entry  = SUFFIX_REGISTRY[aspect]
                fn     = entry["fn"]
                n_args = len(entry.get("arg_types", []))
                args: list[Any] = []
                # First drain any queued inline args
                while inline_args and len(args) < n_args:
                    args.append(inline_args.pop(0))
                # Then pull from -val word queue
                while len(args) < n_args:
                    try:
                        av = next(val_arg_iter)
                        args.append(self._eval_word(av, env))
                    except StopIteration:
                        break
                try:
                    value = fn(value, *args)
                except Exception as e:
                    value = RagulHiba(str(e))
            elif aspect in self._user_scopes:
                us = self._user_scopes[aspect]
                value = self._call_user_scope(us, value, val_arg_iter, env)
            elif aspect.lstrip("-") in EFFECT_CHANNELS:
                EFFECT_CHANNELS[aspect.lstrip("-")](value)
                value = None
            # Unknown aspect — pass through (lenient MVP)

        # Execute action (-va / -ve)
        if word.action in ("-va", "-ve"):
            if word.root in EFFECT_CHANNELS and not word.aspects:
                EFFECT_CHANNELS[word.root](value)
                value = None
            elif word.root == "megszakít":
                # -megszakít-va (break signal)
                raise _BreakSignal()
            elif word.root in self._user_scopes and not word.aspects:
                us = self._user_scopes[word.root]
                value = self._call_user_scope(us, value, iter([]), env)

        # Error propagation
        if word.error and isinstance(value, RagulHiba):
            raise PropagateError(value)

        return value

    def _resolve_root(self, word: Word, env: Environment) -> Any:
        """Resolve the root of a word to a Python value."""
        root = word.root

        # List literal
        if root == "__list__":
            return [self._eval_word(elem, env) for elem in word.val_args]

        # String literal
        if root.startswith('"') or root.startswith("'"):
            return root.strip('"').strip("'")

        # Number literal
        try:
            if '.' in root:
                return float(root)
            return int(root)
        except (ValueError, TypeError):
            pass

        # Boolean literals
        if root == "igaz":   return True
        if root == "hamis":  return False

        # Effect channel direct call (e.g. képernyőre-va)
        if root in EFFECT_CHANNELS:
            return root  # deferred to action handling

        # Variable lookup — BEFORE user scope check, so loop variables
        # named the same as their scope (e.g. i-míg) resolve to the variable.
        if env.has(root):
            return env.get(root)

        # Named scope reference (suffix call without value piping)
        if root in self._user_scopes:
            return root  # deferred

        # Unresolved — return as string (lenient MVP)
        return root

    def _call_user_scope(self, scope: Scope, root_val: Any,
                         val_iter, env: Environment) -> Any:
        """Call a user-defined scope as a suffix, binding -d parameters."""
        # Collect parameter names from scope's sentences
        params = self._extract_params(scope)

        args: dict[str, Any] = {}
        if params:
            args[params[0]] = root_val
            for param in params[1:]:
                try:
                    av = next(val_iter)
                    args[param] = self._eval_word(av, env)
                except StopIteration:
                    break

        return self._exec_scope(scope, env, args)

    def _extract_params(self, scope: Scope) -> list[str]:
        """Extract -d parameter root names from a scope's sentences."""
        params = []
        for sentence in scope.sentences:
            for word in sentence.words:
                if word.possession == "-d" and word.root not in params:
                    params.append(word.root)
        return params

    # ------------------------------------------------------------------
    # REPL helper
    # ------------------------------------------------------------------

    def eval_sentence(self, sentence: Sentence) -> Any:
        """Evaluate a single sentence in the global environment (for REPL)."""
        try:
            return self._exec_sentence(sentence, self.global_env, self.root_scope)
        except PropagateError as e:
            return e.hiba
        except RagulRuntimeError as e:
            print(f"Error: {e.ragul_message}", file=sys.stderr)
            return None
