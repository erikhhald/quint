import os
import platform
from pathlib import Path


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


def write_to_managed_store(data, deck_name, original_path):
    """
    Write file data to the managed store under DATA_DIR/files/deck_name.

    Args:
        data: File data to write (bytes or string)
        deck_name: Name of the deck for directory organization
        original_path: Original file path to extract filename from

    Returns:
        str: Path to the written file in managed store
    """
    # Create the managed directory structure
    files_dir = Path(DATA_DIR) / "files" / deck_name
    files_dir.mkdir(parents=True, exist_ok=True)

    # Extract filename from original path
    original_file = Path(original_path)
    filename = original_file.name

    # Generate unique filename if needed
    target_path = files_dir / filename
    counter = 1
    while target_path.exists():
        stem = original_file.stem
        suffix = original_file.suffix
        filename = f"{stem}_{counter}{suffix}"
        target_path = files_dir / filename
        counter += 1

    # Write the file data
    if isinstance(data, str):
        target_path.write_text(data, encoding="utf-8")
    else:
        target_path.write_bytes(data)

    return str(target_path)
