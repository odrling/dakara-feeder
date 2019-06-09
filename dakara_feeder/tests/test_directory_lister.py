from unittest import TestCase
from unittest.mock import patch

from path import Path

from dakara_feeder import directory_lister


class ListDirectoryTestCase(TestCase):
    """Test the directory lister
    """

    @patch.object(Path, "walkfiles")
    def test_list_directory(self, mocked_walkfiles):
        """Test to list a directory
        """
        # mock directory structure
        mocked_walkfiles.return_value = (
            item
            for item in [
                Path("directory/file0.mkv"),
                Path("directory/file1.mkv"),
                Path("directory/subdirectory/file2.mkv"),
                Path("directory/subdirectory/file3.mkv"),
            ]
        )

        # call the function
        with self.assertLogs("dakara_feeder.directory_lister", "DEBUG") as logger:
            listing = directory_lister.list_directory(Path("directory"))

        # check the structure
        self.assertCountEqual(
            [
                Path("file0.mkv"),
                Path("file1.mkv"),
                Path("subdirectory/file2.mkv"),
                Path("subdirectory/file3.mkv"),
            ],
            listing,
        )

        # check the logger was called
        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.directory_lister:Listing directory",
                "DEBUG:dakara_feeder.directory_lister:Listed 4 files",
            ],
        )

    @patch.object(Path, "walkfiles")
    def test_list_directory_with_extra_files(self, mocked_walkfiles):
        """Test to list a directory with extra unwanted files
        """
        # mock directory structure
        mocked_walkfiles.return_value = (
            item
            for item in [
                Path("directory/file0.mkv"),
                Path("directory/file1.other"),
                Path("directory/subdirectory/file2.mp4"),
                Path("directory/subdirectory/file3.other"),
            ]
        )

        # call the function
        with self.assertLogs("dakara_feeder.directory_lister", "DEBUG"):
            listing = directory_lister.list_directory(Path("directory"))

        # check the structure
        self.assertCountEqual(
            [Path("file0.mkv"), Path("subdirectory/file2.mp4")], listing
        )
