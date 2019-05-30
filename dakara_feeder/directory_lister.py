def list_directory(path):
    """List existing files in local directory

    Args:
        path (path.Path): Path of directory to scan.

    Returns:
        list of str: each file in the directory and its subdirectories. Path of
            each file is relative to the given path.
    """
    return [p.relpath(path) for p in path.walkfiles()]
