"""Shared helper utilities for the Snake language."""

from snake.errors import SnakeError, SnakeIndentationError

INDENT_SIZE = 4


def read_source(filepath: str) -> tuple[str, list[str]]:
    """Read a Snake source file and return (full_source, lines_list).

    Raises:
        SnakeError: If the file cannot be found or read.
    """
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            source = f.read()
        return source, source.splitlines()
    except FileNotFoundError:
        raise SnakeError(f"File not found: '{filepath}'")
    except OSError as e:
        raise SnakeError(f"Cannot read file '{filepath}': {e}")


def get_indent_level(line: str) -> int:
    """Count leading spaces and return indent level (multiples of INDENT_SIZE).

    Raises:
        SnakeIndentationError: If tabs are found or spaces aren't a multiple of INDENT_SIZE.
    """
    if "\t" in line[:len(line) - len(line.lstrip())]:
        raise SnakeIndentationError(
            "Tabs are not allowed. Use 4 spaces for indentation.", source_line=line
        )

    spaces = len(line) - len(line.lstrip(" "))
    if spaces % INDENT_SIZE != 0:
        raise SnakeIndentationError(
            f"Indentation must be a multiple of {INDENT_SIZE} spaces, got {spaces}.",
            source_line=line,
        )
    return spaces // INDENT_SIZE


def is_numeric(value: str) -> bool:
    """Return True if string can be parsed as int or float."""
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


def snake_type_name(value) -> str:
    """Return 'number', 'text', or 'unknown' for a Python value."""
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, str):
        return "text"
    return "unknown"
