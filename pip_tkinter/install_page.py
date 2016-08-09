 # coding=utf-8
from __future__ import absolute_import

import logging
import threading
import multiprocessing
import queue
import socket
import asyncio
import os

import tkinter as tk
from tkinter import ttk
from io import StringIO
from pip_tkinter.config import get_build_platform

logger = logging.getLogger(__name__)

class InstallPage(ttk.Frame):
    """
    Manage search and install. Implements GUI for

    1. Search and Install from PyPI
    2. Install from local archive
    3. Install from requirements file
    4. Install from PythonLibs
    5. Install from alternate repository
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
        self.create_install_log_frame()

        self.container.tkraise()

    def create_install_log_frame(self):

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
        self.abort_install_button = ttk.Button(
            self.task_frame,
            text='Abort',
            command=lambda: self.abort_installation())
        self.abort_install_button.grid(
            row=1,
            column=1,
            sticky='e',
            padx=5,
            pady=5)
        self.abort_install_button.config(state='disabled')

    def navigate_back(self):
        self.debug_bar.config(text='No message')
        self.container.tkraise()

    def abort_installation(self):
        self.abort_install_button.config(state='disabled')
        self.frames_dict[self.current_frame].abort_installation()
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
        pypi_text = "Install From PyPI"
        local_archive_text = "Install From Local Archive"
        requirements_text = "Install From Requirements File"
        pythonlibs_text = "Install From PythonLibs"
        #alternate_repo_text = "Install From Alternate Repository"

        # Button style
        navbar_button_style = ttk.Style()
        navbar_button_style.configure(
            'navbar.TButton',
            padding=(6, 25)
        )

        self.button_pypi = ttk.Button(
            self.navbar_frame,
            text=pypi_text,
            state='active',
            style='navbar.TButton',
            command=lambda : self.show_frame('InstallFromPyPI')
        )
        self.button_pypi.grid(row=0, column=0, sticky='nwe')

        self.button_local_archive = ttk.Button(
            self.navbar_frame,
            text=local_archive_text,
            style='navbar.TButton',
            command=lambda : self.show_frame('InstallFromLocalArchive')
        )
        self.button_local_archive.grid(row=1, column=0, sticky='nwe')

        self.button_requirements = ttk.Button(
            self.navbar_frame,
            text=requirements_text,
            style='navbar.TButton',
            command=lambda : self.show_frame('InstallFromRequirements')
        )
        self.button_requirements.grid(row=2, column=0, sticky='nwe')

        if get_build_platform()=='Windows':

            self.button_pythonlibs = ttk.Button(
                self.navbar_frame,
                text=pythonlibs_text,
                style='navbar.TButton',
                command=lambda : self.show_frame('InstallFromPythonlibs')
            )
            self.button_pythonlibs.grid(row=3, column=0, sticky='nwe')

        '''
        self.button_alternate_repo = ttk.Button(
            self.navbar_frame,
            text=alternate_repo_text,
            style='navbar.TButton',
            command=lambda : self.show_frame('InstallFromAlternateRepo')
        )
        self.button_alternate_repo.grid(row=4, column=0, sticky='nwe')
        '''

    def manage_frames(self):
        """
        Manage multiple frames. Creates dictionary of multiple frames to
        be used for showing user different GUI frames for different ways of
        installation.
        """

        if get_build_platform()!='Windows':
            #If not windows
            frames_tuple = (
                InstallFromPyPI,
                InstallFromLocalArchive,
                InstallFromRequirements,
            )

        else:
            #Else add InstallFromPythonlibs page (for Windows systems)
            frames_tuple = (
                InstallFromPyPI,
                InstallFromLocalArchive,
                InstallFromRequirements,
                InstallFromPythonlibs,
            )

        self.frames_dict = {}
        for F in frames_tuple:
            frame_name = F.__name__
            new_frame = F(self.container, self)
            new_frame.grid(row=0, column=1, sticky='nsew')
            self.frames_dict[frame_name] = new_frame

        self.show_frame('InstallFromPyPI')

    def show_frame(self, frame_name):
        self.debug_bar.config(text='No message')
        self.current_frame = frame_name
        frame = self.frames_dict[frame_name]
        frame.tkraise()

    def show_task_frame(self):
        self.debug_bar.config(text='No message')
        self.task_frame.tkraise()
        self.go_back_button.config(state='disabled')
        self.abort_install_button.config(state='normal')

    def create_message_bar(self):
        """
        Create message bar for printing debug messages for user
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
        self.debug_bar.config(text="No message")


class InstallFromPyPI(ttk.Frame):

    def __init__(self, parent, controller):

        ttk.Frame.__init__(
            self,
            parent,
            borderwidth=3,
            padding=0.5,
            relief='ridge')
        self.grid(row=0, column=0, sticky='nse', pady=(1,1), padx=(1,1))
        self.controller = controller
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_nav_buttons()
        self.create_search_bar()
        self.create_multitem_treeview()

    def create_search_bar(self):

        import pkg_resources, os

        #Configure style for search bar
        data= pkg_resources.resource_string(__name__, 'pic.dat')
        global s1,s2
        s1 = tk.PhotoImage('search1', data=data, format='gif -index 0')
        s2 = tk.PhotoImage('search2', data=data, format='gif -index 1')
        style = ttk.Style()
        style.element_create('Search.field1', 'image', 'search1',
            ('focus', 'search2'), border=[25, 9, 14], sticky='ew')
        style.layout('Search.entry', [
            ('Search.field1', {'sticky': 'nswe', 'border': 1, 'children':
                [('Entry.padding', {'sticky': 'nswe', 'children':
                    [('Entry.textarea', {'sticky': 'nswe'})]
                })]
            })]
        )
        style.configure('Search.entry')

        #Create search bar and button
        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(
            self,
            style='Search.entry',
            textvariable=self.search_var)
        self.entry.bind('<Return>', lambda event : self.update_search_results())
        self.search_button = ttk.Button(
            self,
            text='Search',
            command=lambda : self.update_search_results())

        self.entry.grid(row=0, column=0, padx=3, pady=3, sticky='nwe')
        self.search_button.grid(row=0, column=1, padx=1, pady = 0, sticky='nw')

    def create_multitem_treeview(self):
        """
        Create multitem treeview to show search results with headers :
        1. Python Module
        2. Installed version
        3. Available versions

        List of buttons :
        1. navigate_back
        2. navigate_next
        3. search_button
        """

        self.headers = ['Python Module','Installed Version','Available Versions']
        from pip_tkinter.utils import MultiItemsList
        self.multi_items_list = MultiItemsList(self, self.headers)
        self.multi_items_list.scroll_tree.bind(
            '<<TreeviewSelect>>', lambda x : self.scroll_tree_select())

        self.package_subwindow = tk.LabelFrame(
            self,
            text="Package Details",
            padx=5,
            pady=5)
        self.package_subwindow.grid(row=2, column=0, columnspan=2, sticky='nswe')
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

        try:
            curr_item = self.multi_items_list.scroll_tree.focus()
            item_dict = self.multi_items_list.scroll_tree.item(curr_item)

            selected_module = 'Module Name : {}'.format(item_dict['values'][0])
            installed_version = 'Installed : {}'.format(item_dict['values'][1])
            latest_version = 'Latest : {}'.format(item_dict['values'][2])

            module_summary = "Not available"
            for module in self.search_results:
                if module[0] == item_dict['values'][0]:
                    module_summary = module[3]
                    break
            module_summary = 'Summary : {}'.format(module_summary)

            selected_package_details = '{}\n{}\n{}\n{}'.format(
                selected_module,
                module_summary,
                installed_version,
                latest_version)
            self.package_details.configure(state='normal')
            self.package_details.delete(1.0, 'end')
            self.package_details.insert(1.0, selected_package_details)
            self.package_details.configure(state='disabled')

        except:
            self.package_details.configure(state='normal')
            self.package_details.delete(1.0, 'end')
            self.package_details.insert(1.0, 'No module selected')
            self.package_details.configure(state='disabled')

    def update_search_results(self):
        """
        Show search results
        """

        self.search_term = self.search_var.get()
        #Update the bottom message bar to inform user that the program
        #is fetching search results
        self.controller.debug_bar.config(text='Fetching search results ...')

        #Disable buttons like :
        self.navigate_back.config(state='disabled')
        self.navigate_next.config(state='disabled')
        self.search_button.config(state='disabled')

        #Spawn a new thread for searching packages,
        #Search results will be returned in the @param : self.thread_queue
        self.search_queue = queue.Queue()

        from pip_tkinter.utils import pip_search_command
        self.search_thread = threading.Thread(
            target=pip_search_command,
            kwargs={
                'package_name':self.search_term,
                'thread_queue':self.search_queue})
        self.search_thread.start()
        self.after(100, self.check_search_queue)

    def check_search_queue(self):
        try:
            results_tuple = self.search_queue.get(0)
            self.search_results = results_tuple

            try:
                self.multi_items_list.populate_rows(results_tuple)
                self.controller.debug_bar.config(text='Fetched search results')

            except TypeError:
                self.controller.debug_bar.config(
                    text='Unable to fetch results. Please verify your internet\
                     connection')

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.search_button.config(state='normal')

        except queue.Empty:
            self.after(100, self.check_search_queue)

    def create_nav_buttons(self):
        """
        Create back and next buttons
        """

        self.navigate_back = ttk.Button(
            self,
            text="Back",
            command=lambda: self.navigate_previous_frame())
        self.navigate_back.grid(row=3, column=0, sticky='w')
        self.navigate_next = ttk.Button(
            self,
            text="Install",
            command=lambda: self.execute_pip_commands())
        self.navigate_next.grid(row=3, column=1, sticky='e')

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

        self.after(100, self.controller.debug_bar.config(
            text='Installing package. Please wait ...'))
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

            self.update_thread.start()

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.search_button.config(state='normal')

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
                            text='Error in installing package')
                    self.install_log_started = False
                    self.controller.go_back_button.config(state='normal')
                    self.controller.abort_install_button.config(state='disabled')
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


    def abort_search_command(self):
        """
        Stop searching for packages
        """
        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.search_button.config(state='normal')
        self.search_thread.stop()

    def abort_installation(self):
        """
        Stop pip installation : Currently not sure to provide option for
        aborting installation in between
        """
        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.search_button.config(state='normal')
        self.update_thread.terminate()


class InstallFromLocalArchive(ttk.Frame):

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
        self.create_entry_form()
        self.create_nav_buttons()

    def create_entry_form(self):
        """
        Make a labelled frame for entry widget with browse option
        """

        self.labelled_entry_frame = tk.LabelFrame(
            self,
            text="Enter path to local or remote archive file",
            padx=5,
            pady=30)

        #Create labelled entry frame
        self.labelled_entry_frame.grid(row=0, column=0, columnspan=2, sticky='nswe')
        self.labelled_entry_frame.columnconfigure(0, weight=1)

        #Create a entry widget for taking input for requirement file
        self.path_to_requirement = ttk.Entry(self.labelled_entry_frame)
        self.path_to_requirement.grid(row=0, column=0, sticky='nswe')

        #Create a tk browse dialog button
        self.browse_button = ttk.Button(
            self.labelled_entry_frame,
            text = "Browse",
            command = self.get_file_name)
        self.browse_button.grid(row = 0, column = 1, sticky = 'w')


    def get_file_name(self):

        from tkinter.filedialog import askopenfilename
        from tkinter.messagebox import showerror
        from os.path import expanduser

        home_directory = expanduser("~")

        self.req_file_name = askopenfilename(
            filetypes = (
                ("Archive file", "*.zip *.tar *tar.gz *.whl")
                ,("All files", "*.*")),
            initialdir = home_directory)

        if self.req_file_name:
            self.path_to_requirement.delete(0, 'end')
            self.path_to_requirement.insert('end', self.req_file_name)


    def create_nav_buttons(self):
        """
        Create back and next buttons
        """

        self.navigate_back = ttk.Button(
            self,
            text="Back",
            command=lambda: self.navigate_previous_frame())
        self.navigate_back.grid(row=2, column=0, sticky='w')
        self.navigate_next = ttk.Button(
            self,
            text="Install",
            command=lambda: self.execute_pip_commands())
        self.navigate_next.grid(row=2, column=1, sticky='e')

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
        self.browse_button.config(state='disabled')

        self.after(100, self.controller.debug_bar.config(
            text='Installing package from archive. Please wait ...'))
        self.after(100, self.update_installation_log)

    def update_installation_log(self):

        from pip_tkinter.utils import pip_install_from_local_archive

        try:
            selected_module = self.req_file_name
            self.controller.show_task_frame()
            self.install_queue = multiprocessing.Queue()

            self.update_thread = multiprocessing.Process(
                target=pip_install_from_local_archive,
                kwargs={
                    'package_args':selected_module,
                    'install_queue':self.install_queue})

            self.install_log_started = False
            self.after(100, self.log_from_install_queue)

            self.update_thread.start()
            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.search_button.config(state='normal')

        except AttributeError:
            self.controller.debug_bar.config(text='Please enter correct path')


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
                    if self.install_message[1]=='0':
                        self.controller.debug_bar.config(text='Done')
                    else:
                        self.controller.debug_bar.config(
                            text='Error in installing package')
                    self.install_log_started = False
                    self.controller.go_back_button.config(state='normal')
                    self.controller.abort_install_button.config(state='disabled')
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


    def abort_installation(self):
        """
        Stop pip installation : Currently not sure to provide option for
        aborting installation in between
        """
        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.browse_button.config(state='normal')
        self.update_thread.terminate()


class InstallFromRequirements(ttk.Frame):

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
        self.create_entry_form()
        self.create_nav_buttons()

    def create_entry_form(self):
        """
        Make a labelled frame for entry widget with browse option
        """

        self.labelled_entry_frame = tk.LabelFrame(
            self,
            text='Enter path to requirement file',
            padx=5,
            pady=30)

        #Create labelled entry frame
        self.labelled_entry_frame.grid(row=0, column=0, columnspan=2, sticky='nswe')
        self.labelled_entry_frame.columnconfigure(0, weight=1)

        #Create a entry widget for taking input for requirement file
        self.path_to_requirement = ttk.Entry(self.labelled_entry_frame)
        self.path_to_requirement.grid(row=0, column=0, sticky='nswe')

        #Create a tk browse dialog button
        self.browse_button = ttk.Button(
            self.labelled_entry_frame,
            text = 'Browse',
            command = self.get_file_name)
        self.browse_button.grid(row = 0, column = 1, sticky = 'w')

        #Create a note informing about the execution of requirement file
        s = ttk.Style()
        self.note_text = tk.Text(
            self.labelled_entry_frame,
            wrap='word',
            bg=s.lookup('TFrame', 'background'),
            height=8)
        self.note_text.grid(
            row=1,
            column=0,
            columnspan=2,
            sticky='nwse',
            pady=(30,20),
            padx=(20,20))
        note_content = "Note :\n\n\n\
1. 'pip' doesn't offer any guarantee of the order of installation of packages \
specified in requirements file.\n\n\
2. In case a particular version is not found, the closest matching version \
will be installed."
        self.note_text.insert('end', note_content)
        self.note_text.config(state='disabled')

    def get_file_name(self):

        from tkinter.filedialog import askopenfilename
        from tkinter.messagebox import showerror
        from os.path import expanduser

        home_directory = expanduser("~")
        self.req_file_name = askopenfilename(
            filetypes = (
                ("Requirement file", "*.txt")
                ,("All files", "*.*")),
            initialdir = home_directory)

        if self.req_file_name:
            self.path_to_requirement.delete(0, 'end')
            self.path_to_requirement.insert('end', req_file_name)


    def create_nav_buttons(self):
        """
        Create 'back' and 'next' buttons
        """

        self.navigate_back = ttk.Button(
            self,
            text="Back",
            command=lambda: self.navigate_previous_frame())
        self.navigate_back.grid(row=2, column=0, sticky='w')
        self.navigate_next = ttk.Button(
            self,
            text="Install",
            command=lambda: self.execute_pip_commands())
        self.navigate_next.grid(row=2, column=1, sticky='e')

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
        self.browse_button.config(state='disabled')

        self.after(100, self.controller.debug_bar.config(
            text='Installing package(s) from requirement file. Please wait ...'))
        self.after(100, self.update_installation_log)

    def update_installation_log(self):

        from pip_tkinter.utils import pip_install_from_requirements

        try:
            selected_module = self.req_file_name
            self.controller.show_task_frame()
            self.install_queue = multiprocessing.Queue()

            self.update_thread = multiprocessing.Process(
                target=pip_install_from_local_archive,
                kwargs={
                    'package_args':selected_module,
                    'install_queue':self.install_queue})

            self.install_log_started = False
            self.after(100, self.log_from_install_queue)

            self.update_thread.start()

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.search_button.config(state='normal')

        except AttributeError:
            self.controller.debug_bar.config(text='Please enter correct path')


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
                    if self.install_message[1]=='0':
                        self.controller.debug_bar.config(text='Done')
                    else:
                        self.controller.debug_bar.config(
                            text='Error in installing package')
                    self.install_log_started = False
                    self.controller.go_back_button.config(state='normal')
                    self.controller.abort_install_button.config(state='disabled')
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


    def abort_installation(self):
        """
        Stop pip installation : Currently not sure to provide option for
        aborting installation in between
        """
        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.browse_button.config(state='normal')
        self.update_thread.terminate()


class InstallFromPythonlibs(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(
            self,
            parent,
            borderwidth=3,
            padding=0.5,
            relief='ridge')

        self.grid(row=0, column=0, sticky='nse', pady=(1,1), padx=(1,1))
        self.controller = controller
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_buttons()
        self.create_multitem_treeview()
        self.create_search_bar()

    def create_buttons(self):
        """
        Create back and next buttons, Also creates option menu for selecting
        compatibility tag
        """

        self.navigate_back = ttk.Button(
            self,
            text='Back',
            command=lambda: self.navigate_previous_frame())
        self.navigate_back.grid(row=3, column=0, sticky='w')

        options = ('Select compatible dist.',)
        self.options_var = tk.StringVar(self)
        self.options_var.set(options[0])
        self.option_menu = tk.OptionMenu(self, self.options_var, *options)
        self.option_menu.grid(row=3, column=1, sticky='e')
        self.option_menu.config(state='disabled')

        self.sync_button = ttk.Button(
            self,
            text='Sync',
            command=lambda: self.sync_pythonlibs_packages())
        self.sync_button.grid(row=3, column=2, sticky='e')

        self.navigate_next = ttk.Button(
            self,
            text='Install',
            command=lambda: self.execute_pip_commands())
        self.navigate_next.grid(row=3, column=3, sticky='e')

    def navigate_previous_frame(self):
        """
        Navigate to previous frame
        """
        self.controller.controller.show_frame('WelcomePage')

    def sync_pythonlibs_packages(self):
        """
        Sync the json file for PythonLibs at :
        https://raw.githubusercontent.com/upendra-k14/pythonlibs_modules/master/pythonlibs.json
        """

        from pip_tkinter.utils import create_resource_directory
        resource_dir = create_resource_directory()

        url = "https://raw.githubusercontent.com/upendra-k14/pythonlibs_modules/master/pythonlibs.json"

        self.update_queue = multiprocessing.Queue()
        self.after(10, self.update_sync_messages)

        self.sync_button.config(state='disabled')
        from pip_tkinter.utils import downloadfile
        downloadfile(url, self.update_queue)

    def update_sync_messages(self):
        try:
            message = self.update_queue.get(0)
            if (message[0]==3):
                self.controller.debug_bar.config(text=message[1])
                self.sync_button.config(state='normal')
                return
            elif (message[0]==1 or message[0]==0):
                self.controller.debug_bar.config(text='Syncing : {}'.format(str(message[1])))
                self.after(10, self.update_sync_messages)
            elif (message[0]==2):
                self.controller.debug_bar.config(text=message[1])
                self.sync_button.config(state='normal')
                return

        except queue.Empty:
            self.after(10, self.update_sync_messages)

    def create_search_bar(self):

        style = ttk.Style()
        style.configure('Search.entry')

        #Create search bar and button
        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(
            self,
            style='Search.entry',
            textvariable=self.search_var)
        self.entry.bind('<Return>', lambda event : self.update_search_results())
        self.search_button = ttk.Button(
            self,
            text='Search',
            command=lambda : self.update_search_results())

        self.entry.grid(
            row=0,
            column=0,
            columnspan=3,
            padx=3,
            pady=3,
            sticky='nwe')
        self.search_button.grid(
            row=0,
            column=3,
            padx=1,
            pady = 0,
            sticky='nw')

    def create_multitem_treeview(self):
        """
        Create multitem treeview to show search results with headers :
        1. Python Module
        2. Installed Version
        3. Available Version

        List of buttons :
        1. navigate_back
        2. navigate_next
        3. search_button
        """

        self.headers = ['Python Module', 'Available Version']
        from pip_tkinter.utils import MultiItemsList
        self.multi_items_list = MultiItemsList(self, self.headers)
        self.multi_items_list.scroll_tree.bind(
            '<<TreeviewSelect>>', lambda x : self.scroll_tree_select())
        self.multi_items_list.myframe.grid(
            row=1,
            column=0,
            columnspan=4,
            sticky='nsew')
        self.package_subwindow = tk.LabelFrame(
            self,
            text="Package Details",
            padx=5,
            pady=5)
        self.package_subwindow.grid(
            row=2,
            column=0,
            columnspan=4,
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

        try:
            curr_item = self.multi_items_list.scroll_tree.focus()
            item_dict = self.multi_items_list.scroll_tree.item(curr_item)

            selected_module = 'Module Name : {}'.format(item_dict['values'][0])
            available_version = 'Version : {}'.format(item_dict['values'][1])
            module_summary = 'Summary : {}'.format(item_dict['values'][2])
            home_page = 'Home Page : {}'.format(item_dict['values'][3])
            last_updated = 'Last Updated : {}'.format(item_dict['values'][4])

            selected_package_details = '{}\n{}\n{}\n{}\n{}'.format(
                selected_module,
                available_version,
                module_summary,
                home_page,
                last_updated,)
            self.package_details.configure(state='normal')
            self.package_details.delete(1.0, 'end')
            self.package_details.insert(1.0, selected_package_details)
            self.package_details.configure(state='disabled')

            #search for module name in self.search_results
            new_options = []
            for items in self.search_results:
                if items[0]==item_dict['values'][0]:
                    self.module_details = items
                    for x in items[5:]:
                        new_options.append(x[0])
                    new_options = tuple(new_options)

            #Update compatibility options in option menu
            self.option_menu.config(state='normal')
            self.option_menu['menu'].delete(0,'end')

            #update options menu
            for opt_tag in new_options:
                self.option_menu['menu'].add_command(
                    label=opt_tag,
                    command=tk._setit(self.options_var, opt_tag))

        except Exception as e:
            print (e)
            self.package_details.configure(state='normal')
            self.package_details.delete(1.0, 'end')
            self.package_details.insert(1.0, 'No module selected')
            self.package_details.configure(state='disabled')

    def update_search_results(self):
        """
        Show search results
        """

        self.search_term = self.search_var.get()
        #Update the bottom message bar to inform user that the program
        #is fetching search results
        self.controller.debug_bar.config(text='Fetching search results ...')

        #Disable buttons like :
        self.navigate_back.config(state='disabled')
        self.navigate_next.config(state='disabled')
        self.search_button.config(state='disabled')

        #Spawn a new thread for searching packages,
        #Search results will be returned in the @param : self.thread_queue
        self.search_queue = multiprocessing.Queue()

        from pip_tkinter.utils import pythonlibs_search_command
        self.search_thread = multiprocessing.Process(
            target=pythonlibs_search_command,
            kwargs={
                'package_name':self.search_term,
                'thread_queue':self.search_queue})
        self.search_thread.start()
        self.after(100, self.check_search_queue)

    def check_search_queue(self):
        try:
            results_tuple = self.search_queue.get(0)
            self.search_results = results_tuple

            try:
                self.multi_items_list.populate_rows(results_tuple)
                self.module_details = None
                self.controller.debug_bar.config(text='Fetched search results')

            except TypeError:
                self.controller.debug_bar.config(
                    text='Unable to fetch results. Please verify your internet\
                     connection')

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.search_button.config(state='normal')

        except queue.Empty:
            self.after(100, self.check_search_queue)

    def execute_pip_commands(self):
        """
        Execute pip commands
        """
        self.navigate_back.config(state='disabled')
        self.navigate_next.config(state='disabled')
        self.search_button.config(state='disabled')

        self.after(100, self.controller.debug_bar.config(
            text='Installing package. Please wait ...'))
        self.after(100, self.update_installation_log)

    def update_installation_log(self):

        from pip_tkinter.utils import pip_install_from_pythonlibs

        try:
            curr_item = self.multi_items_list.scroll_tree.focus()
            item_dict = self.multi_items_list.scroll_tree.item(curr_item)
            dists = item_dict['values'][5]

            self.controller.show_task_frame()
            self.install_queue = multiprocessing.Queue()

            selected_url = ''
            if self.module_details==None:
                return
            else:
                for x in self.module_details[5:]:
                    if x[0]==self.options_var.get():
                        selected_url = x[3]

            self.update_thread = multiprocessing.Process(
                target=pip_install_from_pythonlibs,
                kwargs={
                    'package_url':selected_url,
                    'install_queue':self.install_queue})

            self.install_log_started = False
            self.error_log_started = False
            self.after(100, self.log_from_download_queue)
            #self.after(100, self.log_from_install_queue)

            self.update_thread.start()

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.search_button.config(state='normal')

        except IndexError:
            self.controller.debug_bar.config(text='Select correct package')

    def log_from_download_queue(self):
        try:
            self.install_message = self.install_queue.get(0)
            if (self.install_message[0]==0):
                self.controller.process_details.config(state='normal')
                self.controller.process_details.delete(1.0,'end')
                self.controller.process_details.config(state='disabled')

            elif (self.install_message[0]==1):
                self.controller.process_details.config(state='normal')
                self.controller.process_details.delete(1.0,'end')
                self.controller.process_details.insert(
                    'end',
                    'Downloading {}\%\n'.format(self.install_message[1]))
                self.controller.process_details.config(state='disabled')

            elif (self.install_message[0]==2):
                self.after(20, self.log_from_install_queue)
                return

            else:
                self.controller.process_details.config(state='normal')
                self.controller.process_details.insert(
                    'end',
                    self.install_message[1])
                self.controller.process_details.config(state='disabled')
                return

            self.after(20, self.log_from_download_queue)

        except queue.Empty:
            self.after(100, self.log_from_download_queue)


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
                            text='Error in installing package')
                    self.install_log_started = False
                    self.controller.go_back_button.config(state='normal')
                    self.controller.abort_install_button.config(state='disabled')
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


    def abort_search_command(self):
        """
        Stop searching for packages
        """
        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.search_button.config(state='normal')
        self.search_thread.stop()

    def abort_installation(self):
        """
        Stop pip installation : Currently not sure to provide option for
        aborting installation in between
        """
        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        self.search_button.config(state='normal')
        self.update_thread.terminate()

class InstallFromAlternateRepo(ttk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(
                        self,
                        parent,
                        borderwidth=3,
                        padding=0.5,
                        relief='ridge')
        self.grid(row=0, column=0, sticky='nse', pady=(1,1), padx=(1,1))
        self.controller = controller
        label = tk.Label(self, text="Install From an alternate respository")
        label.pack(pady=10, padx=10)


if __name__ == "__main__":

    # If you want to check GUI
    root = tk.Tk()
    # root.resizable(width='false', height='false')
    install_app = InstallPage(root)
    root.mainloop()
