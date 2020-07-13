import logging
import subprocess
from abc import ABC, abstractmethod
from tempfile import TemporaryDirectory

from path import Path


logger = logging.getLogger(__name__)


class SubtitleExtractor(ABC):
    """Abstract class for subtitle extractor

    Arg:
        content (anything): object containing the lyrics. Can be a complete
            object or the full text of the lyrics.
    """

    def __init__(self, content=""):
        self.content = content

    @staticmethod
    @abstractmethod
    def is_available():
        """Check if the parser is callable
        """

    @classmethod
    @abstractmethod
    def extract(cls, filepath):
        """Extract lyrics form a file

        Args:
            input_file_path (str): path to the input file.
        """

    def get_subtitle(self):
        return self.content


class FFmpegSubtitleExtractor(SubtitleExtractor):
    """Subtitle extractor using FFmpeg
    """

    @staticmethod
    def is_available():
        """Check if the parser is callable
        """
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True

        except FileNotFoundError:
            return False

    @classmethod
    def extract(cls, input_file_path):
        """Extract lyrics form a file

        Try to extract the first subtitle of the given input file into the
        output file given.

        Args:
            input_file_path (str): path to the input file.
        """
        with TemporaryDirectory() as tempdir:
            directory_path = Path(tempdir)
            output_file_path = directory_path / "output.ass"

            process = subprocess.run(
                ["ffmpeg", "-i", input_file_path, "-map", "0:s:0", output_file_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            # if call failed, return empty string
            if process.returncode:
                return cls()

            # otherwise extract content
            return cls(output_file_path.text())
