import unittest
from pip_tkinter.pip_extensions import GUISearchCommand
from pip.commands.search import SearchCommand

class ExtensionsTest(unittest.TestCase):
    def setUp(self):
        self.test_gui_search = GUISearchCommand()
        self.pip_search = SearchCommand()

    def test_search_results(self):
        """
        Check if search results of overidden method and original pip search
        method are same.
        """
        self.test_gui_search.main('pip')
        self.pip_search.main('pip')
        self.assertEquals(self.test_gui_search.hits, self.pip_search.hits)

    def test_for_installed_packages_list(self):
        """
        Check if the installed packages list is correct or not
        """
        pass

    def tearDown(self):
        pass


if __name__ == 'main':
    unittest.main()
