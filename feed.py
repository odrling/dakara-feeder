#!/usr/bin/env python3
import logging
from argparse import ArgumentParser

from path import Path
from dakara_base.exceptions import DakaraError
from dakara_base.config import load_config, create_logger, set_loglevel

from dakara_feeder.dakara_feeder import DakaraFeeder


CONFIG_FILE_PATH = "config.yaml"


logger = logging.getLogger(__name__)


def get_parser():
    """Get a parser

    Returns:
        argparse.ArgumentParser: parser.
    """
    parser = ArgumentParser(description="Feeder for the Dakara project")

    parser.add_argument(
        "-d",
        "--debug",
        action="store_true",
        help="enable debug output, increase verbosity",
    )

    parser.add_argument(
        "-f", "--force", action="store_true", help="force unchanged files to be updated"
    )

    parser.add_argument(
        "--no-progress",
        dest="progress",
        action="store_false",
        help="do not display progress bars",
    )

    parser.add_argument(
        "--config",
        help="path to the config file, default: '{}'".format(CONFIG_FILE_PATH),
        default=CONFIG_FILE_PATH,
    )

    return parser


def feed(args):
    """Execute the feed action

    Args:
        args (argparse.Namespace): arguments from command line.
    """
    # prepare execution
    create_logger(wrap=True)
    config = load_config(
        Path(args.config), args.debug, mandatory_keys=["kara_folder", "server"]
    )
    set_loglevel(config)

    # do the actual feeding
    feeder = DakaraFeeder(config, force_update=args.force, progress=args.progress)
    feeder.load()
    feeder.feed()


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    try:
        feed(args)

    except KeyboardInterrupt:
        logger.info("Quit by user")
        exit(255)

    except SystemExit:
        logger.info("Quit by system")
        exit(254)

    except DakaraError as error:
        if args.debug:
            raise

        logger.critical(error)
        exit(1)

    except BaseException as error:
        if args.debug:
            raise

        logger.exception("Unexpected error: {}".format(error))
        logger.critical(
            "Please fill a bug report at "
            "https://github.com/DakaraProject/dakara-feeder/issues"
        )
        exit(128)

    exit(0)
