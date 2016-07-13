# coding=utf-8
from __future__ import absolute_import

import queue
import threading
import asyncio
import logging
import tkinter as tk
from tkinter import ttk
from io import StringIO

logger = logging.getLogger(__name__)

class ManageInstalledPage(ttk.Frame):
    """
    Manage already installed packages. Implements GUI for

    1. Updating package
    2. Uninstalling package
    """

    def __init__(self, root, controller=None):
        ttk.Frame.__init__(self, root)
        self.parent = root
        self.controller = controller

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0, sticky='nsew')
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(1, weight=1)
        self.create_message_bar()
        self.manage_frames()
        self.create_side_navbar()


    def create_side_navbar(self):
        """
        Create side navigation bar for providing user with options for
        selecting different ways of installation
        """

        # Create a navbar frame in which all navbar buttons will lie
        self.navbar_frame = ttk.Frame(
                                self.container,
                                borderwidth=3,
                                padding=0.5,
                                relief='ridge')
        self.navbar_frame.grid(
                            row=0,
                            column=0,
                            sticky='nsw',
                            pady=(1,1),
                            padx=(1,1))
        # Configure style for navbar frame

        # Button text
        update_archive_text = "Update Installed Packages"
        uninstall_archive_text = "Uninstall Package"

        # Button style
        navbar_button_style = ttk.Style()
        navbar_button_style.configure(
            'navbar.TButton',
            padding=(6, 25)
        )

        self.button_update = ttk.Button(
            self.navbar_frame,
            text=update_archive_text,
            state='active',
            style='navbar.TButton',
            command=lambda : self.show_frame('UpdatePackage')
        )
        self.button_update.grid(row=0, column=0, sticky='nwe')

        self.button_uninstall = ttk.Button(
            self.navbar_frame,
            text=uninstall_archive_text,
            style='navbar.TButton',
            command=lambda : self.show_frame('UninstallPackage')
        )
        self.button_uninstall.grid(row=1, column=0, sticky='nwe')

    def manage_frames(self):
        """
        Manage multiple frames. Creates dictionary of multiple frames to
        be used for showing user different GUI frames for different ways of
        installation.
        """

        frames_tuple = (
            UpdatePackage,
            UninstallPackage)

        self.frames_dict = {}
        for F in frames_tuple:
            frame_name = F.__name__
            new_frame = F(self.container, self)
            new_frame.grid(row=0, column=1, sticky='nsew')
            self.frames_dict[frame_name] = new_frame

        self.show_frame('UpdatePackage')

    def show_frame(self, frame_name):
        """
        Function for changing frames
        """

        frame = self.frames_dict[frame_name]
        frame.tkraise()

    def create_message_bar(self):
        """
        Print debug messages
        """

        self.debug_text = tk.StringVar()
        self.debug_text.set("No message")
        self.debug_bar = ttk.Label(
            self.container,
            textvariable=self.debug_text,
            padding=0.5,
            relief='ridge')
        self.debug_bar.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='swe',
            padx=(1,1),
            pady=(1,1))


class UpdatePackage(ttk.Frame):

    def __init__(self, parent, controller):

        ttk.Frame.__init__(
            self,
            parent,
            borderwidth=3,
            padding=0.5,
            relief='ridge')
        self.grid(row=0, column=0, sticky='nse', pady=(1,1), padx=(1,1))
        self.controller = controller
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_multitem_treeview()
        self.create_buttons()


    def create_multitem_treeview(self):
        """
        Create multitem treeview to show search results with headers :
        1. Python Module
        2. Installed version
        3. Available versions
        """

        self.headers = ['Python Module','Installed Version','Latest Version']
        from pip_tkinter.utils import MultiItemsList
        self.multi_items_list = MultiItemsList(self, self.headers)
        self.multi_items_list.myframe.grid(row=0, column=0, columnspan=3, sticky='nsew')
        #self.refresh_installed_packages()
        self.package_subwindow = tk.LabelFrame(
            self,
            text="Package Details",
            padx=5,
            pady=5)
        self.package_subwindow.grid(row=1, column=0, columnspan=3, sticky='nswe')
        self.package_details = tk.Text(
            self.package_subwindow,
            wrap='word',
            height=5)
        self.package_details.insert(1.0, 'No module selected')
        self.package_details.configure(state='disabled')
        self.package_details.pack(side='left', fill='x', expand='yes')
        yscrollbar=ttk.Scrollbar(
            self.package_subwindow,
            orient='vertical',
            command=self.package_details.yview)
        yscrollbar.pack(side='right', fill='y')
        self.package_details["yscrollcommand"]=yscrollbar.set
        self.multi_items_list.scroll_tree.bind(
            "<Double-Button-1>",
            lambda x: self.show_summary())

    def show_summary(self):
        """
        Show the details of the selected package
        """

        curr_item = self.multi_items_list.scroll_tree.focus()
        item_dict = self.multi_items_list.scroll_tree.item(curr_item)

        selected_module = 'Module Name : {}'.format(item_dict['values'][0])

        from pip_tkinter.utils import pip_show_command
        status_code, selected_package_details, serror = pip_show_command(selected_module)

        self.package_details.configure(state='normal')
        self.package_details.delete(1.0, 'end')
        self.package_details.insert(1.0, selected_package_details)
        self.package_details.configure(state='disabled')


    def refresh_installed_packages(self):
        """
        Show search results
        """

        #Disable buttons like :
        self.navigate_back.config(state='disabled')
        self.navigate_next.config(state='disabled')
        self.refresh_button.config(state='disabled')

        #Update the bottom message bar to inform user that the program
        #is fetching outdated packages list
        self.after(0, self.controller.debug_text.set('Fetching outdated packages ...'))

        #Spawn a new thread for getting list of outdated packages
        self.after(100, self.update_outdated_packages)

    def update_outdated_packages(self):

        from pip_tkinter.utils import pip_list_outdated_command
        results_tuple = pip_list_outdated_command()

        if len(results_tuple) > 0:
            self.multi_items_list.populate_rows(results_tuple)
            self.controller.debug_text.set('Found outdated packages')
        else:
            self.controller.debug_text.set('Error in fetching list of outdated\
            packages. Please check your internet settings')

        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.refresh_button.config(state='normal')

    def create_buttons(self):
        """
        Create back and next buttons
        """

        self.navigate_back = ttk.Button(
            self,
            text="Back",
            command=lambda: self.navigate_previous_frame())
        self.navigate_back.grid(row=3, column=0, sticky='w')

        self.refresh_button = ttk.Button(
            self,
            text="Refresh",
            command=lambda: self.refresh_installed_packages())
        self.refresh_button.grid(row=3, column=1, sticky='e')

        self.navigate_next = ttk.Button(
            self,
            text="Update",
            command=lambda: self.execute_pip_commands())
        self.navigate_next.grid(row=3, column=2, sticky='e')

    def navigate_previous_frame(self):
        """
        Navigate to previous frame
        """
        self.controller.controller.show_frame('WelcomePage')

    def execute_pip_commands(self):
        """
        Execute pip commands
        """
        self.navigate_back.config(state='disabled')
        self.navigate_next.config(state='disabled')
        self.search_button.config(state='disabled')

        self.after(0, self.controller.debug_text.set('Updating package. Please wait ...'))
        self.after(100, self.update_install_text)

        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.search_button.config(state='normal')

    def update_install_text(self):
        """
        Update install text
        """
        from pip_tkinter.utils import pip_install_from_PyPI

        curr_item = self.multi_items_list.scroll_tree.focus()
        item_dict = self.multi_items_list.scroll_tree.item(curr_item)
        selected_module = item_dict['values'][0]

        status, output, err = pip_install_from_PyPI(selected_module)

        if str(status) == '0':
            self.controller.debug_text.set('Successfully updated package')
        else:
            self.controller.debug_text.set('Error in updating package')


class UninstallPackage(ttk.Frame):

    def __init__(self, parent, controller):

        ttk.Frame.__init__(
            self,
            parent,
            borderwidth=3,
            padding=0.5,
            relief='ridge')
        self.grid(row=0, column=0, sticky='nse', pady=(1,1), padx=(1,1))
        self.controller = controller
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_multitem_treeview()
        self.create_buttons()


    def create_multitem_treeview(self):
        """
        Create multitem treeview to show search results with headers :
        1. Python Module
        2. Installed version
        3. Available versions
        """

        self.headers = ['Python Module','Installed Version']
        from pip_tkinter.utils import MultiItemsList
        self.multi_items_list = MultiItemsList(self, self.headers)
        self.multi_items_list.myframe.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky='nswe')
        #self.refresh_installed_packages()
        self.package_subwindow = tk.LabelFrame(
            self,
            text="Package Details",
            padx=5,
            pady=5)
        self.package_subwindow.grid(row=1, column=0, columnspan=3, sticky='nswe')
        self.package_details = tk.Text(
            self.package_subwindow,
            wrap='word',
            height=5)
        self.package_details.insert(1.0, 'No module selected')
        self.package_details.configure(state='disabled')
        self.package_details.pack(side='left', fill='x', expand='yes')
        yscrollbar=ttk.Scrollbar(
            self.package_subwindow,
            orient='vertical',
            command=self.package_details.yview)
        yscrollbar.pack(side='right', fill='y')
        self.package_details["yscrollcommand"]=yscrollbar.set
        self.multi_items_list.scroll_tree.bind(
            "<Double-Button-1>",
            lambda x: self.show_summary())

    def show_summary(self):
        """
        Show the details of the selected package
        """

        curr_item = self.multi_items_list.scroll_tree.focus()
        item_dict = self.multi_items_list.scroll_tree.item(curr_item)
        selected_module = 'Module Name : {}'.format(item_dict['values'][0])

        from pip_tkinter.utils import pip_show_command
        status_code, selected_package_details, serror = pip_show_command(selected_module)

        self.package_details.configure(state='normal')
        self.package_details.delete(1.0, 'end')
        self.package_details.insert(1.0, selected_package_details)
        self.package_details.configure(state='disabled')

    def refresh_installed_packages(self):
        """
        Show search results
        """

        from pip_tkinter.utils import pip_list_command

        self.installed_packages_list = pip_list_command()
        results_tuple = self.installed_packages_list
        self.multi_items_list.populate_rows(results_tuple)

        self.controller.debug_text.set('Found installed packages')

    def create_buttons(self):
        """
        Create back and next buttons
        """

        self.navigate_back = ttk.Button(
            self,
            text="Back",
            command=lambda: self.navigate_previous_frame())
        self.navigate_back.grid(row=3, column=0, sticky='w')

        self.refresh_button = ttk.Button(
            self,
            text="Refresh",
            command=lambda: self.refresh_installed_packages())
        self.refresh_button.grid(row=3, column=1, sticky='e')

        self.navigate_next = ttk.Button(
            self,
            text="Uninstall",
            command=lambda: self.execute_pip_commands())
        self.navigate_next.grid(row=3, column=2, sticky='e')

    def navigate_previous_frame(self):
        """
        Navigate to previous frame
        """
        self.controller.controller.show_frame('WelcomePage')

    def execute_pip_commands(self):
        """
        Execute pip commands
        """
        self.navigate_back.config(state='disabled')
        self.navigate_next.config(state='disabled')
        self.refresh_button.config(state='disabled')

        self.after(0, self.controller.debug_text.set(
            'Uninstalling package. Please wait ...'))
        self.after(100, self.update_uninstall_text)

    def update_uninstall_text(self):
        """
        Update install text
        """
        from pip_tkinter.utils import pip_uninstall

        curr_item = self.multi_items_list.scroll_tree.focus()
        item_dict = self.multi_items_list.scroll_tree.item(curr_item)
        selected_module = item_dict['values'][0]

        status, output, err = pip_uninstall(selected_module)

        if str(status) == '0':
            self.controller.debug_text.set('Package removed')
        else:
            self.controller.debug_text.set('Error in uninstalling package')
            print (err)

        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.refresh_button.config(state='normal')
