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
    6. Insall From PythonLibs
    7. Manage Installed Modules page
    8. Uninstall Package
    9. Update Package
    10. Freeze Requirements
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
            self.check_uninstall_modules,
            self.check_update_modules,
            self.check_freeze_requirements,
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

        install_page = self.main_app.frames_dict['InstallPage']
        install_from_arch = install_page.frames_dict['InstallFromLocalArchive']

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

    def check_install_from_pythonlibs(self):
        """
        Test install from pythonlibs
        """

        install_page = self.main_app.frames_dict['InstallPage']
        install_from_pythonlibs = install_page.frames_dict[
            'InstallFromPythonlibs']

        #Set focus to search entry widget
        install_from_pythonlibs.entry.focus_force()
        install_from_pythonlibs.entry.update()
        install_from_pythonlibs.entry.insert(0, 'Hello')

        #Check if entry widget has text 'Hello'
        self.assertEqual(install_from_pythonlibs.entry.get(),'Hello')

        #Delete contents of entry widget
        install_from_pythonlibs.entry.focus_force()
        install_from_pythonlibs.entry.delete(0, 'end')
        self.assertEqual(install_from_pythonlibs.entry.get(),'')

        #Search for pip using search
        install_from_pythonlibs.entry.focus_force()
        install_from_pythonlibs.entry.insert(0, 'al')
        install_from_pythonlibs.update()
        install_from_pythonlibs.search_button.invoke()

        #Wait for the search thread to end
        install_from_pythonlibs.search_thread.join()
        #Update the GUI with retrieved multi_items_list
        install_from_pythonlibs.update()

        #Cross check the number of elements of treeview with the list of
        #not updated packages
        treeview = install_from_pythonlibs.multi_items_list.scroll_tree
        tree_children = treeview.get_children()
        self.assertEqual(
            len(tree_children),
            len(install_from_pythonlibs.outdated_list))

        #Cross check if both results are same
        for item, package in zip(tree_children, install_from_pythonlibs.outdated_list):
            item_dict = install_from_pythonlibs.multi_items_list.scroll_tree.item(item)
            self.assertEqual(item_dict['values'][0], package[0])

        #Check if there are some elements in treeview
        if(len(tree_children)>0):
            #Select first item and set the focus to first item
            treeview.selection_set(tree_children[0])
            treeview.focus(tree_children[0])
            install_from_pythonlibs.update()

            #get iid of currently focused/selected item
            curr_item = treeview.focus()
            self.assertEqual(curr_item, tree_children[0])

    def check_manage_installed_modules(self):
        """"
        Test manage installed modules page
        """

        mng_installed_page = self.main_app.frames_dict["ManageInstalledPage"]
        uninstall_page = mng_installed_page.frames_dict["UninstallPackage"]
        #Test switching between different tabs.frames in manage installed page

    def check_uninstall_modules(self):
        """
        Test uninstall packages page
        """

        mng_installed_page = self.main_app.frames_dict["ManageInstalledPage"]
        uninstall_page = mng_installed_page.frames_dict["UninstallPackage"]

        #invoke the refresh button to populate treeview
        uninstall_page.refresh_button.invoke()
        uninstall_page.update()

        #Cross check the number of elements of treeview with the list of
        #not updated packages
        treeview = uninstall_page.multi_items_list.scroll_tree
        tree_children = treeview.get_children()
        self.assertEqual(
            len(tree_children),
            len(uninstall_page.installed_packages_list))

        #Cross check if both results are same
        for item, package in zip(tree_children, uninstall_page.installed_packages_list):
            item_dict = uninstall_page.multi_items_list.scroll_tree.item(item)
            self.assertEqual(item_dict['values'][0], package[0])


    def check_update_modules(self):
        """
        Test update package page
        """

        from pip_tkinter.utils import verify_pypi_url

        mng_installed_page = self.main_app.frames_dict["ManageInstalledPage"]
        update_page = mng_installed_page.frames_dict["UpdatePackage"]

        if verify_pypi_url() == True:
            #invoke the refresh button to populate treeview
            update_page.refresh_button.invoke()
            update_page.update()

            #Wait for the oudated list to be generated
            while(True):
                try:
                    update_page.update()
                    update_page.outdated_list
                    break
                except AttributeError as e:
                    continue

            #Cross check the number of elements of treeview with the list of
            #not updated packages
            treeview = update_page.multi_items_list.scroll_tree
            tree_children = treeview.get_children()
            self.assertEqual(len(tree_children),len(update_page.outdated_list))

            #Cross check if both results are same
            for item, package in zip(tree_children, update_page.outdated_list):
                item_dict = update_page.multi_items_list.scroll_tree.item(item)
                self.assertEqual(item_dict['values'][0], package[0])
        else:
            print ("Test partially completed for Update Modules Page")

    def check_freeze_requirements(self):
        """
        Test freeze requirements page
        """

        mng_installed_page = self.main_app.frames_dict["ManageInstalledPage"]
        freeze_req_page = mng_installed_page.frames_dict[
            "FreezeRequirementsPage"]

        #invoke the refresh button to populate treeview
        freeze_req_page.refresh_button.invoke()
        freeze_req_page.update()

        #Cross check the number of elements of treeview with the list of
        #not updated packages
        treeview = freeze_req_page.multi_items_list.scroll_tree
        tree_children = treeview.get_children()
        self.assertEqual(
            len(tree_children),
            len(freeze_req_page.installed_packages_list))

        #Cross check if both results are same
        for item, package in zip(tree_children, freeze_req_page.installed_packages_list):
            item_dict = freeze_req_page.multi_items_list.scroll_tree.item(item)
            self.assertEqual(item_dict['values'][0], package[0])

    @classmethod
    def tearDownClass(self):
        self.root.destroy()
        del self.root
