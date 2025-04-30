#!/usr/bin/env python3
"""
Additional unit tests for Scriptic version module

This module provides additional tests to increase coverage of the version.py module.
"""

import pytest
import re
import sys
from unittest.mock import patch, MagicMock
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
    __version__,
    VERSION,
)


def test_version_edge_cases():
    """Test version comparisons with various edge cases."""
    # Test a version with both pre-release and dev
    version_with_both = "1.0.0-beta+dev1"
    parsed = parse_version_string(version_with_both)
    assert parsed == (1, 0, 0, "beta", "dev1")
    
    # Test different dev versions
    assert compare_versions("1.0.0+dev1", "1.0.0+dev2") == -1
    assert compare_versions("1.0.0+dev2", "1.0.0+dev1") == 1
    
    # Test different pre-release versions
    assert compare_versions("1.0.0-alpha", "1.0.0-beta") == -1
    assert compare_versions("1.0.0-beta", "1.0.0-alpha") == 1
    
    # Test pre-release vs none
    assert compare_versions("1.0.0-alpha", "1.0.0") == -1
    assert compare_versions("1.0.0", "1.0.0-alpha") == 1
    
    # Test dev vs none
    assert compare_versions("1.0.0+dev", "1.0.0") == -1
    assert compare_versions("1.0.0", "1.0.0+dev") == 1
    
    # Test with pre-release and dev in both versions
    assert compare_versions("1.0.0-alpha+dev1", "1.0.0-alpha+dev2") == -1
    assert compare_versions("1.0.0-alpha+dev1", "1.0.0-beta+dev1") == -1


def test_version_equality():
    """Test equal versions."""
    # Equal versions
    assert compare_versions("1.0.0", "1.0.0") == 0
    assert compare_versions("1.0.0-alpha", "1.0.0-alpha") == 0
    assert compare_versions("1.0.0+dev1", "1.0.0+dev1") == 0
    assert compare_versions("1.0.0-alpha+dev1", "1.0.0-alpha+dev1") == 0


def test_version_different_segments():
    """Test version comparison when different segments matter."""
    # Test major version differences
    assert compare_versions("2.0.0", "1.0.0") == 1
    assert compare_versions("1.0.0", "2.0.0") == -1
    
    # Test minor version differences
    assert compare_versions("1.2.0", "1.1.0") == 1
    assert compare_versions("1.1.0", "1.2.0") == -1
    
    # Test patch version differences
    assert compare_versions("1.1.2", "1.1.1") == 1
    assert compare_versions("1.1.1", "1.1.2") == -1


def test_is_compatible_edge_cases():
    """Test compatibility check with edge cases."""
    # When MAJOR is 0, no version is compatible
    with patch("scriptic.version.MAJOR", 0):
        assert is_compatible("0.1.0") is True
        assert is_compatible("1.0.0") is False
    
    # When MAJOR is not 0
    with patch("scriptic.version.MAJOR", 1):
        assert is_compatible("1.0.0") is True
        assert is_compatible("1.1.0") is True
        assert is_compatible("1.0.1") is True
        assert is_compatible("2.0.0") is False
        assert is_compatible("0.1.0") is False
    
    # Test with invalid version string
    assert is_compatible("not.a.version") is False
    assert is_compatible("") is False


def test_direct_version_string_creation():
    """Test direct creation of version string with different component values."""
    # Test with no PRE_RELEASE or DEV
    with patch("scriptic.version.MAJOR", 1):
        with patch("scriptic.version.MINOR", 2):
            with patch("scriptic.version.PATCH", 3):
                with patch("scriptic.version.PRE_RELEASE", None):
                    with patch("scriptic.version.DEV", None):
                        assert get_version() == "1.2.3"
    
    # Test with PRE_RELEASE only
    with patch("scriptic.version.MAJOR", 1):
        with patch("scriptic.version.MINOR", 2):
            with patch("scriptic.version.PATCH", 3):
                with patch("scriptic.version.PRE_RELEASE", "alpha"):
                    with patch("scriptic.version.DEV", None):
                        assert get_version() == "1.2.3-alpha"
    
    # Test with DEV only
    with patch("scriptic.version.MAJOR", 1):
        with patch("scriptic.version.MINOR", 2):
            with patch("scriptic.version.PATCH", 3):
                with patch("scriptic.version.PRE_RELEASE", None):
                    with patch("scriptic.version.DEV", "dev1"):
                        assert get_version() == "1.2.3+dev1"
    
    # Test with both PRE_RELEASE and DEV
    with patch("scriptic.version.MAJOR", 1):
        with patch("scriptic.version.MINOR", 2):
            with patch("scriptic.version.PATCH", 3):
                with patch("scriptic.version.PRE_RELEASE", "beta"):
                    with patch("scriptic.version.DEV", "dev2"):
                        assert get_version() == "1.2.3-beta+dev2"


def test_version_import_and_constants():
    """Test version module imports and constants."""
    # Make sure constants are of correct type
    assert isinstance(MAJOR, int)
    assert isinstance(MINOR, int)
    assert isinstance(PATCH, int)
    
    # PRE_RELEASE and DEV can be None or str
    assert isinstance(PRE_RELEASE, (type(None), str))
    assert isinstance(DEV, (type(None), str))
    
    # Make sure version values are consistent
    assert VERSION == __version__
    assert __version__ == get_version()
    assert get_version_tuple() == (MAJOR, MINOR, PATCH, PRE_RELEASE, DEV)
    
    # Test version info dict
    info = get_version_info()
    assert "version" in info
    assert "major" in info
    assert "minor" in info
    assert "patch" in info
    assert "pre_release" in info
    assert "dev" in info
    assert "release_date" in info
    assert "author" in info
    assert "author_email" in info
    assert "license" in info


if __name__ == "__main__":
    pytest.main(["-v", __file__])