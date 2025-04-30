#!/usr/bin/env python3
"""
Unit tests for Scriptic version module

This module contains tests for version.py functionality including version parsing,
comparison, and compatibility checking.
"""

import unittest
import re
import pytest
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


class VersionTestCase(unittest.TestCase):
    """Test cases for version-related functions."""

    def test_get_version(self):
        """Test get_version function."""
        version = get_version()
        expected_pattern = r"^\d+\.\d+\.\d+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$"
        self.assertTrue(re.match(expected_pattern, version), f"Version {version} does not match expected format")

    def test_get_version_tuple(self):
        """Test get_version_tuple function."""
        version_tuple = get_version_tuple()
        self.assertEqual(len(version_tuple), 5)
        self.assertEqual(version_tuple[0], MAJOR)
        self.assertEqual(version_tuple[1], MINOR)
        self.assertEqual(version_tuple[2], PATCH)
        self.assertEqual(version_tuple[3], PRE_RELEASE)
        self.assertEqual(version_tuple[4], DEV)

    def test_get_version_info(self):
        """Test get_version_info function."""
        info = get_version_info()
        self.assertEqual(info["version"], get_version())
        self.assertEqual(info["major"], MAJOR)
        self.assertEqual(info["minor"], MINOR)
        self.assertEqual(info["patch"], PATCH)
        self.assertEqual(info["pre_release"], PRE_RELEASE)
        self.assertEqual(info["dev"], DEV)
        self.assertEqual(info["release_date"], RELEASE_DATE)
        self.assertEqual(info["author"], AUTHOR)
        self.assertEqual(info["author_email"], AUTHOR_EMAIL)
        self.assertEqual(info["license"], LICENSE)

    def test_parse_version_string_valid(self):
        """Test parse_version_string with valid inputs."""
        test_cases = [
            ("1.2.3", (1, 2, 3, None, None)),
            ("0.1.0", (0, 1, 0, None, None)),
            ("1.2.3-alpha", (1, 2, 3, "alpha", None)),
            ("1.2.3+dev1", (1, 2, 3, None, "dev1")),
            ("1.2.3-beta+dev2", (1, 2, 3, "beta", "dev2")),
        ]

        for version_str, expected in test_cases:
            with self.subTest(version_str=version_str):
                result = parse_version_string(version_str)
                self.assertEqual(result, expected)

    def test_parse_version_string_invalid(self):
        """Test parse_version_string with invalid inputs."""
        invalid_versions = [
            "1.2",  # Missing patch version
            "1.2.x",  # Non-numeric patch
            "1.2.3.4",  # Too many segments
            "v1.2.3",  # Prefix not allowed
            "1,2,3",  # Wrong separator
            "version 1.2.3",  # Extra text
            "",  # Empty string
            "abc",  # Non-version string
        ]

        for invalid_version in invalid_versions:
            with self.subTest(version=invalid_version):
                with self.assertRaises(ValueError):
                    parse_version_string(invalid_version)

    def test_compare_versions(self):
        """Test compare_versions function."""
        test_cases = [
            # Basic comparisons
            ("1.2.3", "1.2.3", 0),  # Equal
            ("1.2.3", "1.2.4", -1),  # Patch version different
            ("1.2.4", "1.2.3", 1),
            ("1.2.3", "1.3.3", -1),  # Minor version different
            ("1.3.3", "1.2.3", 1),
            ("1.2.3", "2.2.3", -1),  # Major version different
            ("2.2.3", "1.2.3", 1),
            # With pre-release versions
            ("1.2.3-alpha", "1.2.3", -1),  # Pre-release < release
            ("1.2.3", "1.2.3-alpha", 1),  # Release > pre-release
            ("1.2.3-alpha", "1.2.3-beta", -1),  # Alpha < beta
            ("1.2.3-beta", "1.2.3-alpha", 1),  # Beta > alpha
            # With dev versions
            ("1.2.3+dev1", "1.2.3", -1),  # Dev < release
            ("1.2.3", "1.2.3+dev1", 1),  # Release > dev
            ("1.2.3+dev1", "1.2.3+dev2", -1),  # Dev1 < dev2
            ("1.2.3+dev2", "1.2.3+dev1", 1),  # Dev2 > dev1
            # Combined cases
            ("1.2.3-alpha+dev1", "1.2.3-alpha", -1),  # Pre-release with dev < pre-release
            ("1.2.3-alpha", "1.2.3-alpha+dev1", 1),
        ]

        for v1, v2, expected in test_cases:
            with self.subTest(v1=v1, v2=v2):
                result = compare_versions(v1, v2)
                self.assertEqual(result, expected)

    def test_is_compatible(self):
        """Test is_compatible function."""
        # Mock MAJOR to ensure consistent testing
        original_major = MAJOR

        try:
            # Create test data that will work regardless of the actual MAJOR value
            compatible_versions = [
                f"{MAJOR}.0.0",
                f"{MAJOR}.1.0",
                f"{MAJOR}.0.1",
                f"{MAJOR}.99.99",
                f"{MAJOR}.0.0-alpha",
                f"{MAJOR}.0.0+dev1",
            ]

            incompatible_versions = [
                # This will always be incompatible
                f"{MAJOR + 1}.0.0",
            ]

            # If MAJOR > 0, we can test a lower version
            if MAJOR > 0:
                incompatible_versions.append(f"{MAJOR - 1}.0.0")

            # Invalid version format
            invalid_version = "invalid-version"

            # Test compatible versions
            for version in compatible_versions:
                with self.subTest(version=version):
                    self.assertTrue(is_compatible(version))

            # Test incompatible versions
            for version in incompatible_versions:
                with self.subTest(version=version):
                    self.assertFalse(is_compatible(version))

            # Test invalid version format
            self.assertFalse(is_compatible(invalid_version))

        finally:
            # Restore original value if needed
            if "MAJOR" in globals():
                globals()["MAJOR"] = original_major

    def test_version_constants(self):
        """Test version constants."""
        self.assertIsInstance(MAJOR, int)
        self.assertIsInstance(MINOR, int)
        self.assertIsInstance(PATCH, int)
        self.assertIsInstance(RELEASE_DATE, str)

        # PRE_RELEASE and DEV can be None or string
        if PRE_RELEASE is not None:
            self.assertIsInstance(PRE_RELEASE, str)
        if DEV is not None:
            self.assertIsInstance(DEV, str)

        self.assertEqual(__version__, get_version())
        self.assertEqual(VERSION, __version__)


# Pytest-specific tests
def test_version_string_matches_components():
    """Test that the version string matches the components using pytest."""
    version = get_version()
    version_parts = version.split(".")

    assert int(version_parts[0]) == MAJOR
    assert int(version_parts[1]) == MINOR

    # Handle patch version which might contain pre-release or dev suffix
    patch_part = version_parts[2]
    if "-" in patch_part:
        patch, remainder = patch_part.split("-", 1)
        assert int(patch) == PATCH

        # Handle dev suffix in pre-release
        if "+" in remainder:
            pre_release, dev = remainder.split("+", 1)
            assert pre_release == PRE_RELEASE
            assert dev == DEV
        else:
            assert remainder == PRE_RELEASE
    elif "+" in patch_part:
        patch, dev = patch_part.split("+", 1)
        assert int(patch) == PATCH
        assert dev == DEV
    else:
        assert int(patch_part) == PATCH


def test_get_version_tuple_with_mock():
    """Test get_version_tuple when modified."""
    # Test that it properly returns the tuple of constants
    result = get_version_tuple()
    assert len(result) == 5


def test_main_function_execution():
    """Test that the module runs as a script."""
    # This is hard to test directly, but we can at least verify the constants
    from scriptic.version import MAJOR, MINOR, PATCH

    assert isinstance(MAJOR, int)
    assert isinstance(MINOR, int)
    assert isinstance(PATCH, int)


def test_compare_versions_invalid_inputs():
    """Test compare_versions with invalid inputs."""
    with pytest.raises(ValueError):
        compare_versions("invalid", "0.1.0")

    with pytest.raises(ValueError):
        compare_versions("0.1.0", "invalid")


if __name__ == "__main__":
    unittest.main()
