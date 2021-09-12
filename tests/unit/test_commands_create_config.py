from argparse import Namespace
from unittest import TestCase
from unittest.mock import ANY, patch

from dakara_feeder.commands.create_config import CreateConfigSubcommand


class CreateConfigTestCase(TestCase):
    """Test the create-config subcommand
    """

    @patch("dakara_feeder.commands.create_config.CONFIG_FILE", "feeder.yaml")
    @patch("dakara_feeder.commands.create_config.create_logger")
    @patch("dakara_feeder.commands.create_config.create_config_file")
    def test_create_config(self, mocked_create_config_file, mocked_create_logger):
        """Test a normall config creation
        """
        subcommand = CreateConfigSubcommand()

        # call the function
        with self.assertLogs("dakara_feeder.commands.create_config") as logger:
            subcommand.handle(Namespace(force=False))

        # assert the logs
        self.assertListEqual(
            logger.output,
            ["INFO:dakara_feeder.commands.create_config:Please edit this file"],
        )

        # assert the call
        mocked_create_logger.assert_called_with(
            custom_log_format=ANY, custom_log_level=ANY
        )
        mocked_create_config_file.assert_called_with(
            "dakara_feeder.resources", "feeder.yaml", False
        )
