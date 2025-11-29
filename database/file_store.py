from pathlib import Path

from .utilities import DATA_DIR

FILE_DIR = DATA_DIR + "/data/files"


def save_file(file_name, data):
    files_dir = Path(FILE_DIR)
    files_dir.mkdir(parents=True, exist_ok=True)

    # Generate unique filename if needed
    target_path = files_dir / file_name
    counter = 0

    while target_path.exists():
        counter += 1
        name_parts = Path(file_name)
        stem = name_parts.stem
        suffix = name_parts.suffix
        new_name = f"{stem}_{counter}{suffix}"
        target_path = files_dir / new_name

    # Write the file data
    if isinstance(data, str):
        target_path.write_text(data, encoding="utf-8")
    else:
        target_path.write_bytes(data)

    return str(target_path)


def load_file(path, internal=True):
    if internal == True:
        with open(f"{FILE_DIR}/{path}", "r") as f:
            data = f.read()
        return data

    return
