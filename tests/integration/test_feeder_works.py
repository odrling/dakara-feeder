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

    def test_correct_work_file(self, mocked_dakara_server_class):
        """Test to feed correct work file."""
        # create the mocks
        mocked_dakara_server_class.return_value.retrieve_songs.return_value = []

        # create the object
        with path(
            "tests.integration.resources.works", "correct_work_file.json"
        ) as filepath:
            feeder = WorksFeeder(self.config, Path(filepath), progress=False)

            # call the method
            with self.assertLogs("dakara_feeder.feeder.works", "DEBUG"):
                with self.assertLogs("dakara_base.progress_bar"):
                    feeder.feed()

        mocked_dakara_server_class.return_value.post_work.assert_has_calls(
            [
                call(
                    {
                        "title": "Work 1",
                        "subtitle": "Subtitle 1",
                        "alternative_titles": ["AltTitle 1", "AltTitle 2"],
                        "work_type": {"query_name": "WorkType 1"},
                    }
                ),
                call(
                    {
                        "title": "Work 2",
                        "subtitle": "Subtitle 2",
                        "work_type": {"query_name": "WorkType 1"},
                    }
                ),
                call(
                    {
                        "title": "Work 3",
                        "alternative_titles": ["AltTitle 1", "AltTitle 3"],
                        "work_type": {"query_name": "WorkType 1"},
                    }
                ),
            ],
            any_order=True,
        )
