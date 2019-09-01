from unittest import TestCase

from path import Path

from dakara_feeder.similarity_calculator import calculate_file_path_similarity


class CalculateFilePathSimilarityTestCase(TestCase):
    """Test calculate_file_path_similarity method
    """

    def test_renamed(self):
        self.assertGreater(
            calculate_file_path_similarity(
                Path("directory/filename.mp4"), Path("directory/filenam.mp4")
            ),
            0.95,
        )

    def test_moved(self):
        self.assertGreater(
            calculate_file_path_similarity(
                Path("directory/filename.mp4"), Path("other/filename.mp4")
            ),
            0.90,
        )

    def test_different(self):
        self.assertLess(
            calculate_file_path_similarity(
                Path("directory/filename.mp4"), Path("directory/other.mp4")
            ),
            0.60,
        )
