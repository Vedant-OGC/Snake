"""Snake language CLI — argument parsing and subcommand dispatch."""

import argparse
import sys
import os

from snake.lexer import tokenize
from snake.parser import Parser
from snake.interpreter import Interpreter
from snake.transpiler import Transpiler
from snake.repl import start_repl
from snake.errors import SnakeError, format_error
from snake.utils import read_source


def main() -> None:
    """Entry point for the Snake CLI."""
    parser = argparse.ArgumentParser(prog="snake", description="The Snake programming language")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # snake bite
    run_parser = subparsers.add_parser("bite", help="Run a .snk file")
    run_parser.add_argument("file", help="Path to the .snk source file")
    run_parser.add_argument("--debug", action="store_true", help="Print AST before running")

    # snake compile
    compile_parser = subparsers.add_parser("compile", help="Transpile a .snk file to Python")
    compile_parser.add_argument("file", help="Path to the .snk source file")
    compile_parser.add_argument("-o", "--output", help="Output .py file path")

    # snake repl
    subparsers.add_parser("repl", help="Launch interactive REPL")

    args = parser.parse_args()

    if args.command == "bite":
        _cmd_run(args)
    elif args.command == "compile":
        _cmd_compile(args)
    elif args.command == "repl":
        start_repl()


def _cmd_run(args) -> None:
    """Execute a Snake source file."""
    _warn_extension(args.file)
    try:
        source, source_lines = read_source(args.file)
        tokens = tokenize(source)
        ast_nodes = Parser(tokens).parse()

        if args.debug:
            print("── AST ──")
            for node in ast_nodes:
                print(f"  {node}")
            print("── Output ──")

        Interpreter().run(ast_nodes, source_lines)
    except SnakeError as e:
        print(format_error(e, []), file=sys.stderr)
        sys.exit(1)


def _cmd_compile(args) -> None:
    """Transpile a Snake source file to Python."""
    _warn_extension(args.file)
    try:
        source, source_lines = read_source(args.file)
        tokens = tokenize(source)
        ast_nodes = Parser(tokens).parse()
        py_code = Transpiler().transpile(ast_nodes)

        output_path = args.output or os.path.splitext(args.file)[0] + ".py"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(py_code)
        print(f"Compiled: {output_path}")
    except SnakeError as e:
        print(format_error(e, []), file=sys.stderr)
        sys.exit(1)


def _warn_extension(filepath: str) -> None:
    """Print a warning if the file doesn't have a .snk extension."""
    if not filepath.endswith(".snk"):
        print(f"Warning: '{filepath}' does not have a .snk extension.", file=sys.stderr)
