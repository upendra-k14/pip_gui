# coding=utf-8
from __future__ import absolute_import

from io import StringIO

import tkinter as tk
from tkinter import ttk

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
        self.manage_frames()
        self.create_side_navbar()
        self.create_message_bar()

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
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.create_search_bar()
        self.create_multitem_treeview()
        self.create_nav_buttons()

    def create_search_bar(self):

        import pkg_resources, os

        resource_package = __name__
        resource_path = os.path.join('pic.dat')

        #Configure style for search bar
        data= pkg_resources.resource_string(resource_package, resource_path)
        global s1,s2
        s1 = tk.PhotoImage('search1', data=data, format='gif -index 0')
        s2 = tk.PhotoImage('search2', data=data, format='gif -index 1')
        style = ttk.Style()
        style.element_create('Search.field', 'image', 'search1',
            ('focus', 'search2'), border=[25, 9, 14], sticky='ew')
        style.layout('Search.entry', [
            ('Search.field', {'sticky': 'nswe', 'border': 1, 'children':
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

        search_term = self.search_var.get()
        print (search_term)
        try:
            from pip_tkinter.utils import pip_search_command
            self.search_results = pip_search_command(search_term)
        except TypeError:
            self.search_results = []

        results_tuple = []
        for item in self.search_results:
            if search_term in item['name']:
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
        pass



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

        req_file_name = askopenfilename(
            filetypes = (
                ("Archive file", "*.zip *.tar *tar.gz *.whl")
                ,("All files", "*.*")),
            initialdir = home_directory)

        if req_file_name:
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
        pass
