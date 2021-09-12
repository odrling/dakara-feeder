import logging

from dakara_base.config import create_config_file, create_logger

from dakara_feeder.commands.base import CONFIG_FILE, Subcommand

logger = logging.getLogger(__name__)


class CreateConfigSubcommand(Subcommand):
    name = "create-config"
    description = "Create a new config file in user directory"

    def set_subparser(self, subparser):
        subparser.add_argument(
            "--force",
            help="overwrite previous config file if it exists",
            action="store_true",
        )

    def handle(self, args):
        create_logger(custom_log_format="%(message)s", custom_log_level="INFO")
        create_config_file("dakara_feeder.resources", CONFIG_FILE, args.force)
        logger.info("Please edit this file")
