"""Snake language parser — transforms token stream into an AST."""

from dataclasses import dataclass
from typing import Any
from snake.lexer import Token
from snake.errors import SnakeSyntaxError


# ── AST Node Definitions ──

@dataclass
class NumberNode:
    """A numeric literal."""
    value: float
    line: int

@dataclass
class StringNode:
    """A string literal."""
    value: str
    line: int

@dataclass
class IdentifierNode:
    """A variable reference."""
    name: str
    line: int

@dataclass
class BinOpNode:
    """A binary operation (arithmetic or comparison)."""
    left: Any
    op: str
    right: Any
    line: int

@dataclass
class InputNode:
    """An input expression."""
    prompt: str
    line: int

@dataclass
class PrintNode:
    """A say statement."""
    values: list
    line: int

@dataclass
class AssignNode:
    """A let assignment statement."""
    name: str
    value: Any
    line: int

@dataclass
class IfNode:
    """An if/else conditional block."""
    condition: Any
    then_body: list
    else_body: list
    line: int

@dataclass
class LoopNode:
    """A loop N times block."""
    count: Any
    body: list
    line: int

@dataclass
class FuncDefNode:
    """A function definition."""
    name: str
    body: list
    line: int

@dataclass
class CallNode:
    """A function call (bare identifier on its own line)."""
    name: str
    line: int


# Union type for type hints
ExprNode = NumberNode | StringNode | IdentifierNode | BinOpNode | InputNode
ASTNode = PrintNode | AssignNode | IfNode | LoopNode | FuncDefNode | CallNode

# Operator precedence
PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, ">": 0, "<": 0, "==": 0, "!=": 0, ">=": 0, "<=": 0}


class Parser:
    """Recursive descent parser for the Snake language."""

    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0

    def parse(self) -> list[ASTNode]:
        """Parse the token stream into a list of top-level AST nodes."""
        nodes: list[ASTNode] = []
        while not self._at_end():
            self._skip_newlines()
            if self._at_end():
                break
            nodes.append(self._parse_statement())
        return nodes

    # ── Statement parsing ──

    def _parse_statement(self) -> ASTNode:
        """Dispatch to the appropriate statement parser based on current token."""
        tok = self._current()

        if tok.type == "KEYWORD":
            if tok.value == "say":
                return self._parse_say()
            if tok.value == "let":
                return self._parse_let()
            if tok.value == "if":
                return self._parse_if()
            if tok.value == "loop":
                return self._parse_loop()
            if tok.value == "func":
                return self._parse_func()

        if tok.type == "IDENTIFIER":
            return self._parse_call()

        raise SnakeSyntaxError(
            f"Unexpected token '{tok.value}'.",
            line=tok.line,
        )

    def _parse_say(self) -> PrintNode:
        """Parse: say <expr> [, <expr> ...]"""
        tok = self._expect("KEYWORD", "say")
        exprs = [self._parse_expression()]
        while self._check("COMMA"):
            self._advance()
            exprs.append(self._parse_expression())
        self._skip_newlines()
        return PrintNode(values=exprs, line=tok.line)

    def _parse_let(self) -> AssignNode:
        """Parse: let <name> = <expr>"""
        tok = self._expect("KEYWORD", "let")
        name_tok = self._expect("IDENTIFIER")
        self._expect("OP", "=")
        expr = self._parse_expression()
        self._skip_newlines()
        return AssignNode(name=name_tok.value, value=expr, line=tok.line)

    def _parse_if(self) -> IfNode:
        """Parse: if <condition>: <block> [else: <block>]"""
        tok = self._expect("KEYWORD", "if")
        condition = self._parse_expression()
        self._expect("COLON")
        self._skip_newlines()
        then_body = self._parse_block()

        else_body: list = []
        if self._check("KEYWORD", "else"):
            self._advance()
            self._expect("COLON")
            self._skip_newlines()
            else_body = self._parse_block()

        return IfNode(condition=condition, then_body=then_body, else_body=else_body, line=tok.line)

    def _parse_loop(self) -> LoopNode:
        """Parse: loop <count>: <block>"""
        tok = self._expect("KEYWORD", "loop")
        count = self._parse_expression()
        self._expect("COLON")
        self._skip_newlines()
        body = self._parse_block()
        return LoopNode(count=count, body=body, line=tok.line)

    def _parse_func(self) -> FuncDefNode:
        """Parse: func <name>: <block>"""
        tok = self._expect("KEYWORD", "func")
        name_tok = self._expect("IDENTIFIER")
        self._expect("COLON")
        self._skip_newlines()
        body = self._parse_block()
        return FuncDefNode(name=name_tok.value, body=body, line=tok.line)

    def _parse_call(self) -> CallNode:
        """Parse: <identifier> (bare function call)"""
        tok = self._expect("IDENTIFIER")
        self._skip_newlines()
        return CallNode(name=tok.value, line=tok.line)

    # ── Block parsing ──

    def _parse_block(self) -> list[ASTNode]:
        """Parse an indented block delimited by INDENT … DEDENT."""
        self._expect("INDENT")
        nodes: list[ASTNode] = []
        while not self._check("DEDENT") and not self._at_end():
            self._skip_newlines()
            if self._check("DEDENT") or self._at_end():
                break
            nodes.append(self._parse_statement())
        self._expect("DEDENT")
        return nodes

    # ── Expression parsing (Pratt-style precedence climbing) ──

    def _parse_expression(self, min_prec: int = -1) -> ExprNode:
        """Parse an expression using precedence climbing."""
        left = self._parse_atom()

        while (
            not self._at_end()
            and self._current().type == "OP"
            and self._current().value in PRECEDENCE
            and PRECEDENCE[self._current().value] > min_prec
        ):
            op_tok = self._advance()
            right = self._parse_expression(PRECEDENCE[op_tok.value])
            left = BinOpNode(left=left, op=op_tok.value, right=right, line=op_tok.line)

        return left

    def _parse_atom(self) -> ExprNode:
        """Parse a primary expression (number, string, identifier, input, paren group)."""
        tok = self._current()

        if tok.type == "NUMBER":
            self._advance()
            val = float(tok.value) if "." in tok.value else int(tok.value)
            return NumberNode(value=val, line=tok.line)

        if tok.type == "STRING":
            self._advance()
            return StringNode(value=tok.value, line=tok.line)

        if tok.type == "IDENTIFIER":
            self._advance()
            return IdentifierNode(name=tok.value, line=tok.line)

        if tok.type == "KEYWORD" and tok.value == "input":
            self._advance()
            prompt_tok = self._expect("STRING")
            return InputNode(prompt=prompt_tok.value, line=tok.line)

        if tok.type == "LPAREN":
            self._advance()
            expr = self._parse_expression()
            self._expect("RPAREN")
            return expr

        raise SnakeSyntaxError(
            f"Expected an expression, got '{tok.value}'.",
            line=tok.line,
        )

    # ── Token helpers ──

    def _current(self) -> Token:
        """Return the current token."""
        return self.tokens[self.pos]

    def _advance(self) -> Token:
        """Consume and return the current token."""
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def _at_end(self) -> bool:
        """Return True if at EOF."""
        return self.pos >= len(self.tokens) or self.tokens[self.pos].type == "EOF"

    def _check(self, tok_type: str, value: str | None = None) -> bool:
        """Check if current token matches type (and optionally value)."""
        if self._at_end():
            return False
        tok = self._current()
        if tok.type != tok_type:
            return False
        if value is not None and tok.value != value:
            return False
        return True

    def _expect(self, tok_type: str, value: str | None = None) -> Token:
        """Consume a token of the expected type/value, or raise SnakeSyntaxError."""
        if self._at_end():
            raise SnakeSyntaxError(
                f"Unexpected end of input, expected {tok_type}" + (f" '{value}'" if value else "") + ".",
                line=self.tokens[-1].line,
            )
        tok = self._current()
        if tok.type != tok_type or (value is not None and tok.value != value):
            expected = f"{tok_type} '{value}'" if value else tok_type
            raise SnakeSyntaxError(
                f"Expected {expected}, got {tok.type} '{tok.value}'.",
                line=tok.line,
            )
        return self._advance()

    def _skip_newlines(self) -> None:
        """Skip over NEWLINE tokens."""
        while not self._at_end() and self._current().type == "NEWLINE":
            self._advance()
