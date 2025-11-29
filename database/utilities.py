import os
import platform


def get_data_dir():
    """Get platform-specific data directory for the application."""
    system = platform.system()

    if system == "Linux":
        # Honor XDG_DATA_HOME if set, otherwise use ~/.local/share
        xdg_data_home = os.environ.get("XDG_DATA_HOME")
        if xdg_data_home:
            return os.path.join(xdg_data_home, "quint")
        else:
            return os.path.expanduser("~/.local/share/quint")

    elif system == "Darwin":  # macOS
        return os.path.expanduser("~/Library/Application Support/quint")

    elif system == "Windows":
        # Use LOCALAPPDATA environment variable
        local_app_data = os.environ.get("LOCALAPPDATA")
        if local_app_data:
            return os.path.join(local_app_data, "quint", "quint")
        else:
            # Fallback to user profile
            return os.path.expanduser("~/AppData/Local/quint")

    else:
        # Fallback for unknown systems
        return os.path.expanduser("~/.quint")


DATA_DIR = get_data_dir()
