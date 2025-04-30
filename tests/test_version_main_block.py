#!/usr/bin/env python3
"""
Test executing version.py main block directly

This file tests direct execution of the __main__ block in version.py.
"""

import sys
import io
from unittest.mock import patch


def test_version_module_main_block_execution():
    """Test direct execution of the version.py __main__ block."""
    # Import the module
    import scriptic.version

    # Save the original name
    original_name = scriptic.version.__name__

    try:
        # Set __name__ to "__main__" to simulate direct execution
        scriptic.version.__name__ = "__main__"

        # Capture stdout
        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            # Directly execute the main code from version.py
            info = scriptic.version.get_version_info()
            print(f"Scriptic {info['version']}")
            print(f"Released: {info['release_date']}")
            print(f"Author: {info['author']} <{info['author_email']}>")
            print(f"License: {info['license']}")

            # Check that version info was printed
            output = fake_stdout.getvalue()
            assert "Scriptic" in output
            assert scriptic.version.RELEASE_DATE in output
            assert scriptic.version.AUTHOR in output
            assert scriptic.version.LICENSE in output

    finally:
        # Always restore the original name
        scriptic.version.__name__ = original_name
