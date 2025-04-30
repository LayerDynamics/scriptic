#!/usr/bin/env python3
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
        return self.result

    def subtract(self, value):
        """Subtract a value from the result."""
        self.result -= value
        return self.result

    def multiply(self, value):
        """Multiply the result by a value."""
        self.result *= value
        return self.result

    def divide(self, value):
        """Divide the result by a value."""
        if value == 0:
            raise ValueError("Cannot divide by zero")
        self.result /= value
        return self.result

    def reset(self):
        """Reset the result to zero."""
        self.result = 0
        return self.result


# Variable that will be available in the REPL
sample_data = {"name": "Example Script", "version": "1.0.0", "description": "Demonstrates Scriptic file execution"}

# Print some information when the script is run
print(f"Loaded {__file__}")
print(f"Command-line arguments: {sys.argv[1:]}")
print("The following objects are now available in the REPL:")
print("- hello(): A function that greets people")
print("- Calculator: A simple calculator class")
print("- sample_data: A dictionary with script metadata")

# Execute some code only if run directly (not imported)
if __name__ == "__main__":
    print("\nScript executed as main program")
    print(hello())

    calc = Calculator()
    print(f"Calculator initial value: {calc.result}")
    print(f"5 + 3 = {calc.add(5).add(3)}")
