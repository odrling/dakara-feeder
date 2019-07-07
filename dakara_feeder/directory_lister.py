import logging
from itertools import groupby


logger = logging.getLogger(__name__)


VIDEO_EXTENSIONS = [".avi", ".mkv", ".mp4", ".mpeg", ".mpg", ".vob", ".webm"]
SUBTITLE_EXTENSIONS = []


def list_directory(path):
    """List files in local directory

    Must be video files.

    Args:
        path (path.Path): Path of directory to scan.

    Returns:
        list: each file in the directory and its subdirectories. Path of
            each file is relative to the given path.
    """
    logger.debug("Listing %s", path)
    files_list = path.walkfiles()
    logger.debug("Listed %i files", len(files_list))

    return [
        item
        for _, files in groupby(files_list, lambda f: f.stem)
        for item in group_by_type(files)
    ]

def group_by_type(files):
    # sort files by their extension
    videos = []
    subtitles = []
    others = []
    for file in files:
        if file.ext in VIDEO_EXTENSIONS:
            videos.append(file)
            continue

        if file.ext in SUBTITLE_EXTENSIONS:
            subtitles.append(file)
            continue

        others.append(file)

    # check there is at least one video
    if len(videos) == 0:
        return []

    # check there if there are only one subtitle
    if len(subtitles) > 1:
        logger.warning("More than one subtitle for video %s", videos[0])
        return []

    # recombine the files
    return [
        {
            "video": video,
            "subtitle": subtitles[0] if subtitles else None,
            "others": others
        } for video in videos
    ]
