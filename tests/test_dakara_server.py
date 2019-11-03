from unittest import TestCase
from unittest.mock import patch

from path import Path

from dakara_feeder import dakara_server


class DakaraServerTestCase(TestCase):
    """Test the Dakara client
    """

    def setUp(self):
        # create a server address
        self.address = "www.example.com"

        # create route
        self.endpoint_prefix = "api"

        # create a server URL
        self.url = "http://www.example.com/api/"

        # create a login and password
        self.login = "test"
        self.password = "test"

        # create config
        self.config = {
            "login": self.login,
            "password": self.password,
            "address": self.address,
        }

    @patch.object(dakara_server.DakaraServer, "get", autoset=True)
    def test_get_songs(self, mocked_get):
        """Test to obtain the list of song paths
        """
        # create the mock
        mocked_get.return_value = [
            {"filename": "song_0.mp4", "directory": "directory_0", "id": 0},
            {"filename": "song_1.mp4", "directory": "directory_1", "id": 1},
        ]

        # create the object
        server = dakara_server.DakaraServer(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        songs_list = server.get_songs()

        # assert the songs are present and filename and directory is joined
        self.assertCountEqual(
            songs_list,
            [
                {"path": Path("directory_0") / "song_0.mp4", "id": 0},
                {"path": Path("directory_1") / "song_1.mp4", "id": 1},
            ],
        )

        # assert the mock
        mocked_get.assert_called_with("library/feeder/retrieve/")

    @patch.object(dakara_server.DakaraServer, "post", autoset=True)
    def test_post_song(self, mocked_post):
        """Test to create one song on the server
        """
        # create song
        song = {
            "title": "title_0",
            "filename": "song_0.mp4",
            "directory": "directory_0",
            "duration": 42,
        }

        # create the object
        server = dakara_server.DakaraServer(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        server.post_song(song)

        # assert the mock
        mocked_post.assert_called_with("library/songs/", json=song)

    @patch.object(dakara_server.DakaraServer, "delete", autoset=True)
    def test_delete_song(self, mocked_delete):
        """Test to delete one song on the server
        """
        # create song ID
        song_id = 42

        # create the object
        server = dakara_server.DakaraServer(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        server.delete_song(song_id)

        # assert the mock
        mocked_delete.assert_called_with("library/songs/42/")

    @patch.object(dakara_server.DakaraServer, "put", autoset=True)
    def test_put_song(self, mocked_put):
        """Test to update one song on the server
        """
        # create song ID
        song_id = 42

        # create song
        song = {
            "title": "title_0",
            "filename": "song_0.mp4",
            "directory": "directory_0",
            "duration": 42,
        }

        # create the object
        server = dakara_server.DakaraServer(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        server.put_song(song_id, song)

        # assert the mock
        mocked_put.assert_called_with("library/songs/42/", json=song)
