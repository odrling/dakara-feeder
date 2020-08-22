import inspect
from types import ModuleType
from unittest import TestCase
from unittest.mock import patch

from dakara_feeder import customization
from dakara_feeder.song import BaseSong


class GetCustomSongTestCase(TestCase):
    """Test the getter of customized song class
    """

    @patch("dakara_feeder.customization.import_custom_object", autospec=True)
    def test_get_from_class(self, mocked_import_custom_object):
        """Test to get a valid song class from class module name
        """
        # mock the returned class
        class MySong(BaseSong):
            pass

        mocked_import_custom_object.return_value = MySong

        # call the method
        with self.assertLogs("dakara_feeder.customization") as logger:
            CustomSong = customization.get_custom_song("song.MySong")

        # assert the result
        self.assertIs(CustomSong, MySong)

        # assert the call
        mocked_import_custom_object.assert_called_with("song.MySong")

        # assert logs
        self.assertListEqual(
            logger.output,
            ["INFO:dakara_feeder.customization:Using custom Song class: song.MySong"],
        )

    @patch("dakara_feeder.customization.import_custom_object", autospec=True)
    def test_get_from_module(self, mocked_import_custom_object):
        """Test to get a valid default song class from module name
        """
        # mock the returned class
        my_module = ModuleType("my_module")

        class Song(BaseSong):
            pass

        my_module.Song = Song
        mocked_import_custom_object.return_value = my_module

        # call the method
        CustomSong = customization.get_custom_song("song")

        # assert the result
        self.assertIs(CustomSong, Song)

    @patch("dakara_feeder.customization.import_custom_object", autospec=True)
    def test_get_from_module_error_no_default(self, mocked_import_custom_object):
        """Test to get a default song class that does not exist
        """
        # mock the returned class
        my_module = ModuleType("my_module")
        mocked_import_custom_object.return_value = my_module

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "Cannot find default class Song in module my_module",
        ):
            customization.get_custom_song("song")

    @patch("dakara_feeder.customization.import_custom_object", autospec=True)
    def test_get_from_class_error_not_class(self, mocked_import_custom_object):
        """Test to get a song class that is not a class
        """
        # mock the returned class
        mocked_import_custom_object.return_value = "str"

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectTypeError, "song.MySong is not a class"
        ):
            customization.get_custom_song("song.MySong")

    @patch("dakara_feeder.customization.import_custom_object", autospec=True)
    def test_get_from_module_error_not_class(self, mocked_import_custom_object):
        """Test to get a default song class that is not a class
        """
        # mock the returned class
        my_module = ModuleType("my_module")
        my_module.Song = 42
        mocked_import_custom_object.return_value = my_module

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectTypeError, "song.Song is not a class"
        ):
            customization.get_custom_song("song")

    @patch("dakara_feeder.customization.import_custom_object", autospec=True)
    def test_get_from_class_error_not_song_subclass(self, mocked_import_custom_object):
        """Test to get a song class that is not a subclass of Song
        """
        # mock the returned class
        class MySong:
            pass

        mocked_import_custom_object.return_value = MySong

        # call the method
        with self.assertRaisesRegex(
            customization.InvalidObjectTypeError, "song.MySong is not a Song subclass"
        ):
            customization.get_custom_song("song.MySong")


class CurrentDirInPathTestCase(TestCase):
    """Test the helper to put current directory in Python path
    """

    @patch("dakara_feeder.customization.os.getcwd")
    @patch("dakara_feeder.customization.sys")
    def test_normal(self, mocked_sys, mocked_getcwd):
        """Test the helper with no alteration of the path
        """
        # setup mocks
        mocked_getcwd.return_value = "current/directory"
        mocked_sys.path = ["some/directory"]

        # use the context manager
        with customization.current_dir_in_path():
            self.assertListEqual(
                mocked_sys.path, ["current/directory", "some/directory"]
            )

        # assert the mock
        self.assertListEqual(mocked_sys.path, ["some/directory"])

    @patch("dakara_feeder.customization.os.getcwd")
    @patch("dakara_feeder.customization.sys")
    def test_alteration(self, mocked_sys, mocked_getcwd):
        """Test the helper with alteration of the path
        """
        # setup mocks
        mocked_getcwd.return_value = "current/directory"
        mocked_sys.path = []

        # use the context manager
        with customization.current_dir_in_path():
            mocked_sys.path.append("other/directory")
            self.assertListEqual(
                mocked_sys.path, ["current/directory", "other/directory"]
            )

        # assert the mock
        self.assertListEqual(mocked_sys.path, [])


class ImportCustomObjectTestCase(TestCase):
    """Test the importer for custom objects
    """

    def test_import_module(self):
        """Test to import a module
        """
        module = customization.import_custom_object("tests.resources.my_module")
        self.assertTrue(inspect.ismodule(module))

    def test_import_parent_module(self):
        """Test to import a parent module
        """
        module = customization.import_custom_object("tests.resources")
        self.assertTrue(inspect.ismodule(module))

    def test_import_class(self):
        """Test to import a class
        """
        klass = customization.import_custom_object("tests.resources.my_module.MyClass")
        self.assertTrue(inspect.isclass(klass))

    def test_import_static_attribute(self):
        """Test to import a class static attribute
        """
        attribute = customization.import_custom_object(
            "tests.resources.my_module.MyClass.my_attribute"
        )
        self.assertEqual(attribute, 42)

    def test_error_parent_module(self):
        """Test to import a non-existing parent module
        """
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module notexistingmodule found",
        ):
            customization.import_custom_object("notexistingmodule.sub")

    def test_error_module(self):
        """Test to import a non-existing module
        """
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module or object notexistingmodule found in tests.resources",
        ):
            customization.import_custom_object("tests.resources.notexistingmodule")

    def test_error_object(self):
        """Test to import a non-existing object
        """
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module or object notexistingattribute found in "
            "tests.resources.my_module",
        ):
            customization.import_custom_object(
                "tests.resources.my_module.notexistingattribute"
            )

    def test_error_sub_object(self):
        """Test to import a non-existing sub object
        """
        with self.assertRaisesRegex(
            customization.InvalidObjectModuleNameError,
            "No module or object notexistingattribute found in "
            "tests.resources.my_module.MyClass",
        ):
            customization.import_custom_object(
                "tests.resources.my_module.MyClass.notexistingattribute"
            )
