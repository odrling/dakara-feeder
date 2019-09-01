from unittest import TestCase

from dakara_base.resources_manager import get_file

from dakara_feeder.subtitle_parser import Pysubs2SubtitleParser


class Pysubs2SubtitleParserTestCase(TestCase):
    def generic_test_subtitle(self, file_name):
        """Run lyrics extraction test on specified file

        Open and extract lyrics from the file,
        and test that the result is the same as the
        corresponding file with "_expected" prefix.

        This method is called from tests methods.
        """
        file_path = get_file("dakara_feeder.tests.resources.subtitles", file_name)

        parser = Pysubs2SubtitleParser(file_path)
        lyrics = parser.get_lyrics()
        lines = lyrics.splitlines()

        # Check against expected file
        with open(file_path + "_expected") as expected:
            expected_lines = expected.read().splitlines()

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
