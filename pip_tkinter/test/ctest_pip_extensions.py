import unittest
from pip.status_codes import SUCCESS, ERROR, NO_MATCHES_FOUND
from pip_tkinter.pip_extensions import GUISearchCommand
from pip_tkinter.pip_extensions import GUIListCommand
from pip_tkinter.utils import verify_pypi_url
from pip_tkinter.utils import pip_install_from_local_archive
from pip_tkinter.utils import pip_uninstall
from pip_tkinter.utils import runpip_using_subprocess
from pip_tkinter.config import find_bit_of_python

def install_dummy_package():

    import pkg_resources, os

    if find_bit_of_python()=='64bit':
        resource_path = pkg_resources.resource_filename(
            __name__,
            'pipguidummypackageAAZZBBCC-1.0-cp34-cp34m-linux_x86_64.whl')
    else:
        resource_path = pkg_resources.resource_filename(
            __name__,
            'pipguidummypackageAAZZBBCC-1.0-py3-none-any.whl')

    out, err = runpip_using_subprocess('pip3 install resource_path')

    if err != None:
        return str(1)
    else:
        return str(0)

def uninstall_dummy_package():

    out, err = runpip_using_subprocess(
        'pip3 uninstall pipguidummypackageAAZZBBCC')
    if err != None:
        return str(1)
    else:
        return str(0)

class PipExtensionsTest(unittest.TestCase):
    """
    Test pip extensions.
    """

    def setUp(self):
        self.test_gui_search = GUISearchCommand()
        self.test_gui_list = GUIListCommand()

    @unittest.skipIf(verify_pypi_url()==False, "Network unreachable")
    def test_return_value_for_successful_search_results(self):
        """
        Check if search results of overidden method return SUCCESS on
        successfully finding package
        """
        cmdline = "--index=https://pypi.python.org/pypi pip"
        options, args = self.test_gui_search.parse_args(cmdline.split())
        status = self.test_gui_search.run(options, args)
        self.assertEqual(status, SUCCESS)

    @unittest.skipIf(verify_pypi_url()==False, "Network unreachable")
    def test_return_value_for_unsuccessful_search_results(self):
        """
        Check if search results of overidden method return NO_MATCHES_FOUND on
        unable to find package
        """
        cmdline = "--index=https://pypi.python.org/pypi nonexistentpackage"
        options, args = self.test_gui_search.parse_args(cmdline.split())
        status = self.test_gui_search.run(options, args)
        self.assertEqual(status, NO_MATCHES_FOUND)

    @unittest.skipIf(
        install_dummy_package()!='0',
        "Unable to install dummy package. May require sudo privileges")
    def test_return_value_for_results_of_list_command_existing_package(self):
        """
        Check return value for list command
        """
        status = self.test_gui_list.main(['--no-cache-dir'])
        self.assertEqual(status, SUCCESS)

        inst_packages_list = self.test_gui_list.get_installed_packages_list()
        package_names_list = [pitem[0] for pitem in inst_packages_list]
        self.assertEqual('pipguidummypackageAAZZBBCC' in package_names_list, True)

    def tearDown(self):
        uninstall_dummy_package()

if __name__ == 'main':
    unittest.main()
