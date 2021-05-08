from unittest import TestCase
from unittest.mock import ANY, patch
from datetime import timedelta

from path import Path
from pymediainfo import MediaInfo

from dakara_feeder.metadata_parser import (
    FFProbeMetadataParser,
    FFProbeNotInstalledError,
    MediaParseError,
    MediainfoMetadataParser,
    MediainfoNotInstalledError,
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

    @patch.object(MediainfoMetadataParser, "is_available")
    def test_parse_not_available(self, mocked_is_available):
        """Test to parse whene mediainfo is not installed
        """
        mocked_is_available.return_value = False

        with self.assertRaisesRegex(
            MediainfoNotInstalledError, "Mediainfo not installed"
        ):
            MediainfoMetadataParser.parse(Path("nowhere"))

    @patch.object(MediaInfo, "parse", autoset=True)
    @patch.object(MediainfoMetadataParser, "is_available")
    def test_parse_invalid_error(self, mocked_is_available, mocked_parse):
        """Test to extract metadata from a file that cannot be parsed
        """
        # prepare the mock
        mocked_is_available.return_value = True
        mocked_parse.side_effect = Exception("invalid")

        # call the method
        with self.assertRaisesRegex(
            MediaParseError, "Error when processing media file 'nowhere': invalid"
        ):
            MediainfoMetadataParser.parse(Path("nowhere"))


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

    @patch.object(FFProbeMetadataParser, "is_available")
    def test_parse_not_available(self, mocked_is_available):
        """Test to parse whene mediainfo is not installed
        """
        mocked_is_available.return_value = False

        with self.assertRaisesRegex(FFProbeNotInstalledError, "FFProbe not installed"):
            FFProbeMetadataParser.parse(Path("nowhere"))

    def test_get_duration_format(self):
        """Test to get duration stored in format key
        """
        parser = FFProbeMetadataParser({"format": {"duration": "42.42"}})
        self.assertEqual(parser.get_duration(), timedelta(seconds=42.42))

    def test_get_duration_streams(self):
        """Test to get duration stored in streams key
        """
        parser = FFProbeMetadataParser({"streams": [{"duration": "42.42"}]})
        self.assertEqual(parser.get_duration(), timedelta(seconds=42.42))

    def test_get_duration_default(self):
        """Test to get default null duration
        """
        parser = FFProbeMetadataParser({})
        self.assertEqual(parser.get_duration(), timedelta(0))

    def test_get_audio_tracks_count_no_streams(self):
        """Test to get default null number of audio tracks
        """
        parser = FFProbeMetadataParser({})
        self.assertEqual(parser.get_audio_tracks_count(), 0)

    def test_get_audio_tracks_count(self):
        """Test to get number of audio tracks
        """
        parser = FFProbeMetadataParser(
            {
                "streams": [
                    {"codec_type": "audio"},
                    {"codec_type": "video"},
                    {"codec_type": "subtitle"},
                ]
            }
        )
        self.assertEqual(parser.get_audio_tracks_count(), 1)

    def test_get_subtitle_tracks_count_no_streams(self):
        """Test to get default null number of subtitle tracks
        """
        parser = FFProbeMetadataParser({})
        self.assertEqual(parser.get_subtitle_tracks_count(), 0)

    def test_get_subtitle_tracks_count(self):
        """Test to get number of subtitle tracks
        """
        parser = FFProbeMetadataParser(
            {
                "streams": [
                    {"codec_type": "audio"},
                    {"codec_type": "video"},
                    {"codec_type": "subtitle"},
                ]
            }
        )
        self.assertEqual(parser.get_subtitle_tracks_count(), 1)
