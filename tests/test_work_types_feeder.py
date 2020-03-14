from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.work_types_feeder import (
    WorkTypesFeeder,
    WorkTypeInvalidError,
    WorkTypeAlreadyExistsError,
)


@patch("dakara_feeder.work_types_feeder.DakaraServer", autoset=True)
class WorkTypesFeederTestCase(TestCase):
    """Test the WorkTypesFeeder class
    """

    def setUp(self):
        # create base config
        self.config = {"server": {}, "kara_folder": "basepath"}

    @patch("dakara_feeder.work_types_feeder.check_version", autoset=True)
    def test_load(self, mocked_check_version, mocked_dakara_server_class):
        """Test to run side-effect tasks
        """
        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.load()

        # assert the call
        mocked_check_version.assert_called_with()
        mocked_dakara_server_class.return_value.authenticate.assert_called_with()

    @patch("dakara_feeder.work_types_feeder.get_yaml_file_content", autoset=True)
    def test_feed(self, mocked_get_yaml_file_content, mocked_dakara_server_class):
        """Test to feed work types
        """
        # create the mock
        work_type = {"query_name": "wt1", "name": "Work Type 1", "icon_name": "icon_1"}
        mocked_get_yaml_file_content.return_value = [work_type]

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.feed()

        # assert the call
        mocked_dakara_server_class.return_value.create_work_type.assert_called_with(
            work_type
        )

    @patch("dakara_feeder.work_types_feeder.get_yaml_file_content", autoset=True)
    def test_feed_error_no_query_name(
        self, mocked_get_yaml_file_content, mocked_dakara_server_class
    ):
        """Test to feed a work type without name
        """
        # create the mock
        work_type = {"name": "Work Type 1", "icon_name": "icon_1"}
        mocked_get_yaml_file_content.return_value = [work_type]

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaises(WorkTypeInvalidError) as error:
            feeder.feed()

        # assert the error
        self.assertEqual(str(error.exception), "Work type 0 must have a query name")

    @patch("dakara_feeder.work_types_feeder.get_yaml_file_content", autoset=True)
    def test_feed_error_work_type_exists(
        self, mocked_get_yaml_file_content, mocked_dakara_server_class
    ):
        """Test to feed a work type that already exists
        """
        # create the mocks
        work_type = {"query_name": "wt1", "name": "Work Type 1", "icon_name": "icon_1"}
        mocked_get_yaml_file_content.return_value = [work_type]
        mocked_dakara_server_class.return_value.create_work_type.side_effect = (
            WorkTypeAlreadyExistsError
        )

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.work_types_feeder", "INFO") as logger:
            feeder.feed()

        # assert the logs
        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.work_types_feeder:Work type wt1 already exists on "
                "server and will not be updated"
            ],
        )
