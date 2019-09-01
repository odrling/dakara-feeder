import json
import os
import subprocess
import sys
from abc import ABC, abstractmethod
from datetime import timedelta

from pymediainfo import MediaInfo
from dakara_base.exceptions import DakaraError


class MetadataParser(ABC):
    """Base class for metadata parser

    Interface for the various metadata parsers available.
    """

    def __init__(self, metadata):
        self.metadata = metadata

    @staticmethod
    @abstractmethod
    def is_available():
        """Check if the parser is callable
        """

    @classmethod
    @abstractmethod
    def parse(cls, filename):
        """Parse metadata from file name

        Args:
            filename (str): path of the file to parse.
        """

    @property
    @abstractmethod
    def duration(self):
        """Get duration as timedelta object

        Returns timedelta 0 if unable to get duration.
        """


class NullMetadataParser(MetadataParser):
    """Dummy metedata parser

    This is a null parser that always returns a timedelta 0 duration.
    """

    @staticmethod
    def is_available():
        return True

    @classmethod
    def parse(cls, filename):
        return cls(filename)

    @property
    def duration(self):
        return timedelta(0)


class MediainfoMetadataParser(MetadataParser):
    """Metadata parser based on PyMediaInfo (wrapper for MediaInfo)

    The class works as an interface for the MediaInfo class, provided by the
    pymediainfo module.

    It does not seem to work on Windows, as the mediainfo DLL cannot be found.
    """

    @staticmethod
    def is_available():
        """Check if the parser is callable
        """
        return MediaInfo.can_parse()

    @classmethod
    def parse(cls, filename):
        """Parse metadata from file name

        Args:
            filename (str): path of the file to parse.
        """
        metadata = MediaInfo.parse(filename)
        return cls(metadata)

    @property
    def duration(self):
        """Get duration as timedelta object

        Returns timedelta 0 if unable to get duration.
        """
        general_track = self.metadata.tracks[0]
        duration = getattr(general_track, "duration", 0) or 0
        return timedelta(milliseconds=int(duration))


class FFProbeMetadataParser(MetadataParser):
    """Metadata parser based on ffprobe

    The class works as a wrapper for the `ffprobe` command. The ffprobe3 module
    does not work, so we do our own here.

    The command is invoked through `subprocess`, so it should work on Windows
    as long as ffmpeg is installed and callable from the command line. Data are
    passed as JSON string.

    Freely inspired from [this proposed
    wrapper](https://stackoverflow.com/a/36743499) and the [code of
    ffprobe3](https://github.com/DheerendraRathor/ffprobe3/blob/master/ffprobe3/ffprobe.py).
    """

    @staticmethod
    def is_available():
        """Check if the parser is callable
        """
        try:
            with open(os.devnull, "w") as tempf:
                subprocess.check_call(["ffprobe", "-h"], stdout=tempf, stderr=tempf)

                return True

        except subprocess.CalledProcessError:
            return False

    @classmethod
    def parse(cls, filename):
        """Parse metadata from file name

        Args:
            filename (path.Path): path of the file to parse.
        """
        command = [
            "ffprobe",
            "-loglevel",
            "quiet",
            "-print_format",
            "json",
            "-show_format",
            "-show_streams",
            filename,
        ]

        process = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        # check errors
        if process.returncode:
            # check the file exists
            if not filename.exists():
                raise MediaFileNotFoundError("Media file {} not found".format(filename))

            # otherwise
            raise ParseError("Error when processing media file {}".format(filename))

        return cls(json.loads(process.stdout.decode(sys.stdout.encoding)))

    @property
    def duration(self):
        """Get duration as timedelta object

        Returns:
            datetime.timedelta: duration of the media. Timedelta of 0 if unable
            to get duration.
        """
        # try in generic location
        if "format" in self.metadata:
            if "duration" in self.metadata["format"]:
                return timedelta(seconds=float(self.metadata["format"]["duration"]))

        # try in the streams
        if "streams" in self.metadata:
            # commonly stream 0 is the video
            for stream in self.metadata["streams"]:
                if "duration" in stream:
                    return timedelta(seconds=float(stream["duration"]))

        # if nothing is found
        return timedelta(0)


class ParseError(DakaraError):
    """Error if the metadata cannot be parsed
    """


class MediaFileNotFoundError(DakaraError):
    """Error if the metadata file does not exist
    """
