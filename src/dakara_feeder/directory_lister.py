import logging
from itertools import groupby

import filetype

from dakara_feeder.subtitle_parser import is_subtitle


logger = logging.getLogger(__name__)


def list_directory(path):
    """List video files in given directory recursively

    Args:
        path (path.Path): Path of directory to scan.

    Returns:
        list of SongPaths: paths of the files for each song. Paths are relative
        to the given path.
    """
    logger.debug("Listing '%s'", path)
    files_list = [p.relpath(path) for p in path.walkfiles()]
    files_list.sort()
    logger.debug("Listed %i files", len(files_list))

    listing = [
        item
        for _, files in groupby(files_list, lambda f: f.dirname() / f.stem)
        for item in group_by_type(files, path)
    ]

    logger.debug("Found %i different videos", len(listing))

    return listing


def get_main_type(file):
    """Get the first part of the MIME type of the given file

    Args:
        file (path.Path): Absolute path to the file to extract the MIME type.

    Returns
        str: Main type if the MIME type can be extracted, None otherwise.
    """
    kind = filetype.guess(str(file))

    if not kind:
        return None

    maintype, _ = kind.mime.split("/")
    return maintype


def group_by_type(files, path):
    """Group files by extension

    Args:
        files (list of path.Path): List of relative path to the files to group.
        path (path.Path): Path of directory to scan.

    Returns:
        list of SongPaths: paths of the files for each song.
    """
    # sort files by their extension
    videos = []
    audios = []
    subtitles = []
    others = []
    for file in files:
        maintype = get_main_type(path / file)

        if maintype == "video":
            videos.append(file)
            continue

        if maintype == "audio":
            audios.append(file)
            continue

        if is_subtitle(file):
            subtitles.append(file)
            continue

        others.append(file)

    # check there is at least one video
    if len(videos) == 0:
        return []

    # check there if there are only one audio file
    if len(audios) > 1:
        logger.warning("More than one audio file for video '%s'", videos[0])
        return []

    # check there if there are only one subtitle
    if len(subtitles) > 1:
        logger.warning("More than one subtitle for video '%s'", videos[0])
        return []

    # recombine the files
    return [
        SongPaths(
            video,
            audios[0] if audios else None,
            subtitles[0] if subtitles else None,
            others,
        )
        for video in videos
    ]


class SongPaths:
    """Paths of files related to a song

    Attributes:
        video (path.Path): Path to the video file.
        audio (path.Path): Path to the audio file.
        subtitle (path.Path): Path to the subtitle file.
        others (list of path.Path): Paths of other files.
    """

    def __init__(self, video, audio=None, subtitle=None, others=[]):
        self.video = video
        self.audio = audio
        self.subtitle = subtitle
        self.others = others

    def __eq__(self, other):
        return self.__hash__() == other.__hash__()

    def __hash__(self):
        return hash(str(self))

    def __repr__(self):
        return "video: {}, audio: {}, subtitle: {}, others: {}".format(
            self.video, self.audio, self.subtitle, self.others
        )
