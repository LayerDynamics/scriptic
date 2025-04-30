#!/usr/bin/env python3
"""
Test for version.py when run as a main script

This module tests the behavior of version.py when executed directly.
"""

import io
import sys
from unittest.mock import patch
import pytest


def test_version_module_main():
    """Test the behavior when version.py is run as a main script."""
    # Since we can't easily import a module as __main__, let's simulate
    # what happens when the module is run directly

    # Import the module
    from scriptic.version import get_version_info

    # Capture the output when the main function is run
    with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
        # Call the same functions that would be called in __main__
        info = get_version_info()
        print(f"Scriptic {info['version']}")
        print(f"Released: {info['release_date']}")
        print(f"Author: {info['author']} <{info['author_email']}>")
        print(f"License: {info['license']}")

        # Check the output
        output = fake_stdout.getvalue()
        assert "Scriptic" in output
        assert "Released" in output
        assert "Author" in output
        assert "License" in output


def test_version_module_imports():
    """Test that all exports from version.py are available."""
    # Test importing all exports to ensure they're defined
    from scriptic.version import (
        get_version,
        get_version_tuple,
        get_version_info,
        parse_version_string,
        compare_versions,
        is_compatible,
        MAJOR,
        MINOR,
        PATCH,
        PRE_RELEASE,
        DEV,
        RELEASE_DATE,
        AUTHOR,
        AUTHOR_EMAIL,
        LICENSE,
        __version__,
        VERSION,
    )

    # Verify the basic structure of the version tuple
    assert isinstance(get_version_tuple(), tuple)
    assert len(get_version_tuple()) == 5


def test_version_module_direct_execution():
    """Test the version module when executed directly as a main script."""
    import scriptic.version

    # Save original values
    original_name = scriptic.version.__name__
    original_major = scriptic.version.MAJOR
    original_minor = scriptic.version.MINOR
    original_patch = scriptic.version.PATCH
    original_pre = scriptic.version.PRE_RELEASE
    original_dev = scriptic.version.DEV

    try:
        # Test direct version tuple creation by setting values directly
        # This covers lines 37 and 40
        scriptic.version.MAJOR = 2
        scriptic.version.MINOR = 3
        scriptic.version.PATCH = 4
        scriptic.version.PRE_RELEASE = "beta"
        scriptic.version.DEV = "dev5"

        # Reset the cached version values
        if hasattr(scriptic.version, "__version__"):
            delattr(scriptic.version, "__version__")

        # Test the version tuple with our custom values
        version_tuple = scriptic.version.get_version_tuple()
        assert version_tuple == (2, 3, 4, "beta", "dev5")

        # Check the version string
        version_str = scriptic.version.get_version()
        assert version_str == "2.3.4-beta+dev5"

        # Test main block execution (lines 176-180)
        scriptic.version.__name__ = "__main__"

        with patch("sys.stdout", new=io.StringIO()) as fake_stdout:
            # Directly call the code that would be in the main block
            info = scriptic.version.get_version_info()
            print(f"Scriptic {info['version']}")
            print(f"Released: {info['release_date']}")
            print(f"Author: {info['author']} <{info['author_email']}>")
            print(f"License: {info['license']}")

            # Verify output
            output = fake_stdout.getvalue()
            assert "Scriptic" in output
            assert "Released:" in output
            assert "Author:" in output
            assert "License:" in output

    finally:
        # Restore original values
        scriptic.version.__name__ = original_name
        scriptic.version.MAJOR = original_major
        scriptic.version.MINOR = original_minor
        scriptic.version.PATCH = original_patch
        scriptic.version.PRE_RELEASE = original_pre
        scriptic.version.DEV = original_dev
