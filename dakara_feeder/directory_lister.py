import os

def list_directory(path):
    """List existing files in local directory

    Args:
        path (str): Path of directory to scan.

    Returns:
        list of str: each file in the directory and its subdirectories. Path of
            each file is relative to the given path.
    """
    return [
            os.path.relpath(os.path.join(directory, filename), path)
            for directory, _, filenames in os.walk(path)
            for filename in filenames
            ]
