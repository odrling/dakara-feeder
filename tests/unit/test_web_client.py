from unittest import TestCase
from unittest.mock import ANY, patch

from path import Path

from dakara_feeder import web_client


class HTTPClientDakaraTestCase(TestCase):
    """Test the HTTP client."""

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

    @patch.object(web_client.HTTPClientDakara, "get", autoset=True)
    def test_get_songs(self, mocked_get):
        """Test to obtain the list of song paths."""
        # create the mock
        mocked_get.return_value = [
            {"filename": "song_0.mp4", "directory": "directory_0", "id": 0},
            {"filename": "song_1.mp4", "directory": "directory_1", "id": 1},
        ]

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        songs_list = http_client.get_songs()

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

    @patch.object(web_client.HTTPClientDakara, "post", autoset=True)
    def test_post_song(self, mocked_post):
        """Test to create one song on the server."""
        # create song
        song = {
            "title": "title_0",
            "filename": "song_0.mp4",
            "directory": "directory_0",
            "duration": 42,
        }

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        http_client.post_song(song)

        # assert the mock
        mocked_post.assert_called_with("library/songs/", json=song)

    @patch.object(web_client.HTTPClientDakara, "delete", autoset=True)
    def test_delete_song(self, mocked_delete):
        """Test to delete one song on the server."""
        # create song ID
        song_id = 42

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        http_client.delete_song(song_id)

        # assert the mock
        mocked_delete.assert_called_with("library/songs/42/")

    @patch.object(web_client.HTTPClientDakara, "put", autoset=True)
    def test_put_song(self, mocked_put):
        """Test to update one song on the server."""
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
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        http_client.put_song(song_id, song)

        # assert the mock
        mocked_put.assert_called_with("library/songs/42/", json=song)

    @patch.object(web_client.HTTPClientDakara, "delete", autoset=True)
    def test_prune_artists(self, mocked_delete):
        """Test to prune artists"""
        # mock objects
        mocked_delete.return_value = {"deleted_count": 2}

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        deleted_count = http_client.prune_artists()

        # assert the value
        self.assertEqual(deleted_count, 2)

        # assert the mock
        mocked_delete.assert_called_with("library/artists/prune/")

    @patch.object(web_client.HTTPClientDakara, "delete", autoset=True)
    def test_prune_works(self, mocked_delete):
        """Test to prune works"""
        # mock objects
        mocked_delete.return_value = {"deleted_count": 2}

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # call the method
        deleted_count = http_client.prune_works()

        # assert the value
        self.assertEqual(deleted_count, 2)

        # assert the mock
        mocked_delete.assert_called_with("library/works/prune/")

    @patch.object(web_client.HTTPClientDakara, "post", autoset=True)
    def test_create_tag(self, mocked_post):
        """Test to create tag"""
        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # create tag
        tag = {"name": "tag1", "color_hue": 250}

        # call the method
        http_client.create_tag(tag)

        # assert the call
        mocked_post.assert_called_with("library/song-tags/", tag, function_on_error=ANY)

    @patch("dakara_base.http_client.requests.post", autoset=True)
    def test_create_tag_error_already_exists(self, mocked_post):
        """Test to create tag that already exists"""
        # create the mock
        mocked_post.return_value.ok = False
        mocked_post.return_value.status_code = 400

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # artificially connect the server
        http_client.token = "token"

        # create tag
        tag = {"name": "tag1", "color_hue": 250}

        # call the method
        with self.assertRaises(web_client.TagAlreadyExistsError):
            http_client.create_tag(tag)

        # assert the call
        mocked_post.assert_called_with(
            self.url + "library/song-tags/", tag, headers=ANY
        )

    @patch("dakara_base.http_client.requests.post", autoset=True)
    def test_create_tag_error_other(self, mocked_post):
        """Test an unknown problem when creating a tag"""
        # create the mock
        mocked_post.return_value.ok = False
        mocked_post.return_value.status_code = 999
        mocked_post.return_value.text = "error message"

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # artificially connect the server
        http_client.token = "token"

        # create tag
        tag = {"name": "tag1", "color_hue": 250}

        # call the method
        with self.assertRaises(web_client.ResponseInvalidError) as error:
            http_client.create_tag(tag)

        # assert the error
        self.assertEqual(
            str(error.exception),
            "Error 999 when communicating with the server: error message",
        )

    @patch.object(web_client.HTTPClientDakara, "post", autoset=True)
    def test_create_work_type(self, mocked_post):
        """Test to create work type"""
        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # create work type
        work_type = {"query_name": "wt1", "name": "Work Type 1"}

        # call the method
        http_client.create_work_type(work_type)

        # assert the call
        mocked_post.assert_called_with(
            "library/work-types/", work_type, function_on_error=ANY
        )

    @patch("dakara_base.http_client.requests.post", autoset=True)
    def test_create_work_type_error_already_exists(self, mocked_post):
        """Test to create work type that already exists"""
        # create the mock
        mocked_post.return_value.ok = False
        mocked_post.return_value.status_code = 400

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # artificially connect the server
        http_client.token = "token"

        # create work type
        work_type = {"query_name": "wt1", "name": "Work Type 1"}

        # call the method
        with self.assertRaises(web_client.WorkTypeAlreadyExistsError):
            http_client.create_work_type(work_type)

        # assert the call
        mocked_post.assert_called_with(
            self.url + "library/work-types/", work_type, headers=ANY
        )

    @patch("dakara_base.http_client.requests.post", autoset=True)
    def test_create_work_type_error_other(self, mocked_post):
        """Test an unknown problem when creating a work type"""
        # create the mock
        mocked_post.return_value.ok = False
        mocked_post.return_value.status_code = 999
        mocked_post.return_value.text = "error message"

        # create the object
        http_client = web_client.HTTPClientDakara(
            self.config, endpoint_prefix=self.endpoint_prefix
        )

        # artificially connect the server
        http_client.token = "token"

        # create work type
        work_type = {"query_name": "wt1", "name": "Work Type 1"}

        # call the method
        with self.assertRaisesRegex(
            web_client.ResponseInvalidError,
            "Error 999 when communicating with the server: error message",
        ):
            http_client.create_work_type(work_type)
