import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_appdata_path(filename):
    """Return the full path for a file in the user's AppData/Roaming/LuckeePass directory."""
    appdata = os.getenv('APPDATA')
    luckeepass_dir = os.path.join(appdata, 'LuckeePass')
    os.makedirs(luckeepass_dir, exist_ok=True)
    return os.path.join(luckeepass_dir, filename) 