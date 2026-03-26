import os


def ensure_dir(path: str) -> None:
    """
    Create a directory (and parents) if it does not already exist.
    """
    if not os.path.exists(path):
        os.makedirs(path)