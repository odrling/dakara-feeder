from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.feeder.work_types import (
    WorkTypeAlreadyExistsError,
    WorkTypeInvalidError,
    WorkTypesFeeder,
)


@patch("dakara_feeder.feeder.work_types.HTTPClientDakara", autoset=True)
class WorkTypesFeederTestCase(TestCase):
    """Test the WorkTypesFeeder class."""

    def setUp(self):
        # create base config
        self.config = {"server": {}, "kara_folder": "basepath"}

    @patch("dakara_feeder.feeder.work_types.check_version", autoset=True)
    def test_load(self, mocked_check_version, mocked_http_client_class):
        """Test to run side-effect tasks."""
        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.load()

        # assert the call
        mocked_check_version.assert_called_with()
        mocked_http_client_class.return_value.authenticate.assert_called_with()

    @patch("dakara_feeder.feeder.work_types.get_yaml_file_content", autoset=True)
    def test_feed(self, mocked_get_yaml_file_content, mocked_http_client_class):
        """Test to feed work types."""
        # create the mock
        work_type = {
            "query_name": "wt1",
            "name": "Work Type 1",
            "name_plural": "Work types 1",
        }
        mocked_get_yaml_file_content.return_value = [work_type]

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.feed()

        # assert the call
        mocked_http_client_class.return_value.post_work_type.assert_called_with(
            work_type
        )

    @patch("dakara_feeder.feeder.work_types.get_yaml_file_content", autoset=True)
    def test_feed_error_no_query_name(
        self, mocked_get_yaml_file_content, mocked_http_client_class
    ):
        """Test to feed a work type without query name."""
        # create the mock
        work_type = {
            "name": "Work Type 1",
            "name_plural": "Work types 1",
            "icon_name": "icon_1",
        }
        mocked_get_yaml_file_content.return_value = [work_type]

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaisesRegex(
            WorkTypeInvalidError, "Work type #0 must have a query name"
        ):
            feeder.feed()

    @patch("dakara_feeder.feeder.work_types.get_yaml_file_content", autoset=True)
    def test_feed_error_no_name(
        self, mocked_get_yaml_file_content, mocked_http_client_class
    ):
        """Test to feed a work type without name."""
        # create the mock
        work_type = {
            "query_name": "wt1",
            "name_plural": "Work types 1",
            "icon_name": "icon_1",
        }
        mocked_get_yaml_file_content.return_value = [work_type]

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaisesRegex(
            WorkTypeInvalidError, "Work type #0 must have a name"
        ):
            feeder.feed()

    @patch("dakara_feeder.feeder.work_types.get_yaml_file_content", autoset=True)
    def test_feed_error_no_name_plural(
        self, mocked_get_yaml_file_content, mocked_http_client_class
    ):
        """Test to feed a work type without plural name."""
        # create the mock
        work_type = {"query_name": "wt1", "name": "Work Type 1", "icon_name": "icon_1"}
        mocked_get_yaml_file_content.return_value = [work_type]

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaisesRegex(
            WorkTypeInvalidError, "Work type #0 must have a plural name"
        ):
            feeder.feed()

    @patch("dakara_feeder.feeder.work_types.get_yaml_file_content", autoset=True)
    def test_feed_error_work_type_exists(
        self, mocked_get_yaml_file_content, mocked_http_client_class
    ):
        """Test to feed a work type that already exists."""
        # create the mocks
        work_type = {
            "query_name": "wt1",
            "name": "Work Type 1",
            "name_plural": "Work types 1",
            "icon_name": "icon_1",
        }
        mocked_get_yaml_file_content.return_value = [work_type]
        mocked_http_client_class.return_value.post_work_type.side_effect = (
            WorkTypeAlreadyExistsError
        )

        # create the object
        feeder = WorkTypesFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.work_types", "INFO") as logger:
            feeder.feed()

        # assert the logs
        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.feeder.work_types:Found 1 work types to create",
                "INFO:dakara_feeder.feeder.work_types:Work type wt1 already exists on "
                "server and will not be updated",
            ],
        )
