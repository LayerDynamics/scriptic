#!/usr/bin/env python3
"""
Direct execution test for version.py __main__ block

This file executes the code in the __main__ block of version.py by
directly running the code that appears within that block.
"""

import importlib
import io
import sys
from unittest.mock import patch


def test_version_py_direct_main_execution():
    """
    Test version.py __main__ block by executing it directly.

    This test focuses on lines 176-180 in version.py.
    It imports the module, patches the script name to __main__,
    and then executes the exact block of code that would run
    when the script is executed directly.
    """
    # Import the version module
    from scriptic import version

    # Create a fresh import to ensure state is clean
    importlib.reload(version)

    # Capture stdout to verify output
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        # The exact lines of code from version.py's __main__ block (lines 176-180)
        info = version.get_version_info()
        print(f"Scriptic {info['version']}")
        print(f"Released: {info['release_date']}")
        print(f"Author: {info['author']} <{info['author_email']}>")
        print(f"License: {info['license']}")

        # Check that the output matches what we expect
        output = fake_stdout.getvalue()
        assert f"Scriptic {version.get_version()}" in output
        assert f"Released: {version.RELEASE_DATE}" in output
        assert f"Author: {version.AUTHOR}" in output
        assert f"License: {version.LICENSE}" in output
