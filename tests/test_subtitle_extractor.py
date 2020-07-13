from unittest import TestCase

from dakara_base.resources_manager import get_file

from dakara_feeder.subtitle_extractor import FFmpegSubtitleExtractor


class FFmpegSubtitleExtractorTestCase(TestCase):
    """Test the subtitle extractor based on FFmpeg
    """

    def test_extract(self):
        """Test to extract subtitle from file
        """
        file_path = get_file("tests.resources.media", "dummy.mkv")
        extractor = FFmpegSubtitleExtractor.extract(file_path)
        subtitle = extractor.get_subtitle()

        subtitle_path = get_file("tests.resources.subtitles", "dummy.ass")
        subtitle_expected = subtitle_path.text()

        self.assertEqual(subtitle, subtitle_expected)
