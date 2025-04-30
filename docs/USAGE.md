# Scriptic Usage Guide

## Overview

Scriptic is a lightweight, embeddable Python REPL designed for integration within Python applications. It provides a complete interactive Python environment with features like multiline input, custom commands, and context sharing.

## Key Features

- **Minimal Size**: Single-file core implementation (~300 lines)
- **Zero Dependencies**: Uses only Python's standard library
- **Extensible**: Add custom commands and hooks for your specific needs
- **Embeddable**: Integrate with any Python application by sharing state
- **Signal Safe**: Gracefully handles keyboard interrupts and terminal signals
- **Context Aware**: Access and manipulate your application's objects directly

## Getting Started

### Basic Usage

The simplest way to use Scriptic is to import it and run with defaults:

```python
from scriptic import run_scriptic

# Start a basic REPL
run_scriptic()
```

### Embedding in an Application

To integrate Scriptic with your application:

1. Create a context dictionary with your application objects
2. Initialize Scriptic with this context
3. Register any custom commands
4. Start the REPL

```python
from scriptic import Scriptic

# Create your application
class MyApp:
    def __init__(self):
        self.counter = 0
        
    def increment(self):
        self.counter += 1
        return self.counter

app = MyApp()

# Create a context with your objects
context = {
    "app": app,
    "increment": app.increment
}

# Create the REPL with your context
repl = Scriptic(
    context=context,
    prompt="myapp> ",
    intro="Welcome to MyApp console. Try using 'app' or 'increment()'."
)

# Add a custom command
def cmd_count(args):
    """Show the current counter value."""
    print(f"Current count: {app.counter}")

repl.register_command("count", cmd_count)

# Run the REPL
repl.run()
```

## Custom Commands

Custom commands are a powerful way to extend Scriptic functionality:

```python
# Basic command registration
def cmd_hello(args):
    """Say hello to someone."""
    name = args.strip() or "World"
    print(f"Hello, {name}!")

repl.register_command("hello", cmd_hello)
```

In the REPL, you access this with:

```
>>> %hello Alice
Hello, Alice!
```

### Using Command Decorators (Advanced)

The advanced example shows how to use a decorator pattern for commands:

```python
# Create a subclass with decorator support
class EnhancedREPL(Scriptic):
    def command(self, name=None):
        def decorator(func):
            cmd_name = name or func.__name__
            self.register_command(cmd_name, func)
            return func
        return decorator

# Usage
repl = EnhancedREPL(context)

@repl.command()
def stats(args):
    """Show application statistics."""
    print("Application statistics...")

@repl.command('shortname')
def longer_function_name(args):
    """This will be %shortname in the REPL."""
    print("Command executed!")
```

## Multiline Input

Scriptic automatically handles multiline Python code:

```python
>>> def factorial(n):
...     if n <= 1:
...         return 1
...     return n * factorial(n-1)
... 
>>> factorial(5)
120
```

## Python File Execution

Scriptic provides two built-in commands for working with Python files:

### 1. The %run Command

The `%run` command executes a Python file in the current context:

```python
# In the REPL
>>> %run script.py arg1 arg2
```

This command:
- Reads and executes the specified Python file
- Sets `sys.argv` to pass command-line arguments to the script
- Makes all definitions from the script available in the REPL context
- Properly handles exceptions and displays tracebacks

### 2. The %load Command

The `%load` command loads a file into the buffer without executing it:

```python
# In the REPL
>>> %load script.py
```

This command:
- Reads the file content and displays it in the REPL
- Adds the file content to the input buffer
- Allows you to edit the code before executing it
- Preserves indentation and formatting

### Example Workflow

A typical workflow using these commands might look like:

1. Write a Python script with functions, classes, and variables
2. Load it into your REPL with `%run script.py`
3. Interactively test and use the loaded components
4. Make changes to the script externally
5. Reload with `%run script.py` to update the REPL

Or alternatively:

1. Load a script with `%load script.py` to review it
2. Make changes directly in the REPL
3. Execute the modified code by pressing Enter
4. Save the modified code externally if needed

## Signal Handling

Scriptic handles keyboard interrupts gracefully:

- `Ctrl+C` interrupts the current input without exiting
- `Ctrl+D` exits the REPL cleanly

## Extending with Subclassing

For more advanced customization, create a subclass:

```python
class CustomREPL(Scriptic):
    def _execute_code(self, code_str):
        """Override to add custom behavior before/after execution."""
        print("Executing code...")
        super()._execute_code(code_str)
        print("Execution complete.")
```

## Best Practices

1. **Keep the Context Clean**: Avoid polluting the REPL context with too many objects
2. **Document Commands**: Always provide clear docstrings for custom commands
3. **Handle Errors**: Catch exceptions in custom commands to prevent REPL crashes
4. **Provide Feedback**: Print helpful messages when commands succeed or fail
5. **Exit Gracefully**: Clean up resources when the REPL exits

## Advanced Techniques

### 1. Dynamic Command Registration

Register commands based on available features:

```python
for feature_name, feature_func in app.get_features().items():
    repl.register_command(
        feature_name, 
        lambda args, func=feature_func: func(args)
    )
```

### 2. Persistent History

Save and restore command history:

```python
import readline
import os

history_file = os.path.expanduser("~/.myapp_history")

# Load history if it exists
if os.path.exists(history_file):
    readline.read_history_file(history_file)

# Save on exit
import atexit
atexit.register(readline.write_history_file, history_file)
```

### 3. Syntax Highlighting (Optional Extension)

For simple syntax highlighting:

```python
try:
    import pygments
    from pygments.lexers import PythonLexer
    from pygments.formatters import TerminalFormatter
    
    def highlight(code):
        return pygments.highlight(
            code, PythonLexer(), TerminalFormatter()
        )
except ImportError:
    def highlight(code):
        return code
```

## Conclusion

Scriptic provides a lightweight yet powerful REPL that can be embedded in any Python application. By following these patterns and examples, you can create a customized interactive console perfectly tailored to your application's needs.