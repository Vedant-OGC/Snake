"""Snake language error classes and pretty error formatter."""


class SnakeError(Exception):
    """Base class for all Snake language errors."""

    def __init__(self, message: str, line: int = 0, source_line: str = ""):
        self.message = message
        self.line = line
        self.source_line = source_line
        super().__init__(message)


class SnakeSyntaxError(SnakeError):
    """Raised on invalid syntax in Snake source code."""


class SnakeNameError(SnakeError):
    """Raised when a variable or function name is not defined."""


class SnakeTypeError(SnakeError):
    """Raised on type mismatches in expressions."""


class SnakeIndentationError(SnakeError):
    """Raised on invalid indentation (tabs or inconsistent spacing)."""


class SnakeRuntimeError(SnakeError):
    """Raised on general runtime errors during interpretation."""


def format_error(error: SnakeError, source_lines: list[str] | None = None) -> str:
    """Return a pretty-formatted error string with source context and carets.

    Args:
        error: The SnakeError instance.
        source_lines: Optional list of source lines for context display.

    Returns:
        A human-readable error message string.
    """
    class_name = type(error).__name__
    header = f"{class_name} on line {error.line}:" if error.line else f"{class_name}:"

    lines = [header]

    # Show the offending source line
    src = error.source_line
    if not src and source_lines and 0 < error.line <= len(source_lines):
        src = source_lines[error.line - 1]

    if src:
        lines.append(f"  {src.rstrip()}")
        # Try to underline the relevant portion
        carets = _build_carets(src, error.message)
        if carets:
            lines.append(f"  {carets}")

    lines.append(error.message)
    return "\n".join(lines)


def _build_carets(source_line: str, message: str) -> str:
    """Build a caret line pointing at the problematic token.

    Attempts to find a quoted token name in the message and underline it
    in the source line. Falls back to underlining the stripped content.
    """
    import re

    # Try to find a quoted identifier in the error message
    match = re.search(r"'(\w+)'", message)
    if match:
        token = match.group(1)
        idx = source_line.find(token)
        if idx >= 0:
            return " " * idx + "^" * len(token)

    return ""
