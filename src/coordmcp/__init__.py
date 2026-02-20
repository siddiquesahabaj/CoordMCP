"""
CoordMCP - A FastMCP-based Model Context Protocol server for intelligent multi-agent code coordination.

Provides shared long-term memory, context switching capabilities, and architectural guidance.
"""

import warnings

# Suppress Pydantic v1 deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")
try:
    from pydantic import PydanticDeprecatedSince20
    warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)
except ImportError:
    pass

import sys

if sys.version_info >= (3, 8):
    from importlib.metadata import version, PackageNotFoundError
else:
    from importlib_metadata import version, PackageNotFoundError

try:
    __version__ = version("coordmcp")
except PackageNotFoundError:
    # Package is not installed
    __version__ = "unknown"

__all__ = ["__version__"]
