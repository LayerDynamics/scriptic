#!/usr/bin/env python3
"""
Scriptic version information

This module contains version information for the Scriptic package.
It follows semantic versioning (https://semver.org/) with a MAJOR.MINOR.PATCH format.
"""

import re
from typing import Tuple, Dict, Any, Optional


# Version components
MAJOR = 0
MINOR = 1
PATCH = 0
PRE_RELEASE = None  # e.g., "alpha", "beta", "rc1"
DEV = None  # e.g., "dev0"

# Release information
RELEASE_DATE = "2025-04-30"
AUTHOR = "Ryan O'Boyle"
AUTHOR_EMAIL = "layerdynamics@proton.me"
LICENSE = "MIT"


def get_version() -> str:
    """
    Get the full version string.

    Returns:
        A string representing the current version in the format MAJOR.MINOR.PATCH[-PRE_RELEASE][+DEV]
    """
    version = f"{MAJOR}.{MINOR}.{PATCH}"

    if PRE_RELEASE:
        version += f"-{PRE_RELEASE}"

    if DEV:
        version += f"+{DEV}"

    return version


def get_version_tuple() -> Tuple[int, int, int, Optional[str], Optional[str]]:
    """
    Get the version components as a tuple.

    Returns:
        A tuple of (MAJOR, MINOR, PATCH, PRE_RELEASE, DEV)
    """
    return (MAJOR, MINOR, PATCH, PRE_RELEASE, DEV)


def get_version_info() -> Dict[str, Any]:
    """
    Get comprehensive version information.

    Returns:
        A dictionary containing all version information
    """
    return {
        "version": get_version(),
        "major": MAJOR,
        "minor": MINOR,
        "patch": PATCH,
        "pre_release": PRE_RELEASE,
        "dev": DEV,
        "release_date": RELEASE_DATE,
        "author": AUTHOR,
        "author_email": AUTHOR_EMAIL,
        "license": LICENSE,
    }


def parse_version_string(version_str: str) -> Tuple[int, int, int, Optional[str], Optional[str]]:
    """
    Parse a version string into its components.

    Args:
        version_str: A version string in the format MAJOR.MINOR.PATCH[-PRE_RELEASE][+DEV]

    Returns:
        A tuple of (MAJOR, MINOR, PATCH, PRE_RELEASE, DEV)

    Raises:
        ValueError: If the version string is invalid
    """
    # Match semantic versioning pattern
    pattern = r"^(\d+)\.(\d+)\.(\d+)(?:-([a-zA-Z0-9.]+))?(?:\+([a-zA-Z0-9.]+))?$"
    match = re.match(pattern, version_str)

    if not match:
        raise ValueError(f"Invalid version string: {version_str}")

    major, minor, patch = map(int, match.groups()[:3])
    pre_release = match.group(4)
    dev = match.group(5)

    return (major, minor, patch, pre_release, dev)


def compare_versions(version_a: str, version_b: str) -> int:
    """
    Compare two version strings.

    Args:
        version_a: First version string
        version_b: Second version string

    Returns:
        -1 if version_a < version_b
         0 if version_a == version_b
         1 if version_a > version_b

    Raises:
        ValueError: If either version string is invalid
    """
    a_tuple = parse_version_string(version_a)
    b_tuple = parse_version_string(version_b)

    # Compare major, minor, patch
    for i in range(3):
        if a_tuple[i] < b_tuple[i]:
            return -1
        elif a_tuple[i] > b_tuple[i]:
            return 1

    # Compare pre-release (None is greater than any pre-release)
    if a_tuple[3] is None and b_tuple[3] is not None:
        return 1
    elif a_tuple[3] is not None and b_tuple[3] is None:
        return -1
    elif a_tuple[3] != b_tuple[3]:
        return -1 if a_tuple[3] < b_tuple[3] else 1

    # Compare dev (None is greater than any dev)
    if a_tuple[4] is None and b_tuple[4] is not None:
        return 1
    elif a_tuple[4] is not None and b_tuple[4] is None:
        return -1
    elif a_tuple[4] != b_tuple[4]:
        return -1 if a_tuple[4] < b_tuple[4] else 1

    return 0


def is_compatible(version_str: str) -> bool:
    """
    Check if a version is compatible with the current version.

    Compatible versions have the same major version but may have different
    minor or patch versions. This follows semantic versioning principles.

    Args:
        version_str: Version string to compare with the current version

    Returns:
        True if compatible, False otherwise
    """
    try:
        other_major = parse_version_string(version_str)[0]
        return other_major == MAJOR
    except ValueError:
        return False


# String representation of the version
__version__ = get_version()

# For backwards compatibility
VERSION = __version__

if __name__ == "__main__":
    # Print version information when run as a script
    info = get_version_info()
    print(f"Scriptic {info['version']}")
    print(f"Released: {info['release_date']}")
    print(f"Author: {info['author']} <{info['author_email']}>")
    print(f"License: {info['license']}")
