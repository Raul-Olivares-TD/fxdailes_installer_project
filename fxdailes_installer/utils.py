import sys
import os


def resource_path(relative_path: str):
    """
    Returns the absolute path to a resource for PyInstaller.
    
    Args:
        relative_path (str): A relative path from the folder/file
            to pack in PyInstaller.
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    else:
        # In development, the base path is the project root
        base_path = os.path.abspath(".")

    # Adjust base path to point to the `assets` directory within our package
    return os.path.join(base_path, 'fxdailes_installer', 'assets', relative_path)
