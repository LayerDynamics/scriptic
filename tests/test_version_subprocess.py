#!/usr/bin/env python3
"""
Execute version.py directly as a script to test the __main__ block

This module uses subprocess to execute version.py directly as a script,
which is the most accurate way to test the __main__ block execution.
"""

import os
import sys
import subprocess
from unittest.mock import patch
import pytest


def test_version_py_subprocess_execution():
    """
    Test version.py's __main__ block by running it directly as a script.

    This test uses subprocess to run the version.py file directly as a script,
    which ensures the __main__ block is executed in exactly the same way as
    it would be when run from the command line.
    """
    # Get the path to the version.py script
    from scriptic import version

    script_path = os.path.abspath(version.__file__)

    # Use subprocess to run the script directly
    result = subprocess.run([sys.executable, script_path], capture_output=True, text=True, check=True)

    # Verify the output contains the expected version information
    assert f"Scriptic {version.get_version()}" in result.stdout
    assert f"Released: {version.RELEASE_DATE}" in result.stdout
    assert f"Author: {version.AUTHOR}" in result.stdout
    assert f"License: {version.LICENSE}" in result.stdout
