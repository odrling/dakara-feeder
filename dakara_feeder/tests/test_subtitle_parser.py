from unittest import TestCase

from dakara_base.resources_manager import get_file
from path import Path

from dakara_feeder.subtitle_parser import Pysubs2SubtitleParser


class Pysubs2SubtitleParserTestCase(TestCase):
    """Test the subtitle parser based on pysubs2
    """

    def generic_test_subtitle(self, file_name):
        """Run lyrics extraction test on specified file

        Open and extract lyrics from the file, and test that the result is the
        same as the corresponding file with "_expected" prefix.

        This method is called from other tests methods.
        """
        file_path = get_file("dakara_feeder.tests.resources.subtitles", file_name)

        # open and parse given file
        parser = Pysubs2SubtitleParser.parse(file_path)
        lyrics = parser.get_lyrics()
        lines = lyrics.splitlines()

        # open expected result
        expected_lines = (file_path + "_expected").lines(retain=False)

        # check against expected file
        self.assertListEqual(lines, expected_lines)

    def test_simple(self):
        """Test simple ass
        """
        self.generic_test_subtitle("simple.ass")

    def test_duplicate_lines(self):
        """Test ass with duplicate lines
        """
        self.generic_test_subtitle("duplicate_lines.ass")

    def test_drawing_commands(self):
        """Test ass containing drawing commands
        """
        self.generic_test_subtitle("drawing_commands.ass")

    def test_comment_and_whitespace(self):
        """Test ass containing comment and whitespace
        """
        self.generic_test_subtitle("comment_and_whitespace.ass")

    def test_not_found(self):
        """Test when the ass file to parse does not exist
        """
        with self.assertRaises(FileNotFoundError):
            Pysubs2SubtitleParser.parse(Path("nowhere"))
