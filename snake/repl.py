"""Snake language REPL — interactive shell for live coding."""

from snake.lexer import tokenize
from snake.parser import Parser
from snake.interpreter import Interpreter
from snake.errors import SnakeError, format_error


def start_repl() -> None:
    """Launch an interactive Snake REPL.

    Maintains interpreter state across inputs. Supports multi-line blocks
    when a line ends with ':'. Type 'exit'/'quit' to leave, 'clear' to reset.
    """
    interp = Interpreter()
    print("Snake REPL v1.0 — Type 'exit' to quit, 'clear' to reset.")

    while True:
        try:
            line = input(">>> ")
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        stripped = line.strip()
        if stripped in ("exit", "quit"):
            print("Bye!")
            break
        if stripped == "clear":
            interp.env.clear()
            interp.functions.clear()
            print("Environment cleared.")
            continue
        if stripped == "":
            continue

        # Multi-line block collection
        source = line
        if stripped.endswith(":"):
            source = _collect_block(line)
            if source is None:
                continue

        _execute_source(source, interp)


def _collect_block(first_line: str) -> str | None:
    """Collect continuation lines for a multi-line block.

    Returns the complete source string, or None if interrupted.
    """
    lines = [first_line]
    while True:
        try:
            cont = input("... ")
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if cont.strip() == "":
            break
        lines.append(cont)
    return "\n".join(lines)


def _execute_source(source: str, interp: Interpreter) -> None:
    """Lex, parse, and execute a source string, catching all errors."""
    source_lines = source.splitlines()
    try:
        tokens = tokenize(source)
        ast_nodes = Parser(tokens).parse()
        interp.run(ast_nodes, source_lines)
    except SnakeError as e:
        print(format_error(e, source_lines))
