"""Snake language lexer — tokenizes raw source into a token stream."""

from dataclasses import dataclass
from snake.errors import SnakeSyntaxError, SnakeIndentationError

KEYWORDS = {"let", "say", "if", "else", "loop", "func", "input"}
INDENT_SIZE = 4
TWO_CHAR_OPS = {"==", "!=", ">=", "<="}
ONE_CHAR_OPS = {"+", "-", "*", "/", ">", "<", "="}


@dataclass
class Token:
    """A single lexical token."""
    type: str   # KEYWORD, IDENTIFIER, NUMBER, STRING, OP, COLON, LPAREN, RPAREN, NEWLINE, INDENT, DEDENT, EOF
    value: str
    line: int


def tokenize(source: str) -> list[Token]:
    """Tokenize Snake source code into a list of Tokens.

    Args:
        source: Raw Snake source string.

    Returns:
        A list of Token objects including INDENT/DEDENT/NEWLINE/EOF.
    """
    tokens: list[Token] = []
    indent_stack: list[int] = [0]
    lines = source.splitlines()

    for line_num, raw_line in enumerate(lines, start=1):
        # Strip comments
        line = _strip_comment(raw_line)

        # Skip blank lines
        if line.strip() == "":
            continue

        # Check for tabs
        leading = raw_line[:len(raw_line) - len(raw_line.lstrip())]
        if "\t" in leading:
            raise SnakeIndentationError(
                "Tabs are not allowed. Use 4 spaces for indentation.",
                line=line_num, source_line=raw_line,
            )

        # Compute indent level
        spaces = len(line) - len(line.lstrip(" "))
        if spaces % INDENT_SIZE != 0:
            raise SnakeIndentationError(
                f"Indentation must be a multiple of {INDENT_SIZE} spaces, got {spaces}.",
                line=line_num, source_line=raw_line,
            )
        level = spaces // INDENT_SIZE

        # Emit INDENT / DEDENT tokens
        if level > indent_stack[-1]:
            indent_stack.append(level)
            tokens.append(Token("INDENT", "", line_num))
        else:
            while level < indent_stack[-1]:
                indent_stack.pop()
                tokens.append(Token("DEDENT", "", line_num))
            if level != indent_stack[-1]:
                raise SnakeIndentationError(
                    "Inconsistent indentation level.",
                    line=line_num, source_line=raw_line,
                )

        # Tokenize the line content
        tokens.extend(_tokenize_line(line.strip(), line_num, raw_line))
        tokens.append(Token("NEWLINE", "\\n", line_num))

    # Close remaining indents
    while len(indent_stack) > 1:
        indent_stack.pop()
        tokens.append(Token("DEDENT", "", len(lines)))

    tokens.append(Token("EOF", "", len(lines) + 1))
    return tokens


def _strip_comment(line: str) -> str:
    """Remove comments from a line, respecting strings."""
    in_string = False
    for i, ch in enumerate(line):
        if ch == '"':
            in_string = not in_string
        elif ch == '#' and not in_string:
            return line[:i]
    return line


def _tokenize_line(line: str, line_num: int, raw_line: str) -> list[Token]:
    """Tokenize a single stripped line into tokens (no INDENT/DEDENT/NEWLINE)."""
    tokens: list[Token] = []
    i = 0

    while i < len(line):
        ch = line[i]

        # Whitespace
        if ch == " ":
            i += 1
            continue

        # String literal
        if ch == '"':
            j = i + 1
            while j < len(line) and line[j] != '"':
                j += 1
            if j >= len(line):
                raise SnakeSyntaxError(
                    "Unterminated string literal. Add a closing '\"'.",
                    line=line_num, source_line=raw_line,
                )
            tokens.append(Token("STRING", line[i + 1:j], line_num))
            i = j + 1
            continue

        # Colon
        if ch == ":":
            tokens.append(Token("COLON", ":", line_num))
            i += 1
            continue

        # Comma
        if ch == ",":
            tokens.append(Token("COMMA", ",", line_num))
            i += 1
            continue

        # Parentheses
        if ch == "(":
            tokens.append(Token("LPAREN", "(", line_num))
            i += 1
            continue
        if ch == ")":
            tokens.append(Token("RPAREN", ")", line_num))
            i += 1
            continue

        # Two-char operators
        if i + 1 < len(line) and line[i:i + 2] in TWO_CHAR_OPS:
            tokens.append(Token("OP", line[i:i + 2], line_num))
            i += 2
            continue

        # One-char operators
        if ch in ONE_CHAR_OPS:
            tokens.append(Token("OP", ch, line_num))
            i += 1
            continue

        # Numbers
        if ch.isdigit():
            j = i
            while j < len(line) and (line[j].isdigit() or line[j] == "."):
                j += 1
            tokens.append(Token("NUMBER", line[i:j], line_num))
            i = j
            continue

        # Identifiers / keywords
        if ch.isalpha() or ch == "_":
            j = i
            while j < len(line) and (line[j].isalnum() or line[j] == "_"):
                j += 1
            word = line[i:j]
            tok_type = "KEYWORD" if word in KEYWORDS else "IDENTIFIER"
            tokens.append(Token(tok_type, word, line_num))
            i = j
            continue

        raise SnakeSyntaxError(
            f"Unexpected character '{ch}'.",
            line=line_num, source_line=raw_line,
        )

    return tokens
