import logging
from itertools import groupby


logger = logging.getLogger(__name__)


VIDEO_EXTENSIONS = [".avi", ".mkv", ".mp4", ".mpeg", ".mpg", ".vob", ".webm"]
SUBTITLE_EXTENSIONS = [".ass", ".ssa"]


def list_directory(path):
    """List video files in given directory recursively

    Args:
        path (path.Path): Path of directory to scan.

    Returns:
        list of SongPaths: paths of the files for each song. Paths are relative
        to the given path.
    """
    logger.debug("Listing %s", path)
    files_list = [p.relpath(path) for p in path.walkfiles()]
    files_list.sort()
    logger.debug("Listed %i files", len(files_list))

    listing = [
        item
        for _, files in groupby(files_list, lambda f: f.dirname() / f.stem)
        for item in group_by_type(files)
    ]

    logger.debug("Found %i different videos", len(listing))

    return listing


def group_by_type(files):
    """Group files by extension

    Args:
        files (list of path.Path): list of files to group.

    Returns:
        list of SongPaths: paths of the files for each song.
    """
    # sort files by their extension
    videos = []
    subtitles = []
    others = []
    for file in files:
        if file.ext.lower() in VIDEO_EXTENSIONS:
            videos.append(file)
            continue

        if file.ext.lower() in SUBTITLE_EXTENSIONS:
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
        SongPaths(video, subtitles[0] if subtitles else None, others)
        for video in videos
    ]


class SongPaths:
    """Paths of files related to a song

    Attributes:
        video (path.Path): Path to the video file.
        subtitle (path.Path): Path to the subtitle file.
        others (list of path.Path): Paths of other files.
    """

    def __init__(self, video, subtitle=None, others=[]):
        self.video = video
        self.subtitle = subtitle
        self.others = others

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return "video: {}, subtitle: {}, others: {}".format(
            self.video, self.subtitle, self.others
        )
