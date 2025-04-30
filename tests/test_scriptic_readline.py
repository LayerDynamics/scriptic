#!/usr/bin/env python3
"""
Unit tests for Scriptic readline functionality

This module contains tests for the readline integration, history management,
and tab completion functionality of Scriptic.
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch, MagicMock, call
import io
import pytest
from scriptic import Scriptic


class ScripticReadlineTestCase(unittest.TestCase):
    """Test cases for Scriptic's readline integration."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_dir = tempfile.TemporaryDirectory()
        self.history_file = os.path.join(self.test_dir.name, "test_history")
        self.context = {}
        self.repl = Scriptic(self.context, history_file=self.history_file)

    def tearDown(self):
        """Clean up test fixtures."""
        self.test_dir.cleanup()

    def test_initialize_readline(self):
        """Test readline initialization."""
        with patch("readline.read_history_file") as mock_read:
            with patch("readline.set_history_length") as mock_set_length:
                with patch("atexit.register") as mock_atexit:
                    with patch("readline.parse_and_bind") as mock_parse:
                        with patch("readline.set_completer") as mock_set_completer:
                            # Create a new repl to ensure fresh readline setup
                            repl = Scriptic(self.context, history_file=self.history_file)
                            repl._initialize_readline()

                            # Verify all expected readline methods are called
                            mock_set_length.assert_called_with(1000)
                            mock_atexit.assert_called_once()
                            mock_parse.assert_called_with("tab: complete")
                            mock_set_completer.assert_called_once()

    def test_initialize_readline_no_history_file(self):
        """Test readline initialization when history file doesn't exist."""
        nonexistent_history = os.path.join(self.test_dir.name, "nonexistent")

        # Ensure the file doesn't exist
        if os.path.exists(nonexistent_history):
            os.remove(nonexistent_history)

        with patch("readline.read_history_file") as mock_read:
            with patch("readline.set_history_length"):
                with patch("atexit.register"):
                    with patch("readline.parse_and_bind"):
                        with patch("readline.set_completer"):
                            # Create a new repl with a nonexistent history file
                            repl = Scriptic(self.context, history_file=nonexistent_history)
                            repl._initialize_readline()

                            # read_history_file should not be called since file doesn't exist
                            mock_read.assert_not_called()

    def test_initialize_readline_error(self):
        """Test readline initialization when readline raises an error."""
        with patch("os.path.exists", return_value=True):
            with patch("readline.read_history_file", side_effect=ImportError("Test error")):
                with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                    # Create a new repl to trigger readline initialization
                    repl = Scriptic(self.context, history_file=self.history_file)
                    repl._initialize_readline()

                    # Verify error message
                    output = fake_stdout.getvalue()
                    self.assertIn("Command history disabled", output)
                    self.assertIn("ImportError", output)

    def test_save_history(self):
        """Test history saving."""
        with patch("readline.write_history_file") as mock_write:
            self.repl._save_history()
            mock_write.assert_called_once_with(self.history_file)

    def test_save_history_error(self):
        """Test history saving when readline raises an error."""
        with patch("readline.write_history_file", side_effect=ImportError("Test error")):
            # Should not raise an exception
            try:
                self.repl._save_history()
                passed = True
            except Exception:
                passed = False

            self.assertTrue(passed, "History saving should handle errors gracefully")

    def test_completer_commands(self):
        """Test tab completion for commands."""
        # Add a test command
        self.repl.register_command("test_cmd", lambda x: None)

        # Test completion for %test - first call (state=0)
        result = self.repl._completer("%test", 0)
        self.assertEqual(result, "%test_cmd")

        # Test completion for %test - second call (state=1)
        result = self.repl._completer("%test", 1)
        self.assertIsNone(result, "No more completions should be available")

    def test_completer_variables(self):
        """Test tab completion for variables and builtins."""
        # Add a test variable
        self.repl.context["test_var"] = 42
        
        # Add 'print' function to context to ensure it's available for completion
        self.repl.context["print"] = print
        
        # Test completion for test_ - first call (state=0)
        result = self.repl._completer("test_", 0)
        self.assertEqual(result, "test_var")
        
        # Test completion for test_ - second call (state=1)
        result = self.repl._completer("test_", 1)
        self.assertIsNone(result, "No more completions should be available")
        
        # Test completion for pri (should match print function) - first call
        result = self.repl._completer("pri", 0)
        self.assertEqual(result, "print")

    def test_completer_no_matches(self):
        """Test tab completion when no matches are found."""
        # Test completion for xyz (no matches) - first call
        result = self.repl._completer("xyz_no_match", 0)
        self.assertIsNone(result, "No completions should be available")

    def test_cmd_history_display(self):
        """Test %history command (display)."""
        # Mock readline.get_current_history_length to return 3
        with patch("readline.get_current_history_length", return_value=3):
            # Mock readline.get_history_item to return test items
            with patch("readline.get_history_item", side_effect=["test1", "test2", "%history"]):
                with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                    # Call the history command
                    self.repl._cmd_history("")

                    # Verify output
                    output = fake_stdout.getvalue()
                    self.assertIn("1: test1", output)
                    self.assertIn("2: test2", output)
                    self.assertNotIn("%history", output)  # Should be filtered out

    def test_cmd_history_display_error(self):
        """Test %history command when readline raises an error."""
        with patch("readline.get_current_history_length", side_effect=ImportError("Test error")):
            with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                # Call the history command
                self.repl._cmd_history("")

                # Verify error message
                output = fake_stdout.getvalue()
                self.assertIn("Error accessing history", output)
                self.assertIn("Test error", output)  # Check for error message instead of exception type

    def test_cmd_history_clear(self):
        """Test %history clear command."""
        with patch("readline.clear_history") as mock_clear:
            with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                # Call the history clear command
                self.repl._cmd_history("clear")

                # Verify call and output
                mock_clear.assert_called_once()
                output = fake_stdout.getvalue()
                self.assertIn("History cleared", output)

    def test_cmd_history_clear_error(self):
        """Test %history clear command when readline raises an error."""
        with patch("readline.clear_history", side_effect=ImportError("Test error")):
            with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                # Call the history clear command
                self.repl._cmd_history("clear")

                # Verify error message
                output = fake_stdout.getvalue()
                self.assertIn("Error clearing history", output)
                self.assertIn("Test error", output)  # Check for error message instead of exception type

    def test_cmd_history_save(self):
        """Test %history save command."""
        with patch("readline.write_history_file") as mock_write:
            with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                # Call the history save command
                self.repl._cmd_history("save")

                # Verify call and output
                mock_write.assert_called_once_with(self.history_file)
                output = fake_stdout.getvalue()
                self.assertIn("History saved to", output)

    def test_cmd_history_save_error(self):
        """Test %history save command when readline raises an error."""
        with patch("readline.write_history_file", side_effect=ImportError("Test error")):
            with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                # Call the history save command
                self.repl._cmd_history("save")

                # Verify error message
                output = fake_stdout.getvalue()
                self.assertIn("Error saving history", output)
                self.assertIn("Test error", output)  # Check for error message instead of exception type

    def test_cmd_history_load(self):
        """Test %history load command."""
        with patch("readline.read_history_file") as mock_read:
            with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                # Call the history load command
                self.repl._cmd_history("load")

                # Verify call and output
                mock_read.assert_called_once_with(self.history_file)
                output = fake_stdout.getvalue()
                self.assertIn("History loaded from", output)

    def test_cmd_history_load_error(self):
        """Test %history load command when readline raises an error."""
        with patch("readline.read_history_file", side_effect=ImportError("Test error")):
            with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
                # Call the history load command
                self.repl._cmd_history("load")

                # Verify error message
                output = fake_stdout.getvalue()
                self.assertIn("Error loading history", output)
                self.assertIn("Test error", output)  # Check for error message instead of exception type

    def test_cmd_history_unknown(self):
        """Test %history with unknown subcommand."""
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            # Call the history with unknown subcommand
            self.repl._cmd_history("unknown")

            # Verify error message
            output = fake_stdout.getvalue()
            self.assertIn("Unknown history command", output)

    def test_javascript_syntax_detection(self):
        """Test detection of JavaScript-like syntax."""
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            # Execute JavaScript-like code
            self.repl._execute_code("const x = 10")

            # Verify helpful message
            output = fake_stdout.getvalue()
            self.assertIn("JavaScript-like syntax detected", output)
            self.assertIn("const x = 10", output)
            self.assertIn("x = 10", output)  # Suggested Python equivalent


# Pytest-specific tests
@pytest.fixture
def history_file():
    """Fixture to create a temporary history file."""
    test_dir = tempfile.TemporaryDirectory()
    history_path = os.path.join(test_dir.name, "test_history")

    yield history_path

    test_dir.cleanup()


def test_scriptic_with_custom_history_file(history_file):
    """Test creating a Scriptic instance with a custom history file."""
    repl = Scriptic(history_file=history_file)
    assert repl.history_file == history_file


def test_scriptic_with_no_history_file():
    """Test creating a Scriptic instance with history disabled."""
    repl = Scriptic(history_file=None)
    assert repl.history_file.endswith(".scriptic_history")


def test_run_cli_with_history_options():
    """Test run_cli with history options."""
    # Test with custom history file
    test_history = "/tmp/custom_history"

    with patch("sys.argv", ["scriptic", "--history-file", test_history]):
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.script = None
        mock_args.history_file = test_history
        mock_args.no_history = False
        mock_parser.parse_args.return_value = mock_args

        with patch("scriptic.scriptic.argparse.ArgumentParser", return_value=mock_parser):
            with patch("scriptic.scriptic.run_scriptic") as mock_run_scriptic:
                # Run CLI
                from scriptic import run_cli

                run_cli()

                # Verify history_file was passed correctly
                assert mock_run_scriptic.call_args[1]["history_file"] == test_history

    # Test with no history
    with patch("sys.argv", ["scriptic", "--no-history"]):
        mock_parser = MagicMock()
        mock_args = MagicMock()
        mock_args.script = None
        mock_args.history_file = None
        mock_args.no_history = True
        mock_parser.parse_args.return_value = mock_args

        with patch("scriptic.scriptic.argparse.ArgumentParser", return_value=mock_parser):
            with patch("scriptic.scriptic.run_scriptic") as mock_run_scriptic:
                # Run CLI
                run_cli()

                # Verify history_file is None
                assert mock_run_scriptic.call_args[1]["history_file"] is None
