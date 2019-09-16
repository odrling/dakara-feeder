import logging

from dakara_base.http_client import HTTPClient
from path import Path


logger = logging.getLogger(__name__)


class DakaraServer(HTTPClient):
    """Client to the Dakara server
    """

    def get_songs(self):
        """Retreive the songs of the library containing their path

        Returns:
            list: list of path on the songs.
        """
        endpoint = "library/feeder/retrieve/"
        songs = self.get(endpoint)

        # join the directory and the filename
        return [
            {"path": Path(song["directory"]) / song["filename"], "id": song["id"]}
            for song in songs
        ]

    def post_song(self, song):
        """Create one or several songs on the server

        Args:
            song (dict or list of dict): new song(s) representation.
        """
        endpoint = "library/songs/"
        self.post(endpoint, json=song)

    def delete_song(self, song_id):
        """Delete one song on the server

        Args:
            song_id (int): ID of the song to delete.
        """
        endpoint = "library/songs/{}/".format(song_id)
        self.delete(endpoint)

    def put_song(self, song_id, song):
        """Update one song on the server

        Args:
            song_id (int): ID of the song to update.
            song (dict): song representation.
        """
        endpoint = "library/songs/{}/".format(song_id)
        self.put(endpoint, json=song)
