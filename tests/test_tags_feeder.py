from unittest import TestCase
from unittest.mock import patch

from yaml import YAMLError
from path import Path

from dakara_feeder.tags_feeder import (
    TagsFeeder,
    InvalidTag,
    InvalidTagsFile,
    TagsFileNotFound,
    TagAlreadyExistsError,
)


@patch("dakara_feeder.tags_feeder.DakaraServer", autoset=True)
class TagsFeederTestCase(TestCase):
    """Test the TestCase class
    """

    def setUp(self):
        # create base config
        self.config = {"server": {}, "kara_folder": "basepath"}

    @patch("dakara_feeder.tags_feeder.check_version", autoset=True)
    def test_load(self, mocked_check_version, mocked_dakara_server_class):
        """Test to run side-effect tasks
        """
        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.load()

        # assert the call
        mocked_check_version.assert_called_with()
        mocked_dakara_server_class.return_value.authenticate.assert_called_with()

    @patch.object(Path, "text", autoset=True)
    def test_get_tags_file_content(self, mocked_text, mocked_dakara_server_class):
        """Test to get a tags file
        """
        # create the mock
        tags = [{"name": "tag1"}]
        mocked_text.return_value = str(tags)

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        content = feeder.get_tags_file_content()

        # assert the result
        self.assertListEqual(content, tags)

        # assert the call
        mocked_text.assert_called_with()

    @patch.object(Path, "text", autoset=True)
    def test_get_tags_file_content_error_not_found(
        self, mocked_text, mocked_dakara_server_class
    ):
        """Test to get a tags file that does not exist
        """
        # create the mock
        mocked_text.side_effect = FileNotFoundError()

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaises(TagsFileNotFound) as error:
            feeder.get_tags_file_content()

        # assert the error
        self.assertEqual(str(error.exception), "Unable to find tags file path/to/file")

    @patch("dakara_feeder.tags_feeder.yaml.load")
    @patch.object(Path, "text", autoset=True)
    def test_get_tags_file_content_error_invalid(
        self, mocked_text, mocked_load, mocked_dakara_server_class
    ):
        """Test to get an invalid tags file
        """
        # create the mock
        tags = [{"name": "tag1"}]
        mocked_text.return_value = str(tags)
        mocked_load.side_effect = YAMLError("error message")

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaises(InvalidTagsFile) as error:
            feeder.get_tags_file_content()

        # assert the error
        self.assertEqual(
            str(error.exception),
            "Unable to parse tags file path/to/file: error message",
        )

    @patch.object(TagsFeeder, "get_tags_file_content")
    def test_feed(self, mocked_get_tags_file_content, mocked_dakara_server_class):
        """Test to feed tags
        """
        # create the mock
        tag = {"name": "tag1", "color_hue": 180}
        tag_extra = tag.copy()
        tag_extra["unused"] = True
        mocked_get_tags_file_content.return_value = {"tags": [tag_extra]}

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        feeder.feed()

        # assert the call
        mocked_dakara_server_class.return_value.create_tag.assert_called_with(tag)

    @patch.object(TagsFeeder, "get_tags_file_content")
    def test_feed_error_no_name(
        self, mocked_get_tags_file_content, mocked_dakara_server_class
    ):
        """Test to feed a tag without name
        """
        # create the mock
        tag = {"color_hue": 180}
        mocked_get_tags_file_content.return_value = {"tags": [tag]}

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaises(InvalidTag) as error:
            feeder.feed()

        # assert the error
        self.assertEqual(str(error.exception), "Tag 0 must have a name")

    @patch.object(TagsFeeder, "get_tags_file_content")
    def test_feed_error_no_hue(
        self, mocked_get_tags_file_content, mocked_dakara_server_class
    ):
        """Test to feed a tag without color hue
        """
        # create the mock
        tag = {"name": "tag1"}
        mocked_get_tags_file_content.return_value = {"tags": [tag]}

        # create the object
        feeder = TagsFeeder(self.config, "path/to/file", progress=False)

        # call the method
        with self.assertRaises(InvalidTag) as error:
            feeder.feed()

        # assert the error
        self.assertEqual(str(error.exception), "Tag 0 must have a color hue")

    @patch.object(TagsFeeder, "get_tags_file_content")
    def test_feed_error_tag_exists(
        self, mocked_get_tags_file_content, mocked_dakara_server_class
    ):
        """Test to feed a tag that already exists
        """
        # create the mocks
        tag = {"name": "tag1", "color_hue": 180}
        mocked_get_tags_file_content.return_value = {"tags": [tag]}
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
                "INFO:dakara_feeder.tags_feeder:Tag tag1 already exists on server and "
                "will not be updated"
            ],
        )
