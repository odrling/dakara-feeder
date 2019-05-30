from unittest import TestCase
from unittest.mock import patch

from dakara_feeder import directory_lister

@patch("dakara_feeder.directory_lister.os.walk")
class ListDirectoryTestCase(TestCase):
    def test_list_directory(self, mocked_walk):
        # mock directory structure
        mocked_walk.return_value = (item for item in [
                (
                    "directory",
                    ["subdirectory"],
                    ["file0", "file1"]
                    ),
                (
                    "directory/subdirectory",
                    [],
                    ["file2", "file3"]
                    )
                ])

        # call the function
        listing = directory_lister.list_directory("directory")

        # check the structure
        self.assertCountEqual([
            "file0",
            "file1",
            "subdirectory/file2",
            "subdirectory/file3"
            ],
            listing)
