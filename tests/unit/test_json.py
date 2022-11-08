from json import dumps
from unittest import TestCase
from unittest.mock import patch

from path import Path

from dakara_feeder.json import (
    JsonContentInvalidError,
    JsonFileInvalidError,
    JsonFileNotFoundError,
    get_json_file_content,
)


@patch.object(Path, "read_text", autoset=True)
class GetJsonFileContentTestCase(TestCase):
    """Test the get_json_file_content function."""

    def test_get(self, mocked_read_text):
        """Test to get a JSON file."""
        # create the mock
        content = {"name": "tag1"}
        mocked_read_text.return_value = dumps(content)

        # call the method
        content_parsed = get_json_file_content(Path("path/to/file"))

        # assert the result
        self.assertDictEqual(content, content_parsed)

        # assert the call
        mocked_read_text.assert_called_with()

    def test_get_error_not_found(self, mocked_read_text):
        """Test to get a JSON file that does not exist."""
        # create the mock
        mocked_read_text.side_effect = FileNotFoundError()

        # call the method
        with self.assertRaisesRegex(
            JsonFileNotFoundError, "Unable to find JSON file 'path/to/file'"
        ):
            get_json_file_content(Path("path/to/file"))

    @patch("dakara_feeder.json.json.load")
    def test_get_error_invalid(self, mocked_load, mocked_read_text):
        """Test to get an invalid JSON file."""
        # create the mock
        mocked_read_text.return_value = "aaaaaaa"

        # call the method
        with self.assertRaisesRegex(
            JsonFileInvalidError,
            "Unable to parse JSON file 'path/to/file':",
        ):
            get_json_file_content(Path("path/to/file"))

    def test_get_key(self, mocked_read_text):
        """Test to get the key of a JSON file."""
        # create the mock
        content = {"tags": {"name": "tag1"}}
        mocked_read_text.return_value = dumps(content)

        # call the method
        content_parsed = get_json_file_content(Path("path/to/file"), "tags")

        # assert the result
        self.assertDictEqual(content["tags"], content_parsed)

        # assert the call
        mocked_read_text.assert_called_with()

    def test_get_key_error(self, mocked_read_text):
        """Test to get a invalid key of a JSON file."""
        # create the mock
        content = {"tags": {"name": "tag1"}}
        mocked_read_text.return_value = dumps(content)

        # call the method
        with self.assertRaisesRegex(
            JsonContentInvalidError,
            "Unable to find key 'other' in JSON file 'path/to/file'",
        ):
            get_json_file_content(Path("path/to/file"), "other")
