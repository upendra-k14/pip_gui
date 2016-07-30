# coding=utf-8
from __future__ import absolute_import

import queue
import threading
import asyncio
import logging
import multiprocessing
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
        """
        Initiate ManageInstalledPage

        :param self.parent: parent frame for ManageInstalledPage
        :param self.controller: parent page for ManageInstalledPage
        :param self.container: a tkinter frame to enclose contents of page
        """
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

        self.create_process_log_frame()
        self.container.tkraise()

    def create_process_log_frame(self):
        """
        Method to create last logging frame to keep the user updated with
        process. Logs real time output of pip process to tkinter text widget

        :param self.task_frame: a tkinter frame to enclose contents
        """

        self.task_frame = ttk.Frame(self, relief='ridge', padding=0.5)
        self.task_frame.grid(row=0, column=0, sticky='nsew')
        self.task_frame.rowconfigure(0, weight=1)
        self.task_frame.columnconfigure(0, weight=1)

        self.process_details = tk.Text(
            self.task_frame,
            wrap='word',
            height=5,
            padx=5)
        self.process_details.insert(1.0, 'No process started')
        self.process_details.configure(state='disabled')
        self.process_details.grid(
            row=0,
            column=0,
            columnspan=2,
            sticky='nsew')
        yscrollbar=ttk.Scrollbar(
            self.task_frame,
            orient='vertical',
            command=self.process_details.yview)
        yscrollbar.grid(row=0, column=1, sticky='nse', in_=self.task_frame)
        self.process_details['yscrollcommand']=yscrollbar.set

        #Create control buttons
        self.go_back_button = ttk.Button(
            self.task_frame,
            text='Back',
            command=lambda: self.navigate_back())
        self.go_back_button.grid(
            row=1,
            column=0,
            sticky='w',
            padx=5,
            pady=5)
        self.go_back_button.config(state='disabled')
        self.abort_process_button = ttk.Button(
            self.task_frame,
            text='Abort',
            command=lambda: self.abort_process())
        self.abort_process_button.grid(
            row=1,
            column=1,
            sticky='e',
            padx=5,
            pady=5)
        self.abort_process_button.config(state='disabled')

    def navigate_back(self):
        self.debug_bar.config(text='No message')
        self.container.tkraise()

    def abort_process(self):
        self.abort_process_button.config(state='disabled')
        self.frames_dict[self.current_frame].abort_process()
        self.debug_bar.config(text='Installation aborted')
        self.go_back_button.config(state='normal')

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
        self.debug_bar.config(text='No message')
        self.current_frame = frame_name
        frame = self.frames_dict[frame_name]
        frame.tkraise()

    def show_task_frame(self):
        self.debug_bar.config(text='No message')
        self.task_frame.tkraise()
        self.go_back_button.config(state='disabled')
        self.abort_process_button.config(state='normal')

    def create_message_bar(self):
        """
        Print debug messages
        """

        self.debug_bar = ttk.Label(
            self,
            padding=0.5,
            relief='ridge')
        self.debug_bar.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='swe',
            padx=(1,1),
            pady=(1,1))
        self.debug_bar.config(text='No message')


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
        self.multi_items_list.myframe.grid(
            row=0,
            column=0,
            columnspan=3,
            sticky='nsew')
        self.multi_items_list.scroll_tree.bind(
            '<<TreeviewSelect>>',
            lambda x : self.scroll_tree_select())
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

    def scroll_tree_select(self):
        """
        If treeview is selected, enable update buttons
        """
        self.navigate_next.config(state='normal')

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
        self.after(0, self.controller.debug_bar.config(
            text='Fetching outdated packages ...'))

        #Spawn a new thread for getting list of outdated packages
        self.after(100, self.update_outdated_packages)

    def update_outdated_packages(self):

        from pip_tkinter.utils import pip_list_outdated_command
        results_tuple = pip_list_outdated_command()

        if len(results_tuple) > 0:
            self.multi_items_list.populate_rows(results_tuple)
            self.controller.debug_bar.config(text='Found outdated packages')
        else:
            self.controller.debug_bar.config(text='Error in fetching list of\
             outdated packages. Please check your internet settings')

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
        self.refresh_button.config(state='disabled')

        self.after(100, self.controller.debug_bar.config(
            text='Updating package. Please wait ...'))
        self.after(100, self.update_installation_log)

    def update_installation_log(self):

        from pip_tkinter.utils import pip_install_from_PyPI

        try:
            curr_item = self.multi_items_list.scroll_tree.focus()
            item_dict = self.multi_items_list.scroll_tree.item(curr_item)
            selected_module = item_dict['values'][0]

            self.controller.show_task_frame()
            self.install_queue = multiprocessing.Queue()

            self.update_thread = multiprocessing.Process(
                target=pip_install_from_PyPI,
                kwargs={
                    'package_args':selected_module,
                    'install_queue':self.install_queue})

            self.install_log_started = False
            self.error_log_started = False
            self.after(100, self.log_from_install_queue)

            self.controller.process_details.config(state='normal')
            self.controller.process_details.delete(1.0,'end')
            self.controller.process_details.config(state='disabled')

            self.update_thread.start()

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.refresh_button.config(state='normal')

        except IndexError:
            self.controller.debug_bar.config(text='Select correct package')


    def log_from_install_queue(self):
        try:
            self.install_message = self.install_queue.get(0)

            if ((self.install_message[1]=='process_started') and
                (self.install_log_started==False)):

                self.install_log_started = True
                self.controller.process_details.config(state='normal')
                self.controller.process_details.delete(1.0,'end')
                self.controller.process_details.config(state='disabled')


            elif (self.install_log_started==True):

                if self.install_message[0]==3:
                    if self.install_message[1]==0:
                        self.controller.debug_bar.config(text='Done')
                    else:
                        self.controller.debug_bar.config(
                            text='Error in updating package')
                    self.install_log_started = False
                    self.controller.go_back_button.config(state='normal')
                    self.controller.abort_process_button.config(state='disabled')
                    return
                else:
                    self.controller.process_details.config(state='normal')
                    self.controller.process_details.insert(
                        'end',
                        self.install_message[1])
                    self.controller.process_details.config(state='disabled')

            self.after(20, self.log_from_install_queue)

        except queue.Empty:
            self.after(100, self.log_from_install_queue)


    def abort_process(self):
        """
        Stop pip process : Currently not sure to provide option for
        aborting process in between
        """

        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.refresh_button.config(state='normal')
        self.update_thread.terminate()


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
        self.multi_items_list.scroll_tree.bind(
            '<<TreeviewSelect>>', lambda x : self.scroll_tree_select())
        #self.refresh_installed_packages()
        self.package_subwindow = tk.LabelFrame(
            self,
            text="Package Details",
            padx=5,
            pady=5)
        self.package_subwindow.grid(
            row=1,
            column=0,
            columnspan=3,
            sticky='nswe')
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

    def scroll_tree_select(self):
        """
        If treeview is selected, enable update buttons
        """
        self.navigate_next.config(state='normal')

    def show_summary(self):
        """
        Show the details of the selected package
        """

        curr_item = self.multi_items_list.scroll_tree.focus()
        item_dict = self.multi_items_list.scroll_tree.item(curr_item)
        selected_module = 'Module Name : {}'.format(item_dict['values'][0])

        from pip_tkinter.utils import pip_show_command
        status_code, selected_package_details, serror = pip_show_command(
            selected_module)

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

        self.controller.debug_bar.config(text='Found installed packages')

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

        self.after(100, self.controller.debug_bar.config(
            text='Uninstalling package. Please wait ...'))
        self.after(100, self.update_uninstallation_log)

    def update_uninstallation_log(self):

        from pip_tkinter.utils import pip_uninstall

        try:
            curr_item = self.multi_items_list.scroll_tree.focus()
            item_dict = self.multi_items_list.scroll_tree.item(curr_item)
            selected_module = item_dict['values'][0]

            self.controller.show_task_frame()
            self.uninstall_queue = multiprocessing.Queue()

            self.update_thread = multiprocessing.Process(
                target=pip_uninstall,
                kwargs={
                    'package_args':selected_module,
                    'uninstall_queue':self.uninstall_queue})

            self.controller.process_details.config(state='normal')
            self.controller.process_details.delete(1.0,'end')
            self.controller.process_details.config(state='disabled')

            self.uninstall_log_started = False
            self.error_log_started = False
            self.after(100, self.log_from_uninstall_queue)

            self.update_thread.start()

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.refresh_button.config(state='normal')

        except IndexError:
            self.controller.debug_bar.config(text='Select correct package')


    def log_from_uninstall_queue(self):
        try:
            self.uninstall_message = self.uninstall_queue.get(0)

            if ((self.uninstall_message[1]=='process_started') and
                (self.uninstall_log_started==False)):

                self.uninstall_log_started = True
                self.controller.process_details.config(state='normal')
                self.controller.process_details.delete(1.0,'end')
                self.controller.process_details.config(state='disabled')

            elif (self.uninstall_log_started==True):

                if self.uninstall_message[0]==3:
                    if self.uninstall_message[1]==0:
                        self.controller.debug_bar.config(text='Done')
                    else:
                        self.controller.debug_bar.config(
                            text='Error in uninstalling package')
                    self.uninstall_log_started = False
                    self.controller.go_back_button.config(state='normal')
                    self.controller.abort_process_button.config(state='disabled')
                    return
                else:
                    self.controller.process_details.config(state='normal')
                    self.controller.process_details.insert(
                        'end',
                        self.uninstall_message[1])
                    self.controller.process_details.config(state='disabled')

            self.after(20, self.log_from_uninstall_queue)

        except queue.Empty:
            self.after(100, self.log_from_uninstall_queue)


    def abort_process(self):
        """
        Stop pip process : Currently not sure to provide option for
        aborting process in between
        """
        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.refresh_button.config(state='normal')
        self.update_thread.terminate()
