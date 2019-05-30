from argparse import ArgumentParser

import yaml
import coloredlogs
from path import Path

from dakara_feeder.dakara_server import DakaraServer
from dakara_feeder.diff_generator import generate_diff
from dakara_feeder.directory_lister import list_directory
from dakara_feeder.song import Song


CONFIG_FILE_PATH = "config.yaml"


class Feeder:
    def __init__(self, config_name, debug):
        # get config values
        config = self.load_config(config_name, debug)

        # create objects
        self.dakara_server = DakaraServer(config["server"])
        self.kara_folder = config["kara_folder"]

        # side-effect actions
        self.dakara_server.authenticate()

    def feed(self):
        """Execute the feeding action
        """
        # get list of songs on the server
        old_songs_path = self.dakara_server.get_songs()

        # get list of songs on the local directory
        new_songs_path = list_directory(self.kara_folder)

        # compute the diffs
        added_songs_path, deleted_songs_path = generate_diff(old_songs_path, new_songs_path)

        # songs to add
        added_songs = [Song(song_path).get_representation() for song_path in added_songs_path]

        # songs to delete
        deleted_songs_path_object = [Path(song_path) for song_path in deleted_songs_path]
        deleted_songs = [{"filename": song_path.basename(), "directory": song_path.dirname()} for song_path in deleted_songs_path_object]

        # send the two lists to server
        self.dakara_server.post_songs_diff(added_songs, deleted_songs)

    @staticmethod
    def load_config(config_path, debug):
        """Load the config from config file

        Args:
            config_path (str): path to the config file.
            debug (bool): run in debug mode.

        Returns:
            dict: dictionary of the config.
        """
        logger.info("Reading config file '{}'".format(config_path))

        # check the config file is present
        if not os.path.isfile(config_path):
            raise IOError("No config file found")

        # load and parse the file
        with open(config_path) as file:
            try:
                config = yaml.load(file, Loader=yaml.Loader)

            except yaml.parser.ParserError as error:
                raise IOError("Unable to read config file") from error

        # check file content
        for key in ("server", "kara_folder"):
            if key not in config:
                raise ValueError("Invalid config file, missing '{}'".format(key))

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
            raise ValueError("Invalid loglevel in config file: '{}'".format(loglevel))

        coloredlogs.set_level(loglevel_numeric)


def get_parser():
    parser = ArgumentParser(description="Feeder for the Dakara project")

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug output, increase verbosity",
    )

    parser.add_argument(
        "--config",
        help="path to the config file, default: '{}'".format(CONFIG_FILE_PATH),
        default=CONFIG_FILE_PATH,
    )

    return parser


def feed(args):
    feeder = Feeder(args.config, args.debug)
    feeder.feed()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
