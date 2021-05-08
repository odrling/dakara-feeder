from unittest import TestCase

from path import Path

from dakara_feeder.similarity_calculator import calculate_file_path_similarity


class CalculateFilePathSimilarityTestCase(TestCase):
    """Test calculate_file_path_similarity method
    """

    def test_renamed(self):
        """Test to detect a file renamed in the same directory
        """
        self.assertGreater(
            calculate_file_path_similarity(
                Path("directory/filename.mp4"), Path("directory/filenam.mp4")
            ),
            0.95,
        )

    def test_moved(self):
        """Test to detect a file moved with same name to another directory
        """
        self.assertGreater(
            calculate_file_path_similarity(
                Path("directory/filename.mp4"), Path("other/filename.mp4")
            ),
            0.90,
        )

    def test_different(self):
        """Test to not detect two different files in the same directory
        """
        self.assertLess(
            calculate_file_path_similarity(
                Path("directory/filename.mp4"), Path("directory/other.mp4")
            ),
            0.60,
        )

    def test_symmetry(self):
        """Test the calculation is symmetrical
        """
        self.assertAlmostEqual(
            calculate_file_path_similarity(Path("directory"), Path("other")),
            calculate_file_path_similarity(Path("other"), Path("directory")),
        )
