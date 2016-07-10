from __future__ import absolute_import

import unittest
import threading
import time
import tkinter as tk

from pip_tkinter.__main__ import MainApp


class EventGenerator(threading.Thread):
    """
    Event Generator class :
    Inject events from different thread into tkinter mainloop()
    """

    def __init__(self, target_widget):
        threading.Thread.__init__(self);
        self.target = target_widget

class TestGUIApp(unittest.TestCase):
    """
    Test the GUI application and it's different GUI events

    Order of testing :

    1. Welcome page
    2. Install page
    3. Install From PyPI
    4. Install From Local archive
    5. Install From Requirements
    6. Manage Installed Modules page
    7. Uninstall Package
    8. Update Package
    """
    @classmethod
    def setUpClass(self):
        self.root = tk.Tk()
        self.main_app = MainApp(self.root)
        self.root.withdraw()

    def test_application(self):

        check_pages = (
            self.check_welcome_page,
            self.check_install_page,
            self.check_install_from_pypi,
            self.check_install_from_local_archive,
            self.check_install_from_requirements,
            self.check_manage_installed_modules,
            self.check_uninstalled_modules,
            self.check_update_modules,
        )

        for test_page in check_pages:
            test_page()

    def check_welcome_page(self):
        """
        Test welcome page
        """

        self.assertTrue('WelcomePage' in self.main_app.frames_dict, True)
        self.welcome_page = self.main_app.frames_dict['WelcomePage']
        self.welcome_page.tkraise()
        self.welcome_page.focus_set()
        self.root.update()

        #Select first radio button and check if it is selected
        self.welcome_page.first_button.invoke()
        self.root.update()
        self.assertEqual(self.welcome_page.radio_var.get(), 1)

        #Select second radio button and check if it is selected
        self.welcome_page.second_button.invoke()
        self.root.update()
        self.assertEqual(self.welcome_page.radio_var.get(), 2)

        #Invoke next button
        self.welcome_page.first_button.invoke()
        self.root.update()
        self.welcome_page.next_button.invoke()
        self.root.update()

        '''
        FIX IT : make tests for checking which window is at top
        x = self.root.tk.eval('wm stackorder '+
            str(self.main_app.frames_dict['InstallPage'])+
            ' isabove '+str(self.welcome_page))
        print (x)
        '''

    def check_install_page(self):
        """
        Test install page
        """

        install_page = self.main_app.frames_dict['InstallPage']
        #Test switching between different tabs.frames in install page

    def check_install_from_pypi(self):
        """
        Test install from pypi
        """

        install_page = self.main_app.frames_dict['InstallPage']
        install_from_pypi = install_page.frames_dict['InstallFromPyPI']

        #Set focus to search entry widget
        install_from_pypi.entry.focus_force()
        install_from_pypi.entry.update()
        install_from_pypi.entry.insert(0, 'Hello')

        #Check if entry widget has text 'Hello'
        self.assertEqual(install_from_pypi.entry.get(),'Hello')

        #Delete contents of entry widget
        install_from_pypi.entry.focus_force()
        install_from_pypi.entry.delete(0, 'end')
        self.assertEqual(install_from_pypi.entry.get(),'')

        #Search for pip using search
        install_from_pypi.entry.focus_force()
        install_from_pypi.entry.insert(0, 'pip')
        install_from_pypi.update()
        install_from_pypi.search_button.invoke()

        #Wait for the search thread to end
        install_from_pypi.search_thread.join()
        #Update the GUI with retrieved multi_items_list
        install_from_pypi.update()

        #Check if there are some elements in treeview
        treeview = install_from_pypi.multi_items_list.scroll_tree
        tree_children = treeview.get_children()
        self.assertTrue(len(tree_children)>0)

        #Select first item and set the focus to first item
        treeview.selection_set(tree_children[0])
        treeview.focus(tree_children[0])
        install_from_pypi.update()
        #get iid of currently focused/selected item
        curr_item = treeview.focus()
        self.assertEqual(curr_item, tree_children[0])


    def check_install_from_local_archive(self):
        """
        Test install from local archive
        """

        install_page = self.main_app.frames_dict["InstallPage"]
        install_from_arch = install_page.frames_dict["InstallFromLocalArchive"]

        #Set focus to search entry widget
        install_from_arch.path_to_requirement.focus_force()
        install_from_arch.path_to_requirement.update()
        install_from_arch.path_to_requirement.insert(0, 'Hello')

        #Check if entry widget has text 'Hello'
        self.assertEqual(install_from_arch.path_to_requirement.get(),'Hello')

    def check_install_from_requirements(self):
        """
        Test install from requirements
        """

        install_page = self.main_app.frames_dict["InstallPage"]
        install_from_req = install_page.frames_dict["InstallFromRequirements"]

        #Set focus to search entry widget
        install_from_req.path_to_requirement.focus_force()
        install_from_req.path_to_requirement.update()
        install_from_req.path_to_requirement.insert(0, 'Hello')

        #Check if entry widget has text 'Hello'
        self.assertEqual(install_from_req.path_to_requirement.get(),'Hello')

    def check_manage_installed_modules(self):
        """"
        Test manage installed modules page
        """

        install_page = self.main_app.frames_dict["InstallPage"]
        install_from_pypi = install_page.frames_dict["InstallFromPyPI"]

    def check_uninstalled_modules(self):
        """
        Test uninstalled Modules
        """

        install_page = self.main_app.frames_dict["ManageInstalledPage"]
        install_from_pypi = install_page.frames_dict["UninstallPackage"]

    def check_update_modules(self):
        """
        Test update package page
        """

        install_page = self.main_app.frames_dict["ManageInstalledPage"]
        install_from_pypi = install_page.frames_dict["UpdatePackage"]

    @classmethod
    def tearDownClass(self):
        self.root.destroy()
        del self.root
