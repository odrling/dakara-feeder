from unittest import TestCase
from unittest.mock import call, patch

try:
    from importlib.resources import path

except ImportError:
    from importlib_resources import path

from path import Path

from dakara_feeder.feeder.works import WorksFeeder


@patch("dakara_feeder.feeder.works.HTTPClientDakara", autoset=True)
class WorksFeederIntegrationTestCase(TestCase):
    """Integration test for the WorksFeeder class."""

    def setUp(self):
        self.config = {"server": {}}

    def test_correct_work_file(self, mocked_http_client_dakara_class):
        """Test to feed correct work file."""
        # create the mocks
        mocked_http_client_dakara_class.return_value.retrieve_works.return_value = [
            {
                "id": 1,
                "title": "Work 1",
                "subtitle": "Subtitle 1",
                "work_type": {"query_name": "WorkType 1"},
            },
            {
                "id": 2,
                "title": "Work 2",
                "subtitle": "Subtitle 2",
                "work_type": {"query_name": "WorkType 1"},
            },
        ]

        # create the object
        with path(
            "tests.integration.resources.works", "correct_work_file.json"
        ) as filepath:
            feeder = WorksFeeder(self.config, Path(filepath), progress=False)

            # call the method
            with self.assertLogs("dakara_feeder.feeder.works", "DEBUG"):
                with self.assertLogs("dakara_base.progress_bar"):
                    feeder.feed()

        mocked_http_client_dakara_class.return_value.post_work.assert_called_with(
            [
                {
                    "title": "Work 3",
                    "alternative_titles": [
                        {"title": "AltTitle 1"},
                        {"title": "AltTitle 3"},
                    ],
                    "work_type": {"query_name": "WorkType 1"},
                }
            ]
        )
        mocked_http_client_dakara_class.return_value.put_work.assert_has_calls(
            [
                call(
                    1,
                    {
                        "title": "Work 1",
                        "subtitle": "Subtitle 1",
                        "alternative_titles": [
                            {"title": "AltTitle 1"},
                            {"title": "AltTitle 2"},
                        ],
                        "work_type": {"query_name": "WorkType 1"},
                    },
                ),
                call(
                    2,
                    {
                        "title": "Work 2",
                        "subtitle": "Subtitle 2",
                        "work_type": {"query_name": "WorkType 1"},
                    },
                ),
            ],
            any_order=True,
        )
