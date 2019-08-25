import logging

import yaml
import coloredlogs
from path import Path

from dakara_feeder.exceptions import DakaraFeederError
from dakara_feeder.dakara_server import DakaraServer
from dakara_feeder.diff_generator import generate_diff
from dakara_feeder.directory_lister import list_directory
from dakara_feeder.song import Song


logger = logging.getLogger(__name__)


class DakaraFeeder:
    """Class for the Dakara feeder

    Args:
        config_name (path.Path): path to the config file.
        debug (bool): run in debug mode.

    Attributes:
        config (dict): config of the feeder.
        dakara_server (dakara_server.DakaraServer): connection to the Dakara server.
        kara_folder (path.Path): path to the folder containing karaoke files.
    """

    def __init__(self, config_name, debug):
        # get config values
        config = self.load_config(config_name, debug)

        # create objects
        self.dakara_server = DakaraServer(config["server"])
        self.kara_folder = Path(config["kara_folder"])
        self.config = config

        # side-effect actions
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

    @staticmethod
    def load_config(config_path, debug):
        """Load the config from config file

        Args:
            config_path (path.Path): path to the config file.
            debug (bool): run in debug mode.

        Returns:
            dict: dictionary of the config.
        """
        logger.info("Reading config file '{}'".format(config_path))

        # check the config file is present
        if not config_path.exists():
            raise ConfigError("No config file found")

        # load and parse the file
        with open(config_path) as file:
            try:
                config = yaml.load(file, Loader=yaml.Loader)

            except yaml.parser.ParserError as error:
                raise ConfigError("Unable to read config file") from error

        # check file content
        for key in ("server", "kara_folder"):
            if key not in config:
                raise ConfigError("Invalid config file, missing '{}'".format(key))

        # if debug is set as argument, override the config
        if debug:
            config["loglevel"] = "DEBUG"

        return config

    def configure_logger(self):
        """Set the logger config

        Set a validated logging level from configuration.
        """
        loglevel = self.config.get("loglevel")

        # if no loglevel is provided, keep the default one (info)
        if loglevel is None:
            return

        # otherwise check if it is valid and apply it
        loglevel_numeric = getattr(logging, loglevel.upper(), None)
        if not isinstance(loglevel_numeric, int):
            raise ConfigError("Invalid loglevel in config file: '{}'".format(loglevel))

        coloredlogs.set_level(loglevel_numeric)


class ConfigError(DakaraFeederError):
    """Error when reading the configuration file
    """
