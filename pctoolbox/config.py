import os
import sys

# Dynamic root path resolution for production and build processes
# PyInstaller stores unpack paths in sys._MEIPASS
if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def get_asset_path(relative_path: str) -> str:
    """
    Get the dynamically resolved absolute path to a resource/asset.
    This guarantees that asset paths won't break when packaged into an executable.
    """
    return os.path.abspath(os.path.join(BASE_DIR, "assets", relative_path))

# Central Global State for Licensing
# IS_PRO_VERSION controls the feature set of the toolbox.
# If True, Pro/Advanced features (like Optimizer and Macro) are fully unlocked.
# If False, they are locked, showing a lock icon and custom styling in the UI.
IS_PRO_VERSION = False

def set_pro_version(is_pro: bool):
    """
    Helper function to dynamically toggle the IS_PRO_VERSION state for testing
    and seamless integration with Steamworks / license APIs.
    """
    global IS_PRO_VERSION
    IS_PRO_VERSION = is_pro
