"""Feeder for songs."""

import logging

from dakara_base.exceptions import DakaraError
from dakara_base.progress_bar import null_bar, progress_bar
from path import Path

from dakara_feeder.customization import get_custom_song
from dakara_feeder.difference import generate_diff, match_similar
from dakara_feeder.directory import list_directory
from dakara_feeder.similarity import calculate_file_path_similarity
from dakara_feeder.song import BaseSong
from dakara_feeder.utils import divide_chunks
from dakara_feeder.version import check_version
from dakara_feeder.web_client import HTTPClientDakara

logger = logging.getLogger(__name__)


SONGS_PER_CHUNK = 100


class SongsFeeder:
    """Class to feed the Dakara server database with songs.

    Args:
        config (dict): Dictionary of config.
        force_update (bool): If `True`, the feeder will re-parse and re-upload
            songs that do not seem to have changed.
        prune (bool): If `True`, artists and works without songs are deleted at
            the end.
        progress (bool): If `True`, a progress bar is displayed during long tasks.

    Attributes:
        http_client (web_client.HTTPClientDakara): Client for the Dakara server.
        kara_folder_path (path.Path): Path to the scanned folder containing karaoke
            files.
        songs_per_chunk (int): Number of songs per chunk to send to server when
            creating songs.
        bar (function): Progress bar to use.
        song_class_module_name (str): Module name of the custom song class to
            use.
        song_class (type): Custom song class to use. Must be a subclass of
            `dakara_feeder.song.BaseSong`.
    """

    def __init__(self, config, force_update=False, prune=True, progress=True):
        # create objects
        self.http_client = HTTPClientDakara(config["server"], endpoint_prefix="api")
        self.kara_folder_path = Path(config["kara_folder"])
        self.force_update = force_update
        self.prune = prune
        self.songs_per_chunk = config["server"].get("songs_per_chunk", SONGS_PER_CHUNK)
        self.bar = progress_bar if progress else null_bar
        self.song_class_module_name = config.get("custom_song_class")
        self.song_class = BaseSong

    def load(self):
        """Execute side-effect initialization tasks."""
        # check version
        check_version()

        # select song class
        if self.song_class_module_name:
            self.song_class = get_custom_song(self.song_class_module_name)

        # check directory exists
        self.check_kara_folder_path()

        # authenticate to server
        self.http_client.load()
        self.http_client.authenticate()

    def check_kara_folder_path(self):
        """Check the kara folder is valid.

        Raises:
            KaraFolderNotFound: If the karaoke folder does not exist.
        """
        if not self.kara_folder_path.isdir():
            raise KaraFolderNotFound(
                "Karaoke folder '{}' does not exist".format(self.kara_folder_path)
            )

    def feed(self):
        """Execute the feeding action."""
        # get list of songs on the server
        old_songs = self.http_client.retrieve_songs()
        logger.info("Found %i songs in server", len(old_songs))

        old_songs_id_by_path = {song["path"]: song["id"] for song in old_songs}
        old_songs_path = list(old_songs_id_by_path.keys())

        # get list of songs on the local directory
        new_songs_paths = list_directory(self.kara_folder_path)
        logger.info("Found %i songs in local directory", len(new_songs_paths))
        new_songs_video_path = [song.video for song in new_songs_paths]

        # create map of new songs
        new_songs_paths_map = {song.video: song for song in new_songs_paths}

        # compute the diffs
        added_songs_path, deleted_songs_path, unchanged_songs_path = generate_diff(
            old_songs_path, new_songs_video_path
        )

        # try to find renamed/moved files
        updated_songs_path, added_songs_path, deleted_songs_path = match_similar(
            added_songs_path, deleted_songs_path, calculate_file_path_similarity
        )

        # when force_update is true, unchanged files are added to update list
        if self.force_update:
            updated_songs_path.extend([(path, path) for path in unchanged_songs_path])

        logger.info("Found %i songs to add", len(added_songs_path))
        logger.info("Found %i songs to delete", len(deleted_songs_path))
        logger.info("Found %i songs to update", len(updated_songs_path))

        # songs to add
        # recover the song paths with the path of the video
        added_songs = []
        if added_songs_path:
            added_songs = [
                self.song_class(
                    self.kara_folder_path, new_songs_paths_map[song_path]
                ).get_representation()
                for song_path in self.bar(added_songs_path, text="Parsing songs to add")
            ]

        # songs to update
        # recover the song paths with the path of the video
        updated_songs = []
        if updated_songs_path:
            updated_songs = [
                (
                    self.song_class(
                        self.kara_folder_path, new_songs_paths_map[new_song_path]
                    ).get_representation(),
                    old_songs_id_by_path[old_song_path],
                )
                for new_song_path, old_song_path in self.bar(
                    updated_songs_path, text="Parsing songs to update"
                )
            ]

        # create added songs on server
        # send them by chunks
        if added_songs:
            for songs_chunk in self.bar(
                list(divide_chunks(added_songs, self.songs_per_chunk)),
                text="Uploading added songs",
            ):
                self.http_client.post_song(songs_chunk)

        # update renamed songs on server
        if updated_songs:
            for song, song_id in self.bar(
                updated_songs, text="Uploading updated songs"
            ):
                self.http_client.put_song(song_id, song)

        # remove deleted songs on server
        if deleted_songs_path:
            for song_path in self.bar(
                deleted_songs_path, text="Deleting removed songs"
            ):
                self.http_client.delete_song(old_songs_id_by_path[song_path])

        # prune artists and works without songs
        if self.prune:
            artists_deleted_count = self.http_client.prune_artists()
            logger.info(
                "Deleted %i artists without songs on server", artists_deleted_count
            )

            works_deleted_count = self.http_client.prune_works()
            logger.info("Deleted %i works without songs on server", works_deleted_count)


class KaraFolderNotFound(DakaraError):
    """Error raised when the kara folder cannot be found."""
