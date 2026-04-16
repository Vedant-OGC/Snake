# Snake 🐍

A beginner-friendly, Python-hosted interpreted programming language.

## Features

- Readable, minimal syntax inspired by Python
- Full Lexer → Parser → AST → Interpreter pipeline
- Transpile Snake source to executable Python `.py` files
- Interactive REPL with multi-line support
- Beginner-friendly error messages (no raw Python tracebacks)

## Quick Start

```bash
# Run a Snake program
python snake/main.py bite examples/hello.snk

# Transpile to Python
python snake/main.py compile examples/combined.snk -o out.py
python out.py

# Launch the REPL
python snake/main.py repl
```

## Language Syntax

```
# Variables
let name = "Newton"
let age = 17

# Output
say "Hello, World!"
say name

# Input
let name = input "What is your name? "

# Conditions
if x > 5:
    say "x is big"
else:
    say "x is small"

# Loops
loop 3:
    say "looping!"

# Functions
func greet:
    say "Hello from a function!"

greet
```

## CLI Commands

| Command | Description |
|---|---|
| `snake bite <file.snk>` | Run a Snake program |
| `snake bite <file.snk> --debug` | Run with AST debug output |
| `snake compile <file.snk>` | Transpile to Python |
| `snake compile <file.snk> -o out.py` | Transpile to custom path |
| `snake repl` | Launch interactive REPL |

## File Extension

Snake source files use the `.snk` extension.

## License

MIT
