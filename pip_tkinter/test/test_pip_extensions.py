import unittest
from pip.status_codes import SUCCESS, ERROR, NO_MATCHES_FOUND
from pip_tkinter.pip_extensions import GUISearchCommand
from pip_tkinter.pip_extensions import GUIShowCommand

class PipExtensionsTest(unittest.TestCase):
    """
    Test pip extensions.
    """

    def setUp(self):
        self.test_gui_search = GUISearchCommand()
        self.test_gui_show = GUIShowCommand()

    def test_return_value_for_successful_search_results(self):
        """
        Check if search results of overidden method return SUCCESS on
        successfully finding package
        """
        status = self.test_gui_search.main('pip')
        self.assertEquals(status, SUCCESS)

    def test_return_value_for_unsuccessful_search_results(self):
        """
        Check if search results of overidden method return NO_MATCHES_FOUND on
        unable to find package
        """
        status = self.test_gui_search.main('nonexistentpackage')
        self.assertEquals(status, NO_MATCHES_FOUND)

    def test_return_value_for_results_of_show_command_existing_package(self):
        """
        Check return value of show command for installed package
        """
        status = self.test_gui_show.main('pip')
        self.assertEquals(status, SUCCESS)

    def test_return_value_for_results_of_show_command_not_existing_package(self):
        """
        Check return value of show command for not installed or not existing
        package
        """
        status = self.test_gui_show.main('nonexistentpackage')
        self.assertEquals(status, ERROR)

    def tearDown(self):
        pass


if __name__ == 'main':
    unittest.main()
