"""
Scriptic: A minimalist embeddable Python REPL

A lightweight, zero-dependency REPL designed to be embedded within Python applications.
Features include multiline input support, custom command hooks, and context injection.
"""

# Import core components for easy access
from .scriptic import Scriptic, run_scriptic, run_cli

# Import version information
from .version import __version__, get_version, get_version_info, VERSION

# Package metadata
__author__ = "Ryan O'Boyle"
__email__ = "layerdynamics@proton.me"
__license__ = "MIT"

# Define what's available when using `from scriptic import *`
__all__ = ["Scriptic", "run_scriptic", "run_cli", "__version__", "get_version", "get_version_info", "VERSION"]
