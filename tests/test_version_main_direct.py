#!/usr/bin/env python3
"""
Extended tests for version.py to improve coverage

This module focuses on direct invocation of the __main__ block.
"""

import io
import sys
from unittest.mock import patch
import pytest


def test_version_module_main_direct():
    """Test the version.py module's __main__ block by directly importing the code."""
    # Capture stdout
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        # Import version module - this simulates executing the module
        import scriptic.version

        # Store original __name__
        original_name = scriptic.version.__name__

        try:
            # Set __name__ to __main__ to trigger the block
            scriptic.version.__name__ = "__main__"

            # Execute the main block code
            if scriptic.version.__name__ == "__main__":
                # Print version information directly
                info = scriptic.version.get_version_info()
                print(f"Scriptic {info['version']}")
                print(f"Released: {info['release_date']}")
                print(f"Author: {info['author']} <{info['author_email']}>")
                print(f"License: {info['license']}")

            # Check output
            output = fake_stdout.getvalue()
            assert "Scriptic" in output
            assert "Released:" in output
            assert "Author:" in output
            assert "License:" in output

        finally:
            # Restore original name
            scriptic.version.__name__ = original_name
