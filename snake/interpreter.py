"""Snake language interpreter — walks the AST and executes it."""

from snake.parser import (
    PrintNode, AssignNode, IfNode, LoopNode, FuncDefNode, CallNode,
    BinOpNode, NumberNode, StringNode, IdentifierNode, InputNode,
)
from snake.errors import SnakeNameError, SnakeTypeError, SnakeRuntimeError, format_error
from snake.utils import snake_type_name


class Interpreter:
    """AST-walking interpreter for the Snake language."""

    def __init__(self):
        self.env: dict[str, any] = {}
        self.functions: dict[str, FuncDefNode] = {}
        self.source_lines: list[str] = []

    def run(self, nodes: list, source_lines: list[str] | None = None) -> None:
        """Execute a list of AST nodes.

        Args:
            nodes: Top-level AST nodes from the parser.
            source_lines: Original source lines for error reporting.
        """
        if source_lines:
            self.source_lines = source_lines
        for node in nodes:
            self.execute(node)

    def execute(self, node) -> None:
        """Dispatch execution to the appropriate visit method."""
        method_name = f"visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise SnakeRuntimeError(f"Unknown node type: {type(node).__name__}", line=getattr(node, "line", 0))
        method(node)

    def visit_PrintNode(self, node: PrintNode) -> None:
        """Execute a say statement."""
        values = [self.eval_expr(v) for v in node.values]
        print(*values)

    def visit_AssignNode(self, node: AssignNode) -> None:
        """Execute a let assignment."""
        self.env[node.name] = self.eval_expr(node.value)

    def visit_IfNode(self, node: IfNode) -> None:
        """Execute an if/else conditional."""
        condition = self.eval_expr(node.condition)
        body = node.then_body if condition else node.else_body
        for stmt in body:
            self.execute(stmt)

    def visit_LoopNode(self, node: LoopNode) -> None:
        """Execute a loop N times."""
        count = self.eval_expr(node.count)
        if not isinstance(count, (int, float)):
            raise SnakeTypeError(
                f"Loop count must be a number, got {snake_type_name(count)}.",
                line=node.line,
            )
        for _ in range(int(count)):
            for stmt in node.body:
                self.execute(stmt)

    def visit_FuncDefNode(self, node: FuncDefNode) -> None:
        """Register a function definition."""
        self.functions[node.name] = node

    def visit_CallNode(self, node: CallNode) -> None:
        """Execute a function call."""
        if node.name not in self.functions:
            raise SnakeNameError(
                f"Function '{node.name}' is not defined. Did you forget 'func {node.name}:'?",
                line=node.line,
            )
        func = self.functions[node.name]
        for stmt in func.body:
            self.execute(stmt)

    # ── Expression evaluation ──

    def eval_expr(self, node) -> any:
        """Evaluate an expression node and return a Python value."""
        if isinstance(node, NumberNode):
            return node.value

        if isinstance(node, StringNode):
            return node.value

        if isinstance(node, IdentifierNode):
            if node.name not in self.env:
                raise SnakeNameError(
                    f"Variable '{node.name}' is not defined. Did you forget 'let {node.name} = ...'?",
                    line=node.line,
                )
            return self.env[node.name]

        if isinstance(node, InputNode):
            return input(node.prompt)

        if isinstance(node, BinOpNode):
            return self._eval_binop(node)

        raise SnakeRuntimeError(f"Cannot evaluate node: {type(node).__name__}", line=getattr(node, "line", 0))

    def _eval_binop(self, node: BinOpNode) -> any:
        """Evaluate a binary operation."""
        left = self.eval_expr(node.left)
        right = self.eval_expr(node.right)

        # String concatenation
        if node.op == "+" and isinstance(left, str) and isinstance(right, str):
            return left + right

        # Comparison operators work on same types
        if node.op in ("==", "!=", ">", "<", ">=", "<="):
            return self._compare(left, node.op, right, node.line)

        # Arithmetic requires numbers
        if not isinstance(left, (int, float)) or not isinstance(right, (int, float)):
            raise SnakeTypeError(
                f"Cannot {_OP_NAMES.get(node.op, 'operate on')} {snake_type_name(left)} and {snake_type_name(right)}. "
                "Both sides must be the same type.",
                line=node.line,
            )

        if node.op == "+":
            return left + right
        if node.op == "-":
            return left - right
        if node.op == "*":
            return left * right
        if node.op == "/":
            if right == 0:
                raise SnakeRuntimeError("Division by zero.", line=node.line)
            return left / right

        raise SnakeRuntimeError(f"Unknown operator '{node.op}'.", line=node.line)

    def _compare(self, left, op: str, right, line: int) -> bool:
        """Evaluate a comparison operation."""
        try:
            if op == "==":
                return left == right
            if op == "!=":
                return left != right
            if op == ">":
                return left > right
            if op == "<":
                return left < right
            if op == ">=":
                return left >= right
            if op == "<=":
                return left <= right
        except TypeError:
            raise SnakeTypeError(
                f"Cannot compare {snake_type_name(left)} and {snake_type_name(right)}.",
                line=line,
            )
        raise SnakeRuntimeError(f"Unknown comparison '{op}'.", line=line)


# Human-readable operator names for error messages
_OP_NAMES = {"+": "add", "-": "subtract", "*": "multiply", "/": "divide"}
