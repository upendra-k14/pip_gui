# coding=utf-8
from __future__ import absolute_import

import logging
import threading
import queue
import socket
import asyncio

import tkinter as tk
from tkinter import ttk
from io import StringIO

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
        alternate_repo_text = "Install From Alternate Repository"

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

        '''
        self.button_pythonlibs = ttk.Button(
            self.navbar_frame,
            text=pythonlibs_text,
            style='navbar.TButton',
            command=lambda : self.show_frame('InstallFromPythonlibs')
        )
        self.button_pythonlibs.grid(row=3, column=0, sticky='nwe')

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

        frames_tuple = (
            InstallFromPyPI,
            InstallFromLocalArchive,
            InstallFromRequirements,
        )

        self.frames_dict = {}
        for F in frames_tuple:
            frame_name = F.__name__
            new_frame = F(self.container, self)
            new_frame.grid(row=0, column=1, sticky='nsew')
            self.frames_dict[frame_name] = new_frame

        self.show_frame('InstallFromPyPI')

    def show_frame(self, frame_name):
        frame = self.frames_dict[frame_name]
        frame.tkraise()

    def create_message_bar(self):
        """
        Create message bar for printing debug messages for user
        """

        self.debug_bar = ttk.Label(
            self.container,
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
                if module['name'] == item_dict['values'][0]:
                    module_summary = module['summary']
                    break
            module_summary = 'Summary {}'.format(module_summary)

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
            self.search_results = self.search_queue.get(0)
            results_tuple = []

            try:
                for item in self.search_results:
                    if self.search_term in item['name']:
                        if 'installed' in item.keys():
                            results_tuple.insert(0, (
                                item['name'],
                                item['installed'],
                                item['latest']))
                        else:
                            results_tuple.insert(0, (
                                item['name'],
                                'not installed',
                                item['latest']))
                self.multi_items_list.populate_rows(results_tuple)
                self.controller.debug_bar.config(text='Fetched search results')

            except TypeError:
                self.controller.debug_bar.config(
                    text='Unable to fetch results. Please verify your internet connection')

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

        self.after(0, self.controller.debug_bar.config(text='Installing package. Please wait ...'))
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
            self.controller.debug_bar.config(text='Successfully installed')
        else:
            self.controller.debug_bar.config(text='Error in installing package')

    def abort_search_command(self):
        """
        Stop pip installation : Currently not sure to provide option for
        aborting installation in between
        """
        self.search_thread.stop()

    def check_install_queue(self):
        try:
            self.install_message = self.install_queue.get(0)

            if str(self.install_message) == 'install_started':
                self.controller.debug_bar.config(
                    text='Installing package. Please wait ...')

            self.navigate_back.config(state='normal')
            self.navigate_next.config(state='normal')
            self.search_button.config(state='normal')

        except queue.Empty:
            self.after(100, self.check_search_queue)

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
            self.path_to_requirement.insert('end', req_file_name)


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
        #self.search_button.config(state='disabled')

        self.after(0, self.controller.debug_bar.config(
            text='Installing package from archive. Please wait ...'))
        self.after(100, self.update_install_text)

        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')
        #self.search_button.config(state='normal')

    def update_install_text(self):
        """
        Update install text
        """
        from pip_tkinter.utils import pip_install_from_local_archive

        try:
            selected_module = self.req_file_name
            status, output, err = pip_install_from_local_archive(selected_module)

            if str(status) == '0':
                self.controller.debug_bar.config(text='Successfully installed')
            else:
                self.controller.debug_bar.config(text='Error in installing package')
                print (err)

        except AttributeError:
            self.controller.debug_bar.config(text='Please enter the path')


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
        self.event_loop = asyncio.get_event_loop()

    def create_entry_form(self):
        """
        Make a labelled frame for entry widget with browse option
        """

        self.labelled_entry_frame = tk.LabelFrame(
            self,
            text="Enter path to requirement file",
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

        #Create a note informing about the execution of requirement file
        s = ttk.Style()
        self.note_text = tk.Text(
            self.labelled_entry_frame,
            wrap='word',
            bg=s.lookup('TFrame', 'background'),
            height=8)
        self.note_text.grid(row=1, column=0, columnspan=2, sticky='nwse', pady=(30,20))
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

        self.after(0, self.controller.debug_bar.config(
            text='Installing package(s) from requirement file. Please wait ...'))
        self.after(100, self.update_install_text)

        self.navigate_back.config(state='normal')
        self.navigate_next.config(state='normal')

    def update_install_text(self):
        """
        Update install text
        """
        from pip_tkinter.utils import pip_install_from_requirements

        try:
            selected_module = self.req_file_name
            status, output, err = pip_install_from_requirements(selected_module)

            if str(status) == '0':
                self.controller.debug_bar.config(text='Successfully installed')
            else:
                self.controller.debug_bar.config(text='Error in installing package')
                print (err)

        except AttributeError:
            self.controller.debug_bar.config(text='Enter path to requirement file')


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
        label = tk.Label(self, text="Install From Python libs")
        label.pack(pady=10, padx=10)
        self.event_loop = asyncio.get_event_loop()


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
        self.event_loop = asyncio.get_event_loop()


if __name__ == "__main__":

    # If you want to check GUI
    root = tk.Tk()
    # root.resizable(width='false', height='false')
    install_app = InstallPage(root)
    root.mainloop()

    # If you want to check search command
    # print (pip_search_command(package_name))
