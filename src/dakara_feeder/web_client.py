"""HTTP client for the Dakara server."""

import logging

from dakara_base.http_client import HTTPClient, ResponseInvalidError
from path import Path

logger = logging.getLogger(__name__)


class HTTPClientDakara(HTTPClient):
    """Client to communicate with the Dakara server."""

    def retrieve_songs(self):
        """Retreive the songs of the library containing their path.

        Returns:
            list: List of path on the songs.
        """
        endpoint = "library/songs/retrieve/"
        songs = self.get(endpoint)

        # join the directory and the filename
        return [
            {"path": Path(song["directory"]) / song["filename"], "id": song["id"]}
            for song in songs
        ]

    def post_song(self, song):
        """Create one or several songs on the server.

        Args:
            song (dict or list of dict): New song(s) representation.
        """
        endpoint = "library/songs/"
        self.post(endpoint, json=song)

    def put_song(self, song_id, song):
        """Update one song on the server.

        Args:
            song_id (int): ID of the song to update.
            song (dict): Song representation.
        """
        endpoint = "library/songs/{}/".format(song_id)
        self.put(endpoint, json=song)

    def delete_song(self, song_id):
        """Delete one song on the server.

        Args:
            song_id (int): ID of the song to delete.
        """
        endpoint = "library/songs/{}/".format(song_id)
        self.delete(endpoint)

    def prune_artists(self):
        """Prune artists without songs.

        Returns:
            int: Number of deleted artists.
        """
        endpoint = "library/artists/prune/"
        return self.delete(endpoint)["deleted_count"]

    def retrieve_works(self):
        """Retreive the works of the library with minimal data.

        Returns:
            list: List of works.
        """
        endpoint = "library/works/retrieve/"
        return self.get(endpoint)

    def post_work(self, work):
        """Create one or several works on the server.

        Args:
            work (dict or list of dict): New work(s) representation.
        """
        endpoint = "library/works/"
        self.post(endpoint, json=work)

    def put_work(self, work_id, work):
        """Update one work on the server.

        Args:
            work_id (int): ID of the work to update.
            work (dict): Work representation.
        """
        endpoint = "library/works/{}/".format(work_id)
        self.put(endpoint, json=work)

    def prune_works(self):
        """Prune works without songs.

        Return:
            int: Number of deleted works.
        """
        endpoint = "library/works/prune/"
        return self.delete(endpoint)["deleted_count"]

    def post_tag(self, tag):
        """Create a tag on the server.

        Args:
            tag (dict): JSON representation of a tag.

        Raises:
            TagAlreadyExistsError: If the tag exists on the server, i.e. if the
                server returns 400.
            dakara_base.http_client.ResponseInvalidError: If the response of
                the server is not OK.
        """

        def on_error(response):
            if response.status_code == 400:
                return TagAlreadyExistsError()

            return ResponseInvalidError(
                "Error {} when communicating with the server: {}".format(
                    response.status_code, response.text
                )
            )

        endpoint = "library/song-tags/"
        self.post(endpoint, tag, function_on_error=on_error)

    def post_work_type(self, work_type):
        """Create a work type on the server.

        Args:
            work_type (dict): JSON representation of a work type.

        Raises:
            WorkTypeAlreadyExistsError: If the work type exists on the server,
                i.e. if the server returns 400.
            dakara_base.http_client.ResponseInvalidError: If the response of
                the server is not OK.
        """

        def on_error(response):
            if response.status_code == 400:
                return WorkTypeAlreadyExistsError()

            return ResponseInvalidError(
                "Error {} when communicating with the server: {}".format(
                    response.status_code, response.text
                )
            )

        endpoint = "library/work-types/"
        self.post(endpoint, work_type, function_on_error=on_error)


class TagAlreadyExistsError(Exception):
    """Error if a tag already exists."""


class WorkTypeAlreadyExistsError(Exception):
    """Error if a work type already exists."""
