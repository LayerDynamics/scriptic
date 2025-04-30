#!/usr/bin/env python3
"""
Scriptic: A minimalist embeddable Python REPL

A lightweight, zero-dependency REPL designed to be embedded within Python applications.
Features include multiline input support, custom command hooks, and context injection.
"""

import sys
import os
import code
import signal
import traceback
import readline  # Enables command history automatically when available
import argparse
import pdb
import atexit
from typing import Dict, Any, Callable, Optional


class Scriptic:
    """
    A minimalist embeddable Python REPL with extensibility hooks.

    This class provides a lightweight REPL that can be embedded within
    any Python application with minimal overhead.

    Features:
    - Multi-line Python code support
    - Custom command registration (prefixed with %)
    - Context injection (provide your app objects)
    - Signal handling (Ctrl+C won't kill your app)
    """

    def __init__(self, context: Optional[Dict[str, Any]] = None, prompt: str = ">>> ", more_prompt: str = "... ", intro: Optional[str] = None, history_file: Optional[str] = None):
        """
        Initialize the Scriptic REPL.

        Args:
            context: Dictionary of objects to inject into REPL namespace
            prompt: Primary prompt string
            more_prompt: Continuation prompt for multiline input
            intro: Introduction text to display when REPL starts
            history_file: Path to the history file (None for no history)
        """
        self.context = {} if context is None else context
        self.prompt = prompt
        self.more_prompt = more_prompt
        self.intro = intro
        self.running = False
        self.buffer = []
        self.custom_commands = {}
        self.history_file = history_file or os.path.expanduser("~/.scriptic_history")
        self._completion_matches = []
        self._original_sigint = None
        self._original_sigterm = None

        # Make the REPL instance available in the context
        self.context["repl"] = self

        # Register built-in commands
        self.register_command("help", self._cmd_help)
        self.register_command("exit", self._cmd_exit)
        self.register_command("quit", self._cmd_exit)
        self.register_command("vars", self._cmd_vars)
        self.register_command("reset", self._cmd_reset)
        self.register_command("run", self._cmd_run)
        self.register_command("load", self._cmd_load)
        self.register_command("debug", self._cmd_debug)
        self.register_command("debugger", self._cmd_debug)
        self.register_command("history", self._cmd_history)

    def register_command(self, name: str, func: Callable) -> None:
        """
        Register a custom command with the REPL.

        Custom commands are prefixed with % when used in the REPL.
        Example usage in REPL: %mycommand arg1 arg2

        Args:
            name: Command name (without the % prefix)
            func: Callable that will receive command arguments as string
        """
        self.custom_commands[name] = func

    def run(self) -> None:
        """Start the REPL loop."""
        # Set up signal handlers
        self._setup_signal_handlers()

        # Initialize readline with history and completion
        self._initialize_readline()

        # Display intro text if provided
        if self.intro:
            print(self.intro)

        self.running = True

        while self.running:
            try:
                # Read user input
                user_input = self._read_input()

                # Check if we have input to process
                if user_input is None:
                    continue

                # Process and evaluate input
                self._process_input(user_input)

            except KeyboardInterrupt:
                # Handle Ctrl+C gracefully
                print("\nKeyboardInterrupt")
                self.buffer = []
                continue

            except EOFError:
                # Handle Ctrl+D (EOF)
                print("\nExiting...")
                break

        # Clean up signal handlers before exit
        self._restore_signal_handlers()

    def _initialize_readline(self) -> None:
        """Initialize readline with history and completion."""
        # Try to load history file
        try:
            if os.path.exists(self.history_file):
                readline.read_history_file(self.history_file)

            # Set maximum number of history items
            readline.set_history_length(1000)

            # Register to save history on exit
            atexit.register(self._save_history)

            # Set basic tab completion for Python
            readline.parse_and_bind("tab: complete")

            # Set completion function
            readline.set_completer(self._completer)

        except (ImportError, AttributeError, IOError) as e:
            # Readline might not be available on all platforms
            print(f"Note: Command history disabled ({e.__class__.__name__})")

    def _save_history(self) -> None:
        """Save command history to file."""
        try:
            readline.write_history_file(self.history_file)
        except (ImportError, AttributeError, IOError):
            # Silently ignore errors when writing history
            pass

    def _completer(self, text: str, state: int) -> Optional[str]:
        """
        Custom completer function for readline.

        Completes:
        - Commands (when input starts with %)
        - Python identifiers from current context

        Args:
            text: The text to complete
            state: The state of completion (0 for first match, etc.)

        Returns:
            The completion or None if no more completions
        """
        if state == 0:
            # Initialize the completion list
            self._completion_matches = []

            # Check if completing a command
            if text.startswith("%"):
                cmd_text = text[1:]
                self._completion_matches = [f"%{cmd}" for cmd in self.custom_commands if cmd.startswith(cmd_text)]
            else:
                # Complete variables and functions in context
                for key in self.context:
                    if key.startswith(text):
                        self._completion_matches.append(key)

                # Add Python builtins
                for key in dir(__builtins__):
                    if key.startswith(text):
                        self._completion_matches.append(key)

            self._completion_matches.sort()

        # Return the appropriate completion or None if we've run out
        if state < len(self._completion_matches):
            return self._completion_matches[state]
        else:
            return None

    def _read_input(self) -> Optional[str]:
        """
        Read a line of input from the user.

        Returns:
            The input string or None if interrupted
        """
        try:
            # Use the appropriate prompt based on buffer state
            current_prompt = self.more_prompt if self.buffer else self.prompt
            return input(current_prompt)
        except KeyboardInterrupt:
            # Reset buffer on Ctrl+C
            self.buffer = []
            print("\nKeyboardInterrupt")
            return None
        except EOFError:
            # Exit on Ctrl+D by propagating exception to run()
            self.buffer = []  # Clear the buffer before exiting
            raise

    def _process_input(self, input_str: str) -> None:
        """
        Process a line of input, either as a command or as Python code.

        Args:
            input_str: The line of input to process
        """
        # Check for empty input
        if not input_str.strip():
            return

        # Check if input is a custom command
        if input_str.startswith("%") and not self.buffer:
            self._handle_command(input_str[1:])
            return

        # Add to our multiline buffer
        self.buffer.append(input_str)
        source = "\n".join(self.buffer)

        # Check if the code block is complete
        try:
            is_complete = code.compile_command(source) is not None
        except (SyntaxError, OverflowError, ValueError):
            # If there's a syntax error, execute to show the error
            is_complete = True

        if is_complete:
            # Execute the complete code block
            self._execute_code(source)
            self.buffer = []  # Reset buffer after execution

    def _handle_command(self, cmd_line: str) -> None:
        """
        Parse and handle a custom command.

        Args:
            cmd_line: Command string without the % prefix
        """
        # Parse command and arguments
        parts = cmd_line.strip().split(maxsplit=1)
        cmd_name = parts[0]
        cmd_args = parts[1] if len(parts) > 1 else ""

        # Check if the command exists
        if cmd_name in self.custom_commands:
            try:
                # Execute the command
                self.custom_commands[cmd_name](cmd_args)
            except (TypeError, ValueError, AttributeError, NameError, IndexError, KeyError) as e:
                print(f"Error executing command: {e}")
                traceback.print_exc()
        else:
            print(f"Unknown command: %{cmd_name}")

    def _execute_code(self, code_str: str) -> None:
        """
        Execute a block of Python code in the REPL context.

        Args:
            code_str: Python code to execute
        """
        try:
            # Check for common JavaScript-like syntax
            if code_str.lstrip().startswith(("const ", "let ", "var ")):
                print("JavaScript-like syntax detected. In Python, variables are declared without keywords:")
                js_var_type = code_str.lstrip().split()[0]
                example = code_str.replace(js_var_type, "", 1).strip()
                print(f"Instead of: {code_str}")
                print(f"Try: {example}")
                return

            # First try to eval (for expressions that return values)
            try:
                # SECURITY NOTE: eval is intentionally used here as part of the REPL functionality.
                # This is an essential feature of a Python REPL and cannot be avoided.
                # pylint: disable=eval-used
                result = eval(code_str, self.context)  # noqa: S307,DUO107,PGH001
                if result is not None:
                    print(repr(result))
            except SyntaxError:
                # If eval fails, try exec (for statements)
                # SECURITY NOTE: exec is intentionally used here as part of the REPL functionality.
                # This is an essential feature of a Python REPL and cannot be avoided.
                # pylint: disable=exec-used
                try:
                    exec(code_str, self.context)  # noqa: S307,DUO107,PGH001
                except SyntaxError as e:
                    # Handle syntax errors specifically
                    print(f"Syntax Error: {e}")
                    traceback.print_exc()
            except (NameError, TypeError, ValueError, AttributeError, IndexError, KeyError) as e:
                # Handle common user code errors specifically
                print(f"Error: {e.__class__.__name__}: {e}")
                traceback.print_exc()
        except Exception as e:  # noqa: BLE001,RUF100,PLR1702
            # This broad exception is necessary for a REPL to catch all possible
            # errors from user code without crashing the interpreter.
            # In a REPL context, we must handle any possible exception from user code.
            print(f"Error: {e.__class__.__name__}: {e}")
            traceback.print_exc()

    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful interruption."""
        # Store original handlers to restore later
        self._original_sigint = signal.getsignal(signal.SIGINT)
        self._original_sigterm = signal.getsignal(signal.SIGTERM)

        # Set custom handlers
        signal.signal(signal.SIGINT, self._handle_signal)
        signal.signal(signal.SIGTERM, self._handle_signal)

    def _restore_signal_handlers(self) -> None:
        """Restore original signal handlers."""
        signal.signal(signal.SIGINT, self._original_sigint)
        signal.signal(signal.SIGTERM, self._original_sigterm)

    def _handle_signal(self, sig: int, _frame=None) -> None:
        """
        Handle signals like SIGINT (Ctrl+C) and SIGTERM.

        Args:
            sig: Signal number
            _frame: Current stack frame (unused but required by signal handler API)
        """
        if sig == signal.SIGINT:
            # For SIGINT, just interrupt the current input
            raise KeyboardInterrupt

        if sig == signal.SIGTERM:
            # For SIGTERM, exit gracefully
            self.running = False
            print("\nReceived termination signal. Exiting...")

    # Built-in commands

    def _cmd_help(self, args: str) -> None:
        """Display help for available commands."""
        if not args:
            # Show general help
            print("Scriptic REPL Help:")
            print("  Enter Python code to execute it.")
            print("  Commands start with % and include:")

            for cmd in sorted(self.custom_commands.keys()):
                doc = self.custom_commands[cmd].__doc__
                desc = doc.split("\n")[0] if doc else "No description"
                print(f"  %{cmd:<10} {desc}")

            print("\nFor help on a specific command use: %help command")
            print("For help on a Python object use: help(object)")
        else:
            # Show help for a specific command
            cmd = args.strip()
            if cmd in self.custom_commands:
                doc = self.custom_commands[cmd].__doc__ or "No documentation available."
                print(f"Help for %{cmd}:\n{doc}")
            else:
                print(f"Unknown command: %{cmd}")

    def _cmd_exit(self, _args: str) -> None:
        """Exit the REPL."""
        self.running = False

    def _cmd_vars(self, _args: str) -> None:
        """Show variables in the current context."""
        # Filter out builtins and private variables
        user_vars = {k: v for k, v in self.context.items() if not k.startswith("_") and k not in dir(__builtins__)}

        if not user_vars:
            print("No variables defined.")
            return

        # Display variables and their types
        print("Variables in current context:")
        for name, value in sorted(user_vars.items()):
            print(f"  {name:<20} {type(value).__name__:<10} {repr(value)[:50]}")

    def _cmd_reset(self, args: str) -> None:
        """Reset the REPL context to initial state."""
        # Keep only the original injected context
        self.context.clear()
        self.context.update({} if args == "all" else {k: v for k, v in self.context.items() if not k.startswith("_")})
        print("Context reset.")

    def _cmd_run(self, args: str) -> None:
        """
        Execute a Python file in the current context.

        The file is executed and any definitions (functions, classes, variables)
        are added to the current REPL context, making them available for use.

        Usage: %run filename.py [arguments]
        """
        if not args:
            print("Usage: %run filename.py [arguments]")
            return

        # Parse filename and arguments
        parts = args.strip().split()
        filename = parts[0]
        script_args = parts[1:] if len(parts) > 1 else []

        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            return

        old_argv = None  # Initialize old_argv
        try:
            # Save original sys.argv and set new one for the script
            old_argv = sys.argv
            sys.argv = [filename] + script_args

            # Set __file__ in the context
            self.context["__file__"] = os.path.abspath(filename)

            # Read the file content
            with open(filename, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Compile and execute the file content
            print(f"Running '{filename}'...")

            try:
                # Compile the code to detect syntax errors
                compiled_code = compile(file_content, filename, "exec")
                # exec is necessary here to run user-provided scripts within the REPL context
                exec(compiled_code, self.context)  # noqa: S307,W0122
                print(f"Finished running '{filename}'")
            except SyntaxError as e:
                # Handle syntax errors found during compile
                print(f"Error executing '{filename}': Syntax error")
                print(f"Error details: {e}")
                traceback.print_exc()
            except Exception as e:  # noqa: W0718
                # Handle other runtime errors
                print(f"Error executing '{filename}': {e}")
                traceback.print_exc()

        except FileNotFoundError:
            print(f"Error: File '{filename}' not found during execution.")
        except OSError as e:
            print(f"Error reading file '{filename}': {e}")
            traceback.print_exc()
        except Exception as e:  # noqa: W0718
            # Catch any other exceptions to ensure they don't propagate out
            print(f"Unexpected error executing '{filename}': {e}")
            traceback.print_exc()
        finally:
            # Restore original sys.argv only if it was saved
            if old_argv is not None:
                sys.argv = old_argv

    def _cmd_load(self, args: str) -> None:
        """
        Load a Python file without executing it.

        This reads a Python file and displays its content without executing it.
        Useful for examining code before running it.

        Usage: %load filename.py
        """
        if not args:
            print("Usage: %load filename.py")
            return

        filename = args.strip()

        if not os.path.exists(filename):
            print(f"Error: File '{filename}' not found")
            return

        try:
            # Read the file content
            with open(filename, "r", encoding="utf-8") as f:
                file_content = f.read()

            # Add to the input buffer so it becomes part of the REPL history
            # and can be edited before execution
            lines = file_content.splitlines()
            self.buffer.extend(lines)

            # Print the loaded content
            print(f"Loaded '{filename}' into buffer:")
            for line in lines:
                print(f"{self.more_prompt}{line}")

        except Exception as e:  # noqa: W0718
            print(f"Error loading '{filename}': {e}")
            traceback.print_exc()

    # Add new debug command
    def _cmd_debug(self, args: str) -> None:  # pylint: disable=W1515
        """
        Start an interactive Python debugger session.

        This command starts a PDB (Python Debugger) session that allows you
        to debug the current state of the REPL. Use standard PDB commands
        within the debugger session.

        Common PDB commands:
        - h: help
        - n: next line
        - s: step into
        - c: continue
        - q: quit debugger
        - p <expr>: print expression

        Usage: %debug [expression]
        """
        print("Starting Python debugger (PDB)")
        print("Type 'h' for help, 'c' to continue back to REPL, 'q' to quit debugger")

        if args:
            try:
                # If args provided, evaluate expression in current context
                # and drop into debugger with the result
                # pylint: disable=W0123
                result = eval(args, self.context)  # noqa: W0123
                print(f"Debug expression result: {result}")
                pdb.set_trace()  # noqa: W1515
            except Exception as e:  # noqa: W0718
                print(f"Error evaluating debug expression: {e}")
                # Still start the debugger so user can inspect the state
                pdb.set_trace()  # noqa: W1515
        else:
            # Start debugger with current context
            pdb.set_trace()  # noqa: W1515

    def _cmd_history(self, args: str) -> None:
        """
        Display or manage command history.

        Usage:
            %history          - Show command history
            %history clear    - Clear history
            %history save     - Save history to file
            %history load     - Load history from file

        Command history is automatically saved between sessions when readline
        is available.
        """
        args = args.strip()

        if not args:
            # Display history
            try:
                history_length = readline.get_current_history_length()
                for i in range(1, history_length + 1):
                    item = readline.get_history_item(i)
                    if item and not item.startswith("%history"):
                        print(f"{i}: {item}")
            except (ImportError, AttributeError) as e:
                print(f"Error accessing history: {e}")
        elif args == "clear":
            # Clear history
            try:
                readline.clear_history()
                print("History cleared.")
            except (ImportError, AttributeError) as e:
                print(f"Error clearing history: {e}")
        elif args == "save":
            # Save history
            try:
                readline.write_history_file(self.history_file)
                print(f"History saved to {self.history_file}")
            except (ImportError, AttributeError, IOError) as e:
                print(f"Error saving history: {e}")
        elif args == "load":
            # Load history
            try:
                readline.read_history_file(self.history_file)
                print(f"History loaded from {self.history_file}")
            except (ImportError, AttributeError, IOError) as e:
                print(f"Error loading history: {e}")
        else:
            print("Unknown history command. Use: %history [clear|save|load]")


def run_scriptic(context: Optional[Dict[str, Any]] = None, prompt: str = ">>> ", more_prompt: str = "... ", intro: Optional[str] = None, history_file: Optional[str] = None) -> None:
    """
    Run a Scriptic REPL with the given context.

    This is a convenience function for quickly starting a REPL
    without needing to instantiate the Scriptic class directly.

    Args:
        context: Dictionary of objects to inject into REPL namespace
        prompt: Primary prompt string
        more_prompt: Continuation prompt for multiline input
        intro: Introduction text to display when REPL starts
        history_file: Path to the history file (None for default ~/.scriptic_history)
    """
    repl = Scriptic(context, prompt, more_prompt, intro, history_file)
    repl.run()


def run_cli():
    """
    Entry point for command-line usage.

    This function is called when running Scriptic as a command-line tool
    via the 'scriptic' command installed by pip.
    """
    parser = argparse.ArgumentParser(description="Scriptic: A minimalist embeddable Python REPL")
    parser.add_argument("script", nargs="?", help="Python script to load on startup")
    parser.add_argument("--no-intro", action="store_true", help="Skip the intro message")
    parser.add_argument("--prompt", default=">>> ", help="Custom prompt string")
    parser.add_argument("--history-file", help="Custom history file location")
    parser.add_argument("--no-history", action="store_true", help="Disable command history")

    args = parser.parse_args()

    # Get local context from script or empty
    context = {}
    if args.script:
        try:
            with open(args.script, "r", encoding="utf-8") as f:
                script_content = f.read()
            # Execute the script and capture its globals
            # NOTE: exec is intentionally used here to load user scripts into the REPL context
            exec(script_content, context)  # noqa: S307,W0122
            print(f"Loaded script: {args.script}")
        except FileNotFoundError:
            print(f"Script not found: {args.script}")
            traceback.print_exc()
        except SyntaxError as e:
            print(f"Syntax error in script: {e}")
            traceback.print_exc()
        except OSError as e:
            print(f"Error reading script: {e}")
            traceback.print_exc()
        except Exception as e:  # noqa: W0718
            # This broader exception handles other runtime errors in user scripts
            print(f"Error executing script: {e}")
            traceback.print_exc()

    # Determine history file
    history_file = None if args.no_history else args.history_file

    # Start the REPL
    intro = None if args.no_intro else "Scriptic REPL - Type Python code or %help for commands"
    run_scriptic(context=context, prompt=args.prompt, intro=intro, history_file=history_file)


if __name__ == "__main__":
    # If run as a script, start a basic REPL
    run_cli()
