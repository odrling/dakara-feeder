from unittest import TestCase
from unittest.mock import patch

from path import Path
from dakara_base.resources_manager import get_file

from dakara_feeder.directory_lister import group_by_type, list_directory, SongPaths


class ListDirectoryTestCase(TestCase):
    """Test the directory lister
    """

    @patch.object(Path, "walkfiles", autoset=True)
    def test_list_directory(self, mocked_walkfiles):
        """Test to list a directory
        """
        # mock directory structure
        mocked_walkfiles.return_value = (
            item.normpath()
            for item in [
                Path("directory/file0.mkv"),
                Path("directory/file1.mkv"),
                Path("directory/file1.ass"),
                Path("directory/subdirectory/file2.mkv"),
                Path("directory/subdirectory/file3.mkv"),
                Path("directory/subdirectory/file3.ass"),
                Path("directory/subdirectory/empty"),
                Path("directory/file0.ass"),
            ]
        )

        # call the function
        with self.assertLogs("dakara_feeder.directory_lister", "DEBUG") as logger:
            listing = list_directory(Path("directory"))

        # check the structure
        self.assertEqual(len(listing), 4)
        self.assertCountEqual(
            [
                SongPaths(Path("file0.mkv"), Path("file0.ass")),
                SongPaths(Path("file1.mkv"), Path("file1.ass")),
                SongPaths(Path("subdirectory") / "file2.mkv"),
                SongPaths(
                    Path("subdirectory") / "file3.mkv",
                    Path("subdirectory") / "file3.ass",
                ),
            ],
            listing,
        )

        # check the logger was called
        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.directory_lister:Listing directory",
                "DEBUG:dakara_feeder.directory_lister:Listed 8 files",
                "DEBUG:dakara_feeder.directory_lister:Found 4 different videos",
            ],
        )

    @patch.object(Path, "walkfiles", autoset=True)
    def test_list_directory_same_stem(self, mocked_walkfiles):
        """Test case when files with the same name exists in different directories
        """
        # mock directory structure
        mocked_walkfiles.return_value = (
            item.normpath()
            for item in [
                Path("directory/file0.mkv"),
                Path("directory/file0.ass"),
                Path("directory/subdirectory/file0.mkv"),
                Path("directory/subdirectory/file0.ass"),
            ]
        )

        # call the function
        with self.assertLogs("dakara_feeder.directory_lister", "DEBUG") as logger:
            listing = list_directory(Path("directory"))

        # check the structure
        self.assertEqual(len(listing), 2)
        self.assertCountEqual(
            [
                SongPaths(Path("file0.mkv"), Path("file0.ass")),
                SongPaths(
                    Path("subdirectory") / "file0.mkv",
                    Path("subdirectory") / "file0.ass",
                ),
            ],
            listing,
        )

        # check the logger was called
        self.assertListEqual(
            logger.output,
            [
                "DEBUG:dakara_feeder.directory_lister:Listing directory",
                "DEBUG:dakara_feeder.directory_lister:Listed 4 files",
                "DEBUG:dakara_feeder.directory_lister:Found 2 different videos",
            ],
        )

    def test_list_directory_dummy(self):
        """Test to list a directory using test ressource dummy files
        """
        # call the function
        with self.assertLogs("dakara_feeder.directory_lister", "DEBUG"):
            directory = get_file("tests.resources", "")
            listing = list_directory(directory)

        # check the structure
        self.assertEqual(len(listing), 1)
        self.assertEqual(SongPaths(Path("dummy.mkv"), Path("dummy.ass")), listing[0])


class GroupByTypeTestCase(TestCase):
    """Test the group_by_type function
    """

    def test_one_video_one_subtitle(self):
        """Test to group one video and one subtitle
        """
        results = group_by_type([Path("video.mp4"), Path("video.ass")])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], SongPaths(Path("video.mp4"), Path("video.ass")))

    def test_one_video_no_subtitle(self):
        """Test to group one video and no subtitle
        """
        results = group_by_type([Path("video.mp4")])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], SongPaths(Path("video.mp4")))

    def test_one_video_one_subtitle_plus_others(self):
        """Test to group one video, one subtitle and other files
        """
        results = group_by_type(
            [
                Path("video.mp4"),
                Path("video.ass"),
                Path("video.other"),
                Path("video.dat"),
            ]
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(
            results[0],
            SongPaths(
                Path("video.mp4"),
                Path("video.ass"),
                [Path("video.other"), Path("video.dat")],
            ),
        )

    def test_one_video_two_subtitles(self):
        """Test to group one video and two subtitles
        """
        with self.assertLogs("dakara_feeder.directory_lister") as logger:
            results = group_by_type(
                [Path("video.mp4"), Path("video.ass"), Path("video.ssa")]
            )

        self.assertEqual(len(results), 0)

        self.assertListEqual(
            logger.output,
            [
                "WARNING:dakara_feeder.directory_lister:"
                "More than one subtitle for video video.mp4"
            ],
        )

    def test_no_video_no_subtitle_other(self):
        """Test to group no video, no subtitle and one other file
        """
        results = group_by_type([Path("other.dat")])

        self.assertEqual(len(results), 0)

    def test_two_videos_one_subtitle(self):
        """Test to group two videos and one subtitle
        """
        results = group_by_type(
            [Path("video.mp4"), Path("video.mkv"), Path("video.ass")]
        )

        self.assertEqual(len(results), 2)
        self.assertCountEqual(
            results,
            [
                SongPaths(Path("video.mp4"), Path("video.ass")),
                SongPaths(Path("video.mkv"), Path("video.ass")),
            ],
        )

    def test_one_video_upper_case_one_subtitle(self):
        """Test to group one video with uppercase extension and one subtitle
        """
        results = group_by_type([Path("video.MP4"), Path("video.ass")])

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], SongPaths(Path("video.MP4"), Path("video.ass")))
