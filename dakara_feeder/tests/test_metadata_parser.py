from unittest import TestCase
from datetime import timedelta

from dakara_base.resources_manager import get_file

from dakara_feeder.metadata_parser import FFProbeMetadataParser


class FFProbeMetadataParserTestCase(TestCase):
    """Test the FFProbe metadata parser
    """

    def test_get_duration(self):
        """Test get duration
        """
        parser = FFProbeMetadataParser.parse(
            get_file("dakara_feeder.tests.resources", "dummy.mkv")
        )
        self.assertEqual(parser.duration, timedelta(seconds=2))
