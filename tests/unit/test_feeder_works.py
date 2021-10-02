from unittest import TestCase
from unittest.mock import call, patch

from path import Path

from dakara_feeder.feeder.works import WorksFeeder


@patch("dakara_feeder.feeder.works.HTTPClientDakara", autoset=True)
class WorksFeederTestCase(TestCase):
    """Test the feeder class."""

    def setUp(self):
        # create base config
        self.config = {"server": {}}

        # create works file path
        self.works_file_path = Path("works")

    @patch("dakara_feeder.feeder.works.check_version", autoset=True)
    def test_load(
        self,
        mocked_check_version,
        mocked_http_client_class,
    ):
        """Test to run side-effect tasks."""
        # create the object
        feeder = WorksFeeder(self.config, self.works_file_path, progress=False)

        # call the method
        feeder.load()

        # assert the call
        mocked_check_version.assert_called_with()
        mocked_http_client_class.return_value.authenticate.assert_called_with()

    @patch("dakara_feeder.feeder.works.get_json_file_content")
    def test_feed(self, mocked_get_json_file_content, mocked_http_client_class):
        """Test to feed."""
        mocked_http_client_class.return_value.retrieve_works.return_value = [
            {
                "id": 0,
                "title": "Work 0",
                "subtitle": "",
                "work_type": {"query_name": "anime"},
            },
            {
                "id": 1,
                "title": "Work 1",
                "subtitle": "subtitle",
                "work_type": {"query_name": "anime"},
            },
        ]
        mocked_get_json_file_content.return_value = {
            "anime": [
                {
                    "title": "Work 0",
                    "subtitle": "",
                },
                {
                    "title": "Work 1",
                    "subtitle": "subtitle",
                    "alternavite_titles": [{"title": "Work 01"}, {"title": "Work 001"}],
                },
                {
                    "title": "Work 2",
                    "subtitle": "",
                },
            ]
        }

        # create the object
        feeder = WorksFeeder(self.config, self.works_file_path, progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.feeder.works", "DEBUG") as logger_feeder:
            with self.assertLogs("dakara_base.progress_bar") as logger_progress:
                feeder.feed()

        # assert the mocks
        mocked_http_client_class.return_value.retrieve_works.assert_called_with()
        mocked_get_json_file_content.assert_called_with(Path("works"))
        mocked_http_client_class.return_value.post_work.assert_has_calls(
            [
                call(
                    {
                        "title": "Work 2",
                        "subtitle": "",
                        "work_type": {"query_name": "anime"},
                    }
                )
            ]
        )
        mocked_http_client_class.return_value.put_work.assert_has_calls(
            [
                call(
                    0,
                    {
                        "title": "Work 0",
                        "subtitle": "",
                        "work_type": {"query_name": "anime"},
                    },
                ),
                call(
                    1,
                    {
                        "title": "Work 1",
                        "subtitle": "subtitle",
                        "alternavite_titles": [
                            {"title": "Work 01"},
                            {"title": "Work 001"},
                        ],
                        "work_type": {"query_name": "anime"},
                    },
                ),
            ],
            any_order=True,
        )

        # assert the logs
        self.assertListEqual(
            logger_feeder.output,
            [
                "INFO:dakara_feeder.feeder.works:Found 2 works in server",
                "INFO:dakara_feeder.feeder.works:Found 1 work types and 3 "
                "works to create",
            ],
        )
        self.assertListEqual(
            logger_progress.output,
            [
                "INFO:dakara_base.progress_bar:Checking works",
                "INFO:dakara_base.progress_bar:Uploading added works",
                "INFO:dakara_base.progress_bar:Uploading updated works",
            ],
        )

    @patch("dakara_feeder.feeder.works.get_json_file_content")
    def test_feed_update_only(
        self, mocked_get_json_file_content, mocked_http_client_class
    ):
        """Test to feed updated works only."""
        mocked_http_client_class.return_value.retrieve_works.return_value = [
            {
                "id": 0,
                "title": "Work 0",
                "subtitle": "",
                "work_type": {"query_name": "anime"},
            },
            {
                "id": 1,
                "title": "Work 1",
                "subtitle": "subtitle",
                "work_type": {"query_name": "anime"},
            },
        ]
        mocked_get_json_file_content.return_value = {
            "anime": [
                {
                    "title": "Work 0",
                    "subtitle": "",
                },
                {
                    "title": "Work 1",
                    "subtitle": "subtitle",
                    "alternavite_titles": [{"title": "Work 01"}, {"title": "Work 001"}],
                },
                {
                    "title": "Work 2",
                    "subtitle": "",
                },
            ]
        }

        # create the object
        feeder = WorksFeeder(
            self.config, self.works_file_path, update_only=True, progress=False
        )

        # call the method
        with self.assertLogs("dakara_feeder.feeder.works", "DEBUG"):
            with self.assertLogs("dakara_base.progress_bar"):
                feeder.feed()

        # assert the mocks
        mocked_http_client_class.return_value.post_work.assert_not_called()
