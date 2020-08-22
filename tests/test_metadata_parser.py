from unittest import TestCase, skipUnless
from unittest.mock import ANY, patch
from datetime import timedelta

from dakara_base.resources_manager import get_file
from path import Path
from pymediainfo import MediaInfo

from dakara_feeder.metadata_parser import (
    FFProbeMetadataParser,
    MediaParseError,
    MediaNotFoundError,
    MediainfoMetadataParser,
    NullMetadataParser,
)


class NullMetadataParserTestCase(TestCase):
    """Test the dummy metadata parser
    """

    def test_available(self):
        """Test if the dummy parser is available
        """
        self.assertTrue(NullMetadataParser.is_available())

    def test_get_duration(self):
        """Test to get a dummy duration
        """
        parser = NullMetadataParser(Path("path/to/file"))
        self.assertEqual(parser.get_duration(), timedelta(0))

    def test_get_audio_tracks_count(self):
        """Test to get a dummy audio tracks count
        """
        parser = NullMetadataParser(Path("path/to/file"))
        self.assertEqual(parser.get_audio_tracks_count(), 0)

    def test_get_subtitle_tracks_count(self):
        """Test to get a dummy subtitle tracks count
        """
        parser = NullMetadataParser(Path("path/to/file"))
        self.assertEqual(parser.get_subtitle_tracks_count(), 0)


@skipUnless(MediaInfo.can_parse(), "MediaInfo not installed")
class MediainfoMetadataParserTestCase(TestCase):
    """Test the Mediainfo metadata parser
    """

    @patch("dakara_feeder.metadata_parser.MediaInfo.can_parse", autoset=True)
    def test_available(self, mocked_can_parse):
        """Test when the parser is available
        """
        # call the method
        result = MediainfoMetadataParser.is_available()

        # assert the result
        self.assertTrue(result)

        # assert the call
        mocked_can_parse.assert_called_with()

    @patch("dakara_feeder.metadata_parser.MediaInfo.can_parse", autoset=True)
    def test_not_available(self, mocked_can_parse):
        """Test when the parser is not available
        """
        # prepare the mock
        mocked_can_parse.return_value = False

        # call the method
        result = MediainfoMetadataParser.is_available()

        # assert the result
        self.assertFalse(result)

    def test_parse_not_found_error(self):
        """Test to extract metadata from a file that does not exist
        """
        # call the method
        with self.assertRaisesRegex(
            MediaNotFoundError, "Media file 'nowhere' not found"
        ):
            MediainfoMetadataParser.parse(Path("nowhere"))

    @patch.object(MediaInfo, "parse", autoset=True)
    def test_parse_invalid_error(self, mocked_parse):
        """Test to extract metadata from a file that cannot be parsed
        """
        # prepare the mock
        mocked_parse.side_effect = Exception("invalid")

        # call the method
        with self.assertRaisesRegex(
            MediaParseError, "Error when processing media file 'nowhere': invalid"
        ):
            MediainfoMetadataParser.parse(Path("nowhere"))

    def test_get_duration(self):
        """Test to get duration
        """
        parser = MediainfoMetadataParser.parse(
            get_file("tests.resources.media", "dummy.mkv")
        )
        self.assertEqual(
            parser.get_duration(), timedelta(seconds=2, microseconds=23000)
        )

    def test_get_number_audio_tracks(self):
        """Test to get number of audio tracks
        """
        parser = MediainfoMetadataParser.parse(
            get_file("tests.resources.media", "dummy.mkv")
        )
        self.assertEqual(parser.get_audio_tracks_count(), 2)

    def test_get_number_subtitle_tracks(self):
        """Test to get number of subtitle tracks
        """
        parser = MediainfoMetadataParser.parse(
            get_file("tests.resources.media", "dummy.mkv")
        )
        self.assertEqual(parser.get_subtitle_tracks_count(), 1)


class FFProbeMetadataParserTestCase(TestCase):
    """Test the FFProbe metadata parser
    """

    @patch("dakara_feeder.metadata_parser.subprocess.run", autoset=True)
    def test_available(self, mocked_run):
        """Test when the parser is available
        """
        # call the method
        result = FFProbeMetadataParser.is_available()

        # assert the result
        self.assertTrue(result)

        # assert the call
        mocked_run.assert_called_with(["ffprobe", "-version"], stdout=ANY, stderr=ANY)

    @patch("dakara_feeder.metadata_parser.subprocess.run", autoset=True)
    def test_not_available(self, mocked_run):
        """Test when the parser is not available
        """
        # prepare the mock
        mocked_run.side_effect = FileNotFoundError()

        # call the method
        result = FFProbeMetadataParser.is_available()

        # assert the result
        self.assertFalse(result)

    @patch.object(Path, "exists", autoset=True)
    def test_parse_not_found_error(self, mocked_exists):
        """Test to extract metadata from a file that does not exist
        """
        # prepare the mock
        mocked_exists.return_value = False

        # call the method
        with self.assertRaisesRegex(
            MediaNotFoundError, "Media file 'nowhere' not found"
        ):
            FFProbeMetadataParser.parse(Path("nowhere"))

        # assert the call
        mocked_exists.assert_called_with()

    @patch.object(Path, "exists", autoset=True)
    def test_parse_invalid_error(self, mocked_exists):
        """Test to extract metadata from a file that cannot be parsed
        """
        # prepare the mock
        mocked_exists.return_value = True

        # call the method
        with self.assertRaisesRegex(
            MediaParseError, "Error when processing media file 'nowhere'"
        ):
            FFProbeMetadataParser.parse(Path("nowhere"))

    def test_get_duration(self):
        """Test to get duration
        """
        parser = FFProbeMetadataParser.parse(
            get_file("tests.resources.media", "dummy.mkv")
        )
        self.assertEqual(
            parser.get_duration(), timedelta(seconds=2, microseconds=23000)
        )

    def test_get_number_audio_tracks(self):
        """Test to get number of audio tracks
        """
        parser = FFProbeMetadataParser.parse(
            get_file("tests.resources.media", "dummy.mkv")
        )
        self.assertEqual(parser.get_audio_tracks_count(), 2)

    def test_get_number_subtitle_tracks(self):
        """Test to get number of subtitle tracks
        """
        parser = FFProbeMetadataParser.parse(
            get_file("tests.resources.media", "dummy.mkv")
        )
        self.assertEqual(parser.get_subtitle_tracks_count(), 1)
