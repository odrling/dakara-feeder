from distutils.util import strtobool

from dakara_base.resources_manager import get_file
from path import Path

CONFIG_FILE = "config.yaml"


def create_config(args):
    """Create a new config file in local directory

    Args:
        args (argparse.Namespace): arguments from command line.
    """
    # get the file
    origin = get_file("dakara_feeder.resources", CONFIG_FILE)
    destination = Path(CONFIG_FILE)

    # check destination does not exist
    if not args.force and destination.exists():
        try:
            result = strtobool(
                input(
                    "{} already exists in this directory, overwrite? [y/N] ".format(
                        destination
                    )
                )
            )

        except ValueError:
            result = False

        if not result:
            return

    # copy file
    origin.copyfile(destination)
