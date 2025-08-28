"""LGApp - NiceGUI web interface for pytest with Labgrid.

A web application that provides a user-friendly interface for uploading and executing 
pytest test scripts integrated with Labgrid for hardware testing.
"""

from .app import main, main_without_reload

__version__ = "0.2.0"
__all__ = ["main", "main_without_reload"]