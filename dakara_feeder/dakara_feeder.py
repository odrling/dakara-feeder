import logging

from path import Path

from dakara_feeder.dakara_server import DakaraServer
from dakara_feeder.diff_generator import generate_diff
from dakara_feeder.directory_lister import list_directory
from dakara_feeder.song import Song


logger = logging.getLogger(__name__)


class DakaraFeeder:
    """Class for the Dakara feeder

    Args:
        config (dict): dictionary of config.

    Attributes:
        dakara_server (dakara_server.DakaraServer): client for the Dakara server.
        kara_folder (path.Path): path to the scanned folder containing karaoke
            files.
    """

    def __init__(self, config):
        # create objects
        self.dakara_server = DakaraServer(config["server"], endpoint_prefix="api")
        self.kara_folder = Path(config["kara_folder"])

    def load(self):
        """Execute side-effect initialization tasks
        """
        self.dakara_server.authenticate()

    def feed(self):
        """Execute the feeding action
        """
        # get list of songs on the server
        old_songs = self.dakara_server.get_songs()
        logger.debug("Found %i songs in server", len(old_songs))

        old_songs_id_by_path = {song["path"]: song["id"] for song in old_songs}
        old_songs_path = list(old_songs_id_by_path.keys())

        # get list of songs on the local directory
        new_songs_paths = list_directory(self.kara_folder)
        logger.debug("Found %i songs in local directory", len(new_songs_paths))
        new_songs_video_path = [song.video for song in new_songs_paths]

        # create map of new songs
        new_songs_paths_map = {song.video: song for song in new_songs_paths}

        # compute the diffs
        added_songs_path, deleted_songs_path = generate_diff(
            old_songs_path, new_songs_video_path
        )
        logger.debug("Found %i songs to add", len(added_songs_path))
        logger.debug("Found %i songs to delete", len(deleted_songs_path))

        # songs to add
        # recover the song paths with the path of the video
        added_songs = [
            Song(self.kara_folder, new_songs_paths_map[song_path]).get_representation()
            for song_path in added_songs_path
        ]

        # songs to delete
        deleted_songs_id = [
            old_songs_id_by_path[song_path] for song_path in deleted_songs_path
        ]

        # create added songs on server
        for song in added_songs:
            self.dakara_server.post_song(song)

        # remove deleted songs on server
        for song_id in deleted_songs_id:
            self.dakara_server.delete_song(song_id)
