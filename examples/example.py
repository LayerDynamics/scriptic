#!/usr/bin/env python3
"""
Example usage of Scriptic REPL

This example demonstrates how to embed Scriptic in an application
and extend it with custom commands.
"""

from scriptic import Scriptic


class DemoApp:
    """A simple demo application with state."""

    def __init__(self):
        self.counter = 0
        self.message = "Hello from DemoApp!"

    def increment(self, amount=1):
        """Increment the counter."""
        self.counter += amount
        return self.counter

    def get_status(self):
        """Get the current application status."""
        return f"Counter: {self.counter}, Message: {self.message}"


def main():
    """Run the demo application with an embedded Scriptic REPL."""
    # Create our demo application
    app = DemoApp()

    # Set up the initial context with our application object
    context = {
        "app": app,
        "increment": app.increment,
        "status": app.get_status,
    }

    # Create a Scriptic instance
    repl = Scriptic(
        context=context,
        prompt="demo>>> ",
        intro="""
Demo App REPL
============
Type Python code to interact with the app.
Built-in objects: app, increment(), status()
Try %help for available commands.
""",
    )

    # Add a custom command
    def cmd_stats(args):
        """Show application statistics."""
        print("Application Statistics:")
        print(f"- Counter value: {app.counter}")
        print(f"- Message length: {len(app.message)}")

    repl.register_command("stats", cmd_stats)

    # Add another custom command with parameters
    def cmd_set_message(args):
        """Set the application message.

        Usage: %set_message Your new message here
        """
        if not args:
            print("Error: Message cannot be empty")
            return

        app.message = args
        print(f"Message set to: {app.message}")

    repl.register_command("set_message", cmd_set_message)

    # Run the REPL
    try:
        repl.run()
    except KeyboardInterrupt:
        print("\nExiting...")

    # Show final state when exiting
    print("\nFinal application state:")
    print(app.get_status())


if __name__ == "__main__":
    main()