VIDEO_EXTENSIONS = [".avi", ".mkv", ".mp4", ".mpeg", ".mpg", ".vob", ".webm"]


def list_directory(path):
    """List files in local directory

    Must be video files.

    Args:
        path (path.Path): Path of directory to scan.

    Returns:
        list: each file in the directory and its subdirectories. Path of
            each file is relative to the given path.
    """
    return [
        p.relpath(path) for p in path.walkfiles() if p.ext.lower() in VIDEO_EXTENSIONS
    ]
