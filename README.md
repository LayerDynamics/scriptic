# Scriptic
[![Upload Python Package](https://github.com/LayerDynamics/scriptic/actions/workflows/python-publish.yml/badge.svg)](https://github.com/LayerDynamics/scriptic/actions/workflows/python-publish.yml)

A minimalist, embeddable Python REPL with zero external dependencies.

## Features

- **Zero Dependencies**: Uses only the Python standard library
- **Lightweight**: Single file implementation (~300 lines of code)
- **Embeddable**: Easily integrate into any Python application
- **Extensible**: Add custom commands with simple decorators
- **Context Injection**: Share your application objects with the REPL
- **Multiline Support**: Properly handles functions, classes, and blocks
- **Signal Handling**: Gracefully manages keyboard interrupts
- **Command History**: Up/down arrow navigation (when readline is available)

## Installation

Simply copy `scriptic.py` into your project:

```bash
# From GitHub
curl -O https://raw.githubusercontent.com/LayerDynamics/scriptic/main/scriptic.py

# Or just copy the file directly to your project
```

## Basic Usage

```python
from scriptic import run_scriptic

# Start a basic REPL
run_scriptic(intro="Welcome to Scriptic!")
```

## Embedding in Your Application

```python
from scriptic import Scriptic

# Create your application objects
my_app = MyApplication()

# Set up the REPL context with your objects
context = {
    "app": my_app,
    "do_something": my_app.do_something,
}

# Create and configure the REPL
repl = Scriptic(
    context=context,
    prompt="myapp> ",
    intro="MyApp Console - Type commands or %help"
)

# Add custom commands
def cmd_status(args):
    """Show the application status."""
    print(f"App status: {my_app.get_status()}")
    
repl.register_command("status", cmd_status)

# Run the REPL
repl.run()
```

## Built-in Commands

Scriptic comes with several built-in commands:

- **%help** - Display help for available commands
- **%exit** or **%quit** - Exit the REPL
- **%vars** - Show variables in the current context
- **%reset** - Reset the REPL context to initial state
- **%run** - Execute a Python file in the current context
- **%load** - Load a Python file into the buffer without executing it

## Adding Custom Commands

Custom commands start with `%` and can take arguments:

```python
def cmd_greet(args):
    """Greet a person by name.
    
    Usage: %greet [name]
    """
    name = args.strip() or "World"
    print(f"Hello, {name}!")

repl.register_command("greet", cmd_greet)
```

In the REPL, you can call this with:

```
>>> %greet Alice
Hello, Alice!
```

## Advanced Usage

### Executing Python Files

Scriptic includes built-in support for running and loading Python files:

```python
# In the REPL, execute a Python file in the current context
>>> %run script.py arg1 arg2

# The script.py file can access sys.argv as usual
# sys.argv[0] will be 'script.py'
# sys.argv[1] will be 'arg1'
# sys.argv[2] will be 'arg2'

# All definitions from the script become available in the REPL
>>> my_function_from_script()

# Load a file into the buffer without executing it
>>> %load another_script.py
# The file content will be displayed and added to the buffer
# You can edit it before executing
```

These commands make it easy to work with external Python files while maintaining the interactive nature of the REPL environment.

### Customizing Signal Handling

Override the `_handle_signal` method for custom behavior:

```python
class MyREPL(Scriptic):
    def _handle_signal(self, sig, frame):
        if sig == signal.SIGINT:
            print("\nDo you want to exit? (y/n)")
            if input().lower() == 'y':
                self.running = False
            else:
                self.buffer = []  # Clear input buffer
```

## Example Application

See `example.py` for a complete demonstration of embedding Scriptic in a simple application.

## License

MIT License - Feel free to use and modify as needed!