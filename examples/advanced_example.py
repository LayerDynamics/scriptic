#!/usr/bin/env python3
"""
Advanced Scriptic REPL Example

This example demonstrates more advanced features of Scriptic:
- Custom command decorators
- Script loading
- Enhanced output formatting
- Extension via subclassing
"""

import os
import sys
import time
import traceback
from scriptic import Scriptic


class EnhancedScriptic(Scriptic):
    """An enhanced version of Scriptic with additional features."""
    
    def __init__(self, *args, **kwargs):
        # Initialize with custom styling options
        self.use_colors = kwargs.pop('use_colors', True)
        super().__init__(*args, **kwargs)
        
        # Add additional built-in commands
        self.register_command("load", self._cmd_load)
        self.register_command("time", self._cmd_time)
        self.register_command("clear", self._cmd_clear)
        self.register_command("history", self._cmd_history)
        
    def command(self, name=None):
        """
        Decorator for registering commands.
        
        Usage:
            @repl.command()
            def mycommand(args):
                '''Command documentation'''
                # Command implementation
                
            @repl.command('shortname')
            def longer_function_name(args):
                # This will be registered as %shortname
        """
        def decorator(func):
            cmd_name = name or func.__name__
            self.register_command(cmd_name, func)
            return func
        return decorator
        
    def _execute_code(self, code_str):
        """Override to add execution timing."""
        start_time = time.time()
        
        # Call the parent implementation
        super()._execute_code(code_str)
        
        # Show execution time for non-trivial operations
        elapsed = time.time() - start_time
        if elapsed > 0.1:  # Only show for operations that take some time
            if self.use_colors:
                print(f"\033[90m# Executed in {elapsed:.4f} seconds\033[0m")
            else:
                print(f"# Executed in {elapsed:.4f} seconds")
    
    # Additional built-in commands
    
    def _cmd_load(self, args):
        """Load and execute a Python script file.
        
        Usage: %load filename.py
        """
        filename = args.strip()
        if not filename:
            print("Error: No filename specified")
            return
            
        try:
            with open(filename, 'r') as f:
                code = f.read()
            print(f"Executing {filename}...")
            exec(code, self.context)
            print(f"Finished executing {filename}")
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            traceback.print_exc()
            
    def _cmd_time(self, args):
        """Time the execution of Python code.
        
        Usage: %time expression or statement
        """
        if not args:
            print("Error: No code specified to time")
            return
            
        # Run multiple times for more accurate timing
        runs = 5
        times = []
        
        print(f"Timing: {args}")
        for i in range(runs):
            start = time.time()
            try:
                # Try eval first (for expressions)
                try:
                    result = eval(args, self.context)
                    if i == 0 and result is not None:
                        print(f"Result: {result}")
                except SyntaxError:
                    # Fall back to exec for statements
                    exec(args, self.context)
            except Exception as e:
                print(f"Error: {e}")
                return
                
            elapsed = time.time() - start
            times.append(elapsed)
            
        # Calculate statistics
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)
        
        # Display results
        print(f"Time statistics (over {runs} runs):")
        print(f"  Average: {avg_time:.6f} seconds")
        print(f"  Minimum: {min_time:.6f} seconds")
        print(f"  Maximum: {max_time:.6f} seconds")
        
    def _cmd_clear(self, args):
        """Clear the screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def _cmd_history(self, args):
        """Show command history (when readline is available)."""
        try:
            import readline
            history_length = readline.get_current_history_length()
            print("Command history:")
            for i in range(1, history_length + 1):
                item = readline.get_history_item(i)
                if item:
                    print(f"  {i}: {item}")
        except (ImportError, AttributeError):
            print("Command history not available (readline module not found)")


def main():
    """Run the advanced Scriptic example."""
    # Create REPL with styled prompt
    repl = EnhancedScriptic(
        prompt="\033[1;32m>>>\033[0m ",
        more_prompt="\033[1;36m...\033[0m ",
        intro="""
=================================
Advanced Scriptic REPL Example
=================================
Try the following commands:
  %help        - Show available commands
  %load file   - Load a Python script
  %time expr   - Time an expression
  %clear       - Clear the screen
  %history     - Show command history
  %vars        - Show variables

Type Python code (multi-line supported)
=================================
"""
    )
    
    # Register commands using the decorator pattern
    @repl.command()
    def hello(args):
        """Say hello to someone.
        
        Usage: %hello [name]
        """
        name = args.strip() or "World"
        print(f"Hello, {name}!")
        
    @repl.command('fibonacci')
    def generate_fibonacci(args):
        """Generate Fibonacci sequence up to n.
        
        Usage: %fibonacci n
        """
        try:
            n = int(args.strip() or "10")
            if n <= 0:
                print("Please provide a positive number")
                return
        except ValueError:
            print("Error: Please provide a valid number")
            return
            
        a, b = 0, 1
        sequence = [a]
        while b < n:
            sequence.append(b)
            a, b = b, a + b
            
        print(f"Fibonacci sequence up to {n}:")
        print(sequence)
        
    # Add some demo variables to context
    sample_data = {
        'users': ['Alice', 'Bob', 'Charlie'],
        'scores': [95, 87, 92],
    }
    
    class Calculator:
        """Demo calculator class."""
        
        def add(self, a, b):
            return a + b
            
        def subtract(self, a, b):
            return a - b
            
        def multiply(self, a, b):
            return a * b
            
        def divide(self, a, b):
            if b == 0:
                raise ValueError("Cannot divide by zero")
            return a / b
    
    # Add objects to context
    repl.context.update({
        'data': sample_data,
        'calc': Calculator(),
        'os': os,
        'sys': sys,
    })
    
    # Run the REPL
    try:
        repl.run()
    except KeyboardInterrupt:
        print("\nExiting...")


if __name__ == "__main__":
    main()