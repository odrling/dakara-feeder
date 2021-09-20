from unittest import TestCase
from unittest.mock import patch

from dakara_feeder.tags_feeder import InvalidTag, TagAlreadyExistsError, TagsFeeder


@patch("dakara_feeder.tags_feeder.DakaraServer", autoset=True)
class TagsFeederTestCase(TestCase):
    """Test the TestCase class"""

    def setUp(self):
        # create base config
        self.config = {"server": {}, "kara_folder": "basepath"}

    @patch("dakara_feeder.tags_feeder.check_version", autoset=True)
    def test_load(self, mocked_check_version, mocked_dakara_server_class):
        """Test to run side-effect tasks"""
        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.load()

        # assert the call
        mocked_check_version.assert_called_with()
        mocked_dakara_server_class.return_value.authenticate.assert_called_with()

    @patch("dakara_feeder.tags_feeder.get_yaml_file_content", autoset=True)
    def test_feed(self, mocked_get_yaml_file_content, mocked_dakara_server_class):
        """Test to feed tags"""
        # create the mock
        tag = {"name": "tag1", "color_hue": 180}
        mocked_get_yaml_file_content.return_value = [tag]

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.feed()

        # assert the call
        mocked_dakara_server_class.return_value.create_tag.assert_called_with(tag)

    @patch("dakara_feeder.tags_feeder.get_yaml_file_content", autoset=True)
    def test_feed_error_no_name(
        self, mocked_get_yaml_file_content, mocked_dakara_server_class
    ):
        """Test to feed a tag without name"""
        # create the mock
        tag = {"color_hue": 180}
        mocked_get_yaml_file_content.return_value = [tag]

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaisesRegex(InvalidTag, "Tag #0 must have a name"):
            feeder.feed()

    @patch("dakara_feeder.tags_feeder.get_yaml_file_content", autoset=True)
    def test_feed_error_no_hue(
        self, mocked_get_yaml_file_content, mocked_dakara_server_class
    ):
        """Test to feed a tag without color hue"""
        # create the mock
        tag = {"name": "tag1"}
        mocked_get_yaml_file_content.return_value = [tag]

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaisesRegex(InvalidTag, "Tag #0 must have a color hue"):
            feeder.feed()

    @patch("dakara_feeder.tags_feeder.get_yaml_file_content", autoset=True)
    def test_feed_error_tag_exists(
        self, mocked_get_yaml_file_content, mocked_dakara_server_class
    ):
        """Test to feed a tag that already exists"""
        # create the mocks
        tag = {"name": "tag1", "color_hue": 180}
        mocked_get_yaml_file_content.return_value = [tag]
        mocked_dakara_server_class.return_value.create_tag.side_effect = (
            TagAlreadyExistsError
        )

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertLogs("dakara_feeder.tags_feeder", "INFO") as logger:
            feeder.feed()

        # assert the logs
        self.assertListEqual(
            logger.output,
            [
                "INFO:dakara_feeder.tags_feeder:Found 1 tags to create",
                "INFO:dakara_feeder.tags_feeder:Tag tag1 already exists on server and "
                "will not be updated",
            ],
        )
