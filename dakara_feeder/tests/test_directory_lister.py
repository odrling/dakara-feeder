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
                Path("directory/file0"),
                Path("directory/file1"),
                Path("directory/subdirectory/file2"),
                Path("directory/subdirectory/file3"),
            ]
        )

        # call the function
        listing = directory_lister.list_directory(Path("directory"))

        # check the structure
        self.assertCountEqual(
            [
                Path("file0"),
                Path("file1"),
                Path("subdirectory/file2"),
                Path("subdirectory/file3"),
            ],
            listing,
        )
