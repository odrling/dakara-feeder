from unittest import TestCase, skipUnless
from unittest.mock import ANY, patch
from datetime import timedelta
from subprocess import CalledProcessError

from dakara_base.resources_manager import get_file
from path import Path
from pymediainfo import MediaInfo

from dakara_feeder.metadata_parser import (
    FFProbeMetadataParser,
    MediaParseError,
    MediaNotFoundError,
    MediainfoMetadataParser,
)


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
        with self.assertRaises(MediaNotFoundError) as error:
            MediainfoMetadataParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(str(error.exception), "Media file nowhere not found")

    @patch.object(MediaInfo, "parse", autoset=True)
    def test_parse_invalid_error(self, mocked_parse):
        """Test to extract metadata from a file that cannot be parsed
        """
        # prepare the mock
        mocked_parse.side_effect = Exception("invalid")

        # call the method
        with self.assertRaises(MediaParseError) as error:
            MediainfoMetadataParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(
            str(error.exception), "Error when processing media file nowhere: invalid"
        )

    def test_get_duration(self):
        """Test to get duration
        """
        parser = MediainfoMetadataParser.parse(get_file("tests.resources", "dummy.mkv"))
        self.assertEqual(parser.get_duration(), timedelta(seconds=2))


class FFProbeMetadataParserTestCase(TestCase):
    """Test the FFProbe metadata parser
    """

    @patch("dakara_feeder.metadata_parser.subprocess.check_call", autoset=True)
    def test_available(self, mocked_check_call):
        """Test when the parser is available
        """
        # call the method
        result = FFProbeMetadataParser.is_available()

        # assert the result
        self.assertTrue(result)

        # assert the call
        mocked_check_call.assert_called_with(ANY, stdout=ANY, stderr=ANY)

    @patch("dakara_feeder.metadata_parser.subprocess.check_call", autoset=True)
    def test_not_available(self, mocked_check_call):
        """Test when the parser is not available
        """
        # prepare the mock
        mocked_check_call.side_effect = CalledProcessError(255, "none")

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
        with self.assertRaises(MediaNotFoundError) as error:
            FFProbeMetadataParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(str(error.exception), "Media file nowhere not found")

        # assert the call
        mocked_exists.assert_called_with()

    @patch.object(Path, "exists", autoset=True)
    def test_parse_invalid_error(self, mocked_exists):
        """Test to extract metadata from a file that cannot be parsed
        """
        # prepare the mock
        mocked_exists.return_value = True

        # call the method
        with self.assertRaises(MediaParseError) as error:
            FFProbeMetadataParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(
            str(error.exception), "Error when processing media file nowhere"
        )

    def test_get_duration(self):
        """Test to get duration
        """
        parser = FFProbeMetadataParser.parse(get_file("tests.resources", "dummy.mkv"))
        self.assertEqual(parser.get_duration(), timedelta(seconds=2))
