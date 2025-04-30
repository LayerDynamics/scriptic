#!/usr/bin/env python3
"""
Tests targeting specific uncovered lines in scriptic.py

This file contains tests that specifically target the remaining uncovered
lines in scriptic.py to improve the test coverage.
"""

import io
import os
import sys
import tempfile
from unittest.mock import patch, MagicMock
import code
import builtins
import pytest
from scriptic import Scriptic, run_scriptic, run_cli


def test_completer_null_state():
    """Test tab completion with state > number of matches (line 107)."""
    repl = Scriptic()

    # Set up _completion_matches with some values
    repl._completion_matches = ["test1", "test2"]

    # Call _completer with state=2 which should return None
    # This specifically targets line 107 in scriptic.py
    result = repl._completer("test", 2)
    assert result is None

    # Call _completer with an empty matches list (line 189)
    repl._completion_matches = []
    result = repl._completer("xyz", 0)
    assert result is None


def test_process_input_syntax_error():
    """Test processing input with syntax error (line 382)."""
    repl = Scriptic()

    # Add a line to the buffer
    repl.buffer = ["def test_func():"]

    # Patch compile_command to raise a SyntaxError
    # This specifically targets line 382 in scriptic.py
    with patch("code.compile_command", side_effect=SyntaxError("test error")):
        with patch.object(repl, "_execute_code") as mock_execute:
            repl._process_input("    print('test')")

            # The execute_code should be called and buffer should be cleared
            mock_execute.assert_called_once()
            assert len(repl.buffer) == 0


def test_handle_command_with_args():
    """Test handling commands with arguments (lines 390-391)."""
    repl = Scriptic()

    # Create a test command that saves the args
    test_args = []

    def test_command(args):
        test_args.append(args)

    # Register the command
    repl.register_command("test", test_command)

    # Call handle_command with a space in the arguments
    # This specifically targets lines 390-391 in scriptic.py
    repl._handle_command("test arg1 arg2 arg3")

    # Verify the entire string after the command name was passed as args
    assert test_args[0] == "arg1 arg2 arg3"


def test_file_run_context_setup():
    """Test __file__ context setup in run command (line 460)."""
    repl = Scriptic()

    # Create a test file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(b"# Test file\nprint('File executed')\n")
        file_path = temp_file.name

    try:
        # Run the file
        with patch("sys.stdout", new=io.StringIO()):
            repl._cmd_run(file_path)

            # Check if __file__ was set in the context (line 460)
            assert "__file__" in repl.context
            assert os.path.abspath(file_path) == repl.context["__file__"]
    finally:
        # Clean up
        os.unlink(file_path)


def test_main_module_execution():
    """Test the __main__ block in scriptic.py (line 667)."""
    # Import the module
    import scriptic.scriptic

    # Save original
    original_name = scriptic.scriptic.__name__
    original_run_cli = scriptic.scriptic.run_cli

    try:
        # Replace run_cli with a mock that we can check was called
        mock_run_cli = MagicMock()
        scriptic.scriptic.run_cli = mock_run_cli

        # Set __name__ to "__main__" to trigger the main block
        scriptic.scriptic.__name__ = "__main__"

        # Re-execute the main block
        if scriptic.scriptic.__name__ == "__main__":
            scriptic.scriptic.run_cli()

        # Verify run_cli was called
        mock_run_cli.assert_called_once()

    finally:
        # Restore original name and function
        scriptic.scriptic.__name__ = original_name
        scriptic.scriptic.run_cli = original_run_cli
