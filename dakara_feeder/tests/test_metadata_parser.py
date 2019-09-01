from unittest import TestCase
from unittest.mock import ANY, patch
from datetime import timedelta
from subprocess import CalledProcessError

from dakara_base.resources_manager import get_file
from path import Path

from dakara_feeder.metadata_parser import (
    FFProbeMetadataParser,
    ParseError,
    MediaFileNotFoundError,
)


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
    def test_parse_not_found(self, mocked_exists):
        """Test to extract metadata from a file that does not exist
        """
        # prepare the mock
        mocked_exists.return_value = False

        # call the method
        with self.assertRaises(MediaFileNotFoundError) as error:
            FFProbeMetadataParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(str(error.exception), "Media file nowhere not found")

        # assert the call
        mocked_exists.assert_called_with()

    @patch.object(Path, "exists", autoset=True)
    def test_parse_invalid(self, mocked_exists):
        """Test to extract metadata from a file that cannot be parsed
        """
        # prepare the mock
        mocked_exists.return_value = True

        # call the method
        with self.assertRaises(ParseError) as error:
            FFProbeMetadataParser.parse(Path("nowhere"))

        # assert the error
        self.assertEqual(
            str(error.exception), "Error when processing media file nowhere"
        )

    def test_get_duration(self):
        """Test to get duration
        """
        parser = FFProbeMetadataParser.parse(
            get_file("dakara_feeder.tests.resources", "dummy.mkv")
        )
        self.assertEqual(parser.duration, timedelta(seconds=2))
