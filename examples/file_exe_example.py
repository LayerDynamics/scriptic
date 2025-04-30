#!/usr/bin/env python3
"""
Scriptic File Execution Demo

This script demonstrates how to use Scriptic's file execution capabilities.
It shows how to run Python files within a REPL session and work with the
loaded components interactively.
"""

import os
import sys
from scriptic import Scriptic

def main():
    """Run the file execution demonstration."""
    
    # Create a Scriptic instance with a custom prompt
    repl = Scriptic(
        prompt="demo>>> ",
        intro="""
==============================================
Scriptic File Execution Demo
==============================================

This demo shows how to work with Python files in Scriptic.
Try the following commands:

1. %run example_script.py Alice
   - This will execute the example script with 'Alice' as an argument
   - All functions, classes, and variables from the script will be available

2. %load example_script.py
   - This will load the script into the buffer without executing it
   - You can review and modify the code before running it

3. After running the script, try:
   - hello("Bob")
   - calc = Calculator()
   - calc.add(5).multiply(2)
   - print(sample_data)

==============================================
"""
    )
    
    # Create a sample script if it doesn't exist
    if not os.path.exists("example_script.py"):
        print("Creating example_script.py...")
        with open("example_script.py", "w") as f:
            f.write('''#!/usr/bin/env python3
"""
Example script for Scriptic REPL

This script demonstrates how a Python file can be loaded
and executed within the Scriptic REPL environment.
"""

import sys

# Function that will be available in the REPL after running
def hello(name=None):
    """Say hello to a person."""
    if name is None:
        # If no name provided, use command-line arguments
        if len(sys.argv) > 1:
            name = sys.argv[1]
        else:
            name = "World"
    
    return f"Hello, {name}!"

# Class that will be available in the REPL
class Calculator:
    """A simple calculator class."""
    
    def __init__(self):
        self.result = 0
    
    def add(self, value):
        """Add a value to the result."""
        self.result += value
        return self
    
    def subtract(self, value):
        """Subtract a value from the result."""
        self.result -= value
        return self
    
    def multiply(self, value):
        """Multiply the result by a value."""
        self.result *= value
        return self
    
    def divide(self, value):
        """Divide the result by a value."""
        if value == 0:
            raise ValueError("Cannot divide by zero")
        self.result /= value
        return self
    
    def reset(self):
        """Reset the result to zero."""
        self.result = 0
        return self
    
    def __str__(self):
        return f"Calculator(result={self.result})"

# Variable that will be available in the REPL
sample_data = {
    'name': 'Example Script',
    'version': '1.0.0',
    'description': 'Demonstrates Scriptic file execution'
}

# Print some information when the script is run
print(f"Loaded {__file__}")
print(f"Command-line arguments: {sys.argv[1:]}")
print("The following objects are now available in the REPL:")
print("- hello(): A function that greets people")
print("- Calculator: A simple calculator class")
print("- sample_data: A dictionary with script metadata")

# Execute some code only if run directly (not imported)
if __name__ == "__main__":
    print("\\nScript executed as main program")
    print(hello())
    
    calc = Calculator()
    print(f"Calculator initial value: {calc.result}")
    print(f"5 + 3 = {calc.add(5).add(3).result}")
''')
    
    # Add a helper command to show script content
    def cmd_show_script(args):
        """Show the content of the example script."""
        try:
            with open("example_script.py", "r") as f:
                content = f.read()
            print("\nContent of example_script.py:")
            print("=" * 50)
            print(content)
            print("=" * 50)
        except Exception as e:
            print(f"Error reading script: {e}")
    
    repl.register_command("show_script", cmd_show_script)
    
    # Run the REPL
    try:
        repl.run()
    except KeyboardInterrupt:
        print("\nExiting demo...")


if __name__ == "__main__":
    main()