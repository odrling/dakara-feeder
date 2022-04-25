import inspect
import re
from importlib import resources
from types import ModuleType
from unittest import TestCase
from unittest.mock import patch

from path import Path

from dakara_feeder import customization
from dakara_feeder.song import BaseSong


@patch("dakara_feeder.customization.import_from_file", autospec=True)
@patch("dakara_feeder.customization.import_from_module", autospec=True)
class GetCustomSongTestCase(TestCase):
    def test_get_from_class(self, mocked_import_from_module, mocked_import_from_file):
        """Test to get a valid song class from class module name."""
        # mock the returned class
        class MySong(BaseSong):
            pass

        mocked_import_from_module.return_value = MySong

        # call the method
        with self.assertLogs("dakara_feeder.customization") as logger:
            CustomSong = customization.get_custom_song("song.MySong")

        # assert the result
        self.assertIs(CustomSong, MySong)

        # assert the call
        mocked_import_from_module.assert_called_with("song.MySong")
        mocked_import_from_file.assert_not_called()

        # assert logs
        self.assertListEqual(
            logger.output,
            ["INFO:dakara_feeder.customization:Using custom Song class: song.MySong"],
        )

    def test_get_from_module(self, mocked_import_from_module, mocked_import_from_file):
        """Test to get a valid default song class from module name."""
        # mock the returned class
        my_module = ModuleType("my_module")

        class Song(BaseSong):
            pass

        my_module.Song = Song
        mocked_import_from_module.return_value = my_module

        # call the method
        CustomSong = customization.get_custom_song("song")

        # assert the result
        self.assertIs(CustomSong, Song)

        # assert the call
        mocked_import_from_file.assert_not_called()

    def test_get_from_file_module(
        self, mocked_import_from_module, mocked_import_from_file
    ):
        """Test to get a valid song class from file."""
        # mock the returned class
        my_module = ModuleType("my_module")

        class Song(BaseSong):
            pass

        my_module.song = Song
        mocked_import_from_file.return_value = my_module

        # call the method
        CustomSong = customization.get_custom_song("file.py::song")

        # assert the result
        self.assertIs(CustomSong, Song)

        # assert the call
        mocked_import_from_module.assert_not_called()

    def test_get_from_file(self, mocked_import_from_module, mocked_import_from_file):
        """Test to get a valid default song class from file."""
        # mock the returned class
        my_module = ModuleType("my_module")

        class Song(BaseSong):
            pass

        my_module.Song = Song
        mocked_import_from_file.return_value = my_module

        # call the method
        CustomSong = customization.get_custom_song("file.py")

        # assert the result
        self.assertIs(CustomSong, Song)

        # assert the call
        mocked_import_from_module.assert_not_called()

    def test_get_from_module_error_no_default(
        self, mocked_import_from_module, mocked_import_from_file
    ):
        """Test to get a default song class that does not exist."""
        # mock the returned class
        my_module = ModuleType("my_module")
        mocked_import_from_module.return_value = my_module

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "Cannot find class Song in module my_module",
        ):
            customization.get_custom_song("song")

        # assert the call
        mocked_import_from_file.assert_not_called()

    def test_get_from_class_error_not_class(
        self, mocked_import_from_module, mocked_import_from_file
    ):
        """Test to get a song class that is not a class."""
        # mock the returned class
        mocked_import_from_module.return_value = "str"

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectTypeError, "song.MySong is not a class"
        ):
            customization.get_custom_song("song.MySong")

        # assert the call
        mocked_import_from_file.assert_not_called()

    def test_get_from_module_error_not_class(
        self, mocked_import_from_module, mocked_import_from_file
    ):
        """Test to get a default song class that is not a class."""
        # mock the returned class
        my_module = ModuleType("my_module")
        my_module.Song = 42
        mocked_import_from_module.return_value = my_module

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectTypeError, "song.Song is not a class"
        ):
            customization.get_custom_song("song")

        # assert the call
        mocked_import_from_file.assert_not_called()

    def test_get_from_class_error_not_song_subclass(
        self, mocked_import_from_module, mocked_import_from_file
    ):
        """Test to get a song class that is not a subclass of Song."""
        # mock the returned class
        class MySong:
            pass

        mocked_import_from_module.return_value = MySong

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectTypeError,
            "song.MySong is not a BaseSong subclass",
        ):
            customization.get_custom_song("song.MySong")

        # assert the call
        mocked_import_from_file.assert_not_called()

    def test_get_from_nothing_error(
        self, mocked_import_from_module, mocked_import_from_file
    ):
        """Test to get a song class from nothing."""
        # call the method
        with self.assertRaises(customization.InvalidSongClassConfigError):
            customization.get_custom_song("")

        # assert the call
        mocked_import_from_file.assert_not_called()


class SplitPathObjectTestCase(TestCase):
    def test_split_path_and_module(self):
        self.assertTupleEqual(
            customization.split_path_object(
                str(Path("path") / "to" / "file.py") + "::object.CustomSong"
            ),
            (Path("path") / "to" / "file.py", "object.CustomSong"),
        )

    def test_split_path(self):
        self.assertTupleEqual(
            customization.split_path_object(str(Path("path") / "to" / "file.py")),
            (Path("path") / "to" / "file.py", None),
        )
        self.assertTupleEqual(
            customization.split_path_object(
                str(Path("path") / "to" / "file.py") + "::"
            ),
            (Path("path") / "to" / "file.py", None),
        )

    def test_split_module(self):
        self.assertTupleEqual(
            customization.split_path_object("object.CustomSong"),
            (None, "object.CustomSong"),
        )

    def test_split_nothing(self):
        self.assertTupleEqual(
            customization.split_path_object(""),
            (None, None),
        )


class DirInPathTestCase(TestCase):
    @patch("dakara_feeder.customization.sys")
    def test_normal(self, mocked_sys):
        """Test the helper with no alteration of the path."""
        # setup mocks
        mocked_sys.path = ["some/directory"]

        # use the context manager
        with customization.dir_in_path(Path("path") / "to" / "directory"):
            self.assertListEqual(
                mocked_sys.path,
                [str(Path("path") / "to" / "directory"), "some/directory"],
            )

        # assert the mock
        self.assertListEqual(mocked_sys.path, ["some/directory"])

    @patch("dakara_feeder.customization.sys")
    def test_alteration(self, mocked_sys):
        """Test the helper with alteration of the path."""
        # setup mocks
        mocked_sys.path = []

        # use the context manager
        with customization.dir_in_path(Path("path") / "to" / "directory"):
            mocked_sys.path.append("other/directory")
            self.assertListEqual(
                mocked_sys.path,
                [str(Path("path") / "to" / "directory"), "other/directory"],
            )

        # assert the mock
        self.assertListEqual(mocked_sys.path, [])


class ImportFromFileTestCase(TestCase):
    def test_import_file(self):
        """Test to import a file."""
        with resources.path("tests.resources", "my_module.py") as file:
            module = customization.import_from_file(Path(file))

        self.assertTrue(inspect.ismodule(module))

    def test_import_error(self):
        """Test to import a non existing file."""
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            re.escape(
                "No module found from file " + Path("path") / "to" / "nowhere.py"
            ),
        ):
            customization.import_from_file(Path("path") / "to" / "nowhere.py")


class ImportFromModuleTestCase(TestCase):
    def test_import_module(self):
        """Test to import a module."""
        module = customization.import_from_module("tests.resources.my_module")
        self.assertTrue(inspect.ismodule(module))

    def test_import_parent_module(self):
        """Test to import a parent module."""
        module = customization.import_from_module("tests.resources")
        self.assertTrue(inspect.ismodule(module))

    def test_import_class(self):
        """Test to import a class."""
        klass = customization.import_from_module("tests.resources.my_module.MyClass")
        self.assertTrue(inspect.isclass(klass))

    def test_import_static_attribute(self):
        """Test to import a class static attribute."""
        attribute = customization.import_from_module(
            "tests.resources.my_module.MyClass.my_attribute"
        )
        self.assertEqual(attribute, 42)

    def test_error_parent_module(self):
        """Test to import a non-existing parent module."""
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module notexistingmodule found",
        ):
            customization.import_from_module("notexistingmodule.sub")

    def test_error_module(self):
        """Test to import a non-existing module."""
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module or object notexistingmodule found in tests.resources",
        ):
            customization.import_from_module("tests.resources.notexistingmodule")

    def test_error_object(self):
        """Test to import a non-existing object."""
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module or object notexistingattribute found in "
            "tests.resources.my_module",
        ):
            customization.import_from_module(
                "tests.resources.my_module.notexistingattribute"
            )

    def test_error_sub_object(self):
        """Test to import a non-existing sub object."""
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module or object notexistingattribute found in "
            "tests.resources.my_module.MyClass",
        ):
            customization.import_from_module(
                "tests.resources.my_module.MyClass.notexistingattribute"
            )
