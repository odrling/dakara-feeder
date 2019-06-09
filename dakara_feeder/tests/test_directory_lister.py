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
        listing = directory_lister.list_directory(Path("directory"))

        # check the structure
        self.assertCountEqual(
            [Path("file0.mkv"), Path("subdirectory/file2.mp4")], listing
        )
