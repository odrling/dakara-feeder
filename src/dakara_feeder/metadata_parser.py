import json
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

    @abstractmethod
    def get_duration(self):
        """Get duration as timedelta object

        Returns timedelta 0 if unable to get duration.
        """

    @abstractmethod
    def get_audio_tracks_count(self):
        """Get number of audio tracks

        Returns:
            int: Number of audio tracks.
        """

    @abstractmethod
    def get_subtitle_tracks_count(self):
        """Get number of subtitle tracks

        Returns:
            int: Number of subtitle tracks.
        """


class NullMetadataParser(MetadataParser):
    """Dummy metedata parser

    This is a null parser that always returns a timedelta 0 duration.

    It can be used with:

    >>> from Path import path
    >>> file_path = Path("path/to/file")
    >>> metadata = NullMetadataParser.parse(file_path)
    >>> metadata.get_duration()
    datetime.timedelta(0)
    """

    @staticmethod
    def is_available():
        return True

    @classmethod
    def parse(cls, filename):
        return cls(filename)

    def get_duration(self):
        return timedelta(0)

    def get_audio_tracks_count(self):
        return 0

    def get_subtitle_tracks_count(self):
        return 0


class MediainfoMetadataParser(MetadataParser):
    """Metadata parser based on PyMediaInfo (wrapper for MediaInfo)

    The class works as an interface for the MediaInfo class, provided by the
    pymediainfo module.

    It does not seem to work on Windows, as the mediainfo DLL cannot be found.

    It can be used with:

    >>> from Path import path
    >>> file_path = Path("path/to/file")
    >>> metadata = MediainfoMetadataParser.parse(file_path)
    >>> metadata.get_duration()
    datetime.timedelta(seconds=42)
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
        try:
            metadata = MediaInfo.parse(filename)

        except FileNotFoundError as error:
            raise MediaNotFoundError(
                "Media file '{}' not found".format(filename)
            ) from error

        except BaseException as error:
            raise MediaParseError(
                "Error when processing media file '{}': {}".format(filename, error)
            ) from error

        return cls(metadata)

    def get_duration(self):
        """Get duration as timedelta object

        Returns timedelta 0 if unable to get duration.
        """
        general_track = self.metadata.tracks[0]
        duration = getattr(general_track, "duration", 0) or 0
        return timedelta(milliseconds=int(duration))

    def get_audio_tracks_count(self):
        """Get number of audio tracks

        Returns:
            int: Number of audio tracks.
        """
        return len([t for t in self.metadata.tracks if t.track_type == "Audio"])

    def get_subtitle_tracks_count(self):
        """Get number of subtitle tracks

        Returns:
            int: Number of subtitle tracks.
        """
        return len([t for t in self.metadata.tracks if t.track_type == "Text"])


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

    It can be used with:

    >>> from Path import path
    >>> file_path = Path("path/to/file")
    >>> metadata = FFProbeMetadataParser.parse(file_path)
    >>> metadata.get_duration()
    datetime.timedelta(seconds=42)
    """

    @staticmethod
    def is_available():
        """Check if the parser is callable
        """
        try:
            subprocess.run(
                ["ffprobe", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        except FileNotFoundError:
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
                raise MediaNotFoundError("Media file '{}' not found".format(filename))

            # otherwise
            raise MediaParseError(
                "Error when processing media file '{}'".format(filename)
            )

        return cls(json.loads(process.stdout.decode(sys.stdout.encoding)))

    def get_duration(self):
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

    def get_audio_tracks_count(self):
        """Get number of audio tracks

        Returns:
            int: Number of audio tracks.
        """
        if "streams" not in self.metadata:
            return 0

        return len(
            [s for s in self.metadata["streams"] if s.get("codec_type") == "audio"]
        )

    def get_subtitle_tracks_count(self):
        """Get number of subtitle tracks

        Returns:
            int: Number of subtitle tracks.
        """
        if "streams" not in self.metadata:
            return 0

        return len(
            [s for s in self.metadata["streams"] if s.get("codec_type") == "subtitle"]
        )


class MediaParseError(DakaraError):
    """Error if the metadata cannot be parsed
    """


class MediaNotFoundError(DakaraError, FileNotFoundError):
    """Error if the metadata file does not exist
    """
