from abc import ABC, abstractmethod

from dakara_base.config import (
    ConfigNotFoundError,
    create_logger,
    get_config_file,
    load_config,
    set_loglevel,
)
from dakara_base.exceptions import DakaraError

CONFIG_FILE = "feeder.yaml"


class Subcommand(ABC):
    name = ""
    description = ""

    def create_subparser(self, subparsers):
        """Add a subparser for the subcommand

        Args:
            subparsers (argparse._SubParserAction): subparsers manager of the
                main parser.
        """
        subparser = subparsers.add_parser(
            self.name, description=self.description, help=self.description
        )

        subparser.set_defaults(function=self.handle)

        self.set_subparser(subparser)

    def set_subparser(self, subparser):
        """Set the subparser.

        Args:
            subparser (argparse.ArgumentParser): subparser.
        """
        pass

    @abstractmethod
    def handle(self, args):
        """Handle the action of the command

        This method is abstract and must be overriden.

        Args:
            args (argparse.Namespace): arguments from command line.
        """

    @staticmethod
    def load_config(debug=False):
        """Securely load the config

        Display help to create config if it fails.

        Args:
            debug (bool): enable debug mode.

        Returns:
            dict: config values.
        """
        create_logger(wrap=True)

        try:
            config = load_config(
                get_config_file(CONFIG_FILE),
                debug,
                mandatory_keys=["kara_folder", "server"],
            )

        except ConfigNotFoundError as error:
            raise ConfigNotFoundError(
                "{}, please run 'dakara-feed create-config'".format(error)
            ) from error

        set_loglevel(config)

        return config

    @staticmethod
    def load_feeder(feeder):
        """Securely load the feeder

        Consider that the config is incomplete if it fails.
        """
        try:
            feeder.load()

        except DakaraError as error:
            error.args = (
                "{}\nConfig may be incomplete, please check '{}'".format(
                    str(error), get_config_file(CONFIG_FILE)
                ),
            )
            raise
