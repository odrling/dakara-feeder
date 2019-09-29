from unittest import TestCase
from unittest.mock import patch

from dakara_base.resources_manager import get_file
from path import Path

from dakara_feeder.subtitle_parser import (
    Pysubs2SubtitleParser,
    SubtitleParseError,
    SubtitleNotFoundError,
)


class Pysubs2SubtitleParserTestCase(TestCase):
    """Test the subtitle parser based on pysubs2
    """

    def generic_test_subtitle(self, file_name):
        """Run lyrics extraction test on specified file

        Open and extract lyrics from the file, and test that the result is the
        same as the corresponding file with "_expected" prefix.

        This method is called from other tests methods.
        """
        file_path = get_file("tests.resources.subtitles", file_name)

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

    def test_not_found_error(self):
        """Test when the ass file to parse does not exist
        """
        # call the method
        with self.assertRaises(SubtitleNotFoundError) as error:
            Pysubs2SubtitleParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(str(error.exception), "Subtitle file nowhere not found")

    @patch("dakara_feeder.subtitle_parser.pysubs2.load")
    def test_parse_error(self, mocked_load):
        """Test when the ass file to parse is invalid
        """
        # prepare the mock
        mocked_load.side_effect = Exception("invalid")

        # call the method
        with self.assertRaises(SubtitleParseError) as error:
            Pysubs2SubtitleParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(
            str(error.exception), "Error when parsing subtitle file nowhere: invalid"
        )
