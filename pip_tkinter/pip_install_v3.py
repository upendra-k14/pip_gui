from __future__ import absolute_import

import pip
import subprocess
import sys
import copy

from pip.commands.search import SearchCommand, transform_hits, highest_version
from pip.exceptions import CommandError
from pip.basecommand import SUCCESS
from pip_tkinter._vendor import pkg_resources
from pip import parseopts, main

from io import StringIO

import tkinter as tk
from tkinter import ttk

search_hits = {}
sysout = StringIO()
syserr = StringIO()

class redirect:
    """Context manager for temporarily redirecting stdout/err.
    Simplified and generalize from contextlib.redirect_stdout.
    """

    def __init__(self, stdfile, new_target):
        self._stdfile = stdfile  # 'stdout' or 'stderr'
        self._new_target = new_target

    def __enter__(self):
        self._old = getattr(sys, self._stdfile)
        setattr(sys, self._stdfile, self._new_target)
        return self._new_target

    def __exit__(self, exctype, excinst, exctb):
        setattr(sys, self._stdfile, self._old)

# For GUI version, redirects would be here, done once.
# Put in runpip for prototype testing in text mode, so can print.
def runpip(argstring):
    '''Run pip with argument string containing command and options.

    Argstring is quoted version of what would follow 'pip'
    on command line.
    '''
    with redirect('stdout', sysout) as f1, redirect('stderr', syserr) as f2:
        status = main(argstring.split())
        out = sysout.getvalue()
        err = syserr.getvalue()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return status, out, err

class GUISearchCommand(SearchCommand):
    """
    Inherited the class : pip.commands.search.SearchCommand to override
    run method

    Advantage of inheriting the class is that we can have better control of
    pip. For example, currently pip search gives output for latest version.
    But, we can retrieve output for all available versions.

    Another advantage is that search can now be done with less time lag as
    compared to pip.main().
    """

    def run(self, options, args):
        if not args:
            raise CommandError('Missing required argument (search query).')
        query = args
        try:
            #The developer version of pip uses options as argument
            pypi_hits = self.search(query,options)
        except TypeError:
            #But, the stable version of pip uses options.index as argument
            pypi_hits = self.search(query,options.index)
        hits = transform_hits(pypi_hits)
        global search_hits
        search_hits = copy.deepcopy(hits)
        return SUCCESS

def get_search_results(hits):
    """
    This code is taken from pip.commands.search.print_results(). It is modified
    to return results in dictionary format instead of printing results
    For all the search results obtained, we can check if a package is already
    installed or not. If installed then the version of installed package is
    found and stored.
    """
    if not hits:
        return None

    #Here pkg_resources is a module of pip._vendor. It has been included
    #in pip gui because as mentioned by pip, this module is considered to
    #be 'immutable'. There are very less chances that it will changed in future
    installed_packages = [p.project_name for p in pkg_resources.working_set]
    for hit in hits:
        hit['latest'] = highest_version(hit['versions'])
        name = hit['name']
        if name in installed_packages:
            dist = pkg_resources.get_distribution(name)
            hit['installed'] = dist.version

    return hits


def pip_search_command(package_name):
    """
    Uses pip.commands.search.SearchCommand to retrieve results of 'pip search'
    """

    search_object = GUISearchCommand()
    cmd_name, cmd_args = parseopts(['search',package_name])
    search_object.main(cmd_args)
    return get_search_results(search_hits)

def pip_install_command_PyPI(package_args):
    """
    Wrapper for installing pip package from PyPI
    """
    return runpip('install -U {}'.format(package_args))

class InstallPage(tk.Tk):
    """
    Manage search and install. Implements GUI for

    1. Search and Install from PyPI
    2. Install from local archive
    3. Install from requirements file
    4. Install from PythonLibs
    5. Install from alternate repository
    """

    def __init__(self, root):
        tk.Frame.__init__(self, root)

        #Set properties for root window
        self.parent = root
        self.parent.title("PIP Package Manager")
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)

        #Set theme style
        theme_style=ttk.Style()
        if 'clam' in theme_style.theme_names():
            theme_style.theme_use('clam')

        #Create container to hold other frames
        self.container = ttk.Frame(self.parent)
        self.container.grid(row=0, column=0, sticky='nsew')
        self.container.rowconfigure(0, weight=1)

        self.adjustWindow()
        self.manage_frames()
        self.create_side_navbar()

    def create_side_navbar(self):
        """
        Create side navigation bar for providing user with options for
        selecting different ways of installation
        """

        #Create a navbar frame in which all navbar buttons will lie
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
        #Configure style for navbar frame

        #Button text
        pypi_text = "Install From PyPI"
        local_archive_text = "Install From Local Archive"
        requirements_text = "Install From Requirements File"
        pythonlibs_text = "Install From PythonLibs"
        alternate_repo_text = "Install From Alternate Repository"

        #Button style
        navbar_button_style = ttk.Style()
        navbar_button_style.configure(
                                'navbar.TButton',
                                padding=(6,25))

        self.button_pypi = ttk.Button(
                                self.navbar_frame,
                                text=pypi_text,
                                state='active',
                                style='navbar.TButton')
        self.button_pypi.grid(row=0, column=0, sticky='nwe')

        self.button_local_archive = ttk.Button(
                                        self.navbar_frame,
                                        text=local_archive_text,
                                        style='navbar.TButton')
        self.button_local_archive.grid(row=1, column=0, sticky='nwe')

        self.button_requirements = ttk.Button(
                                        self.navbar_frame,
                                        text=requirements_text,
                                        style='navbar.TButton')
        self.button_requirements.grid(row=2, column=0, sticky='nwe')

        self.button_pythonlibs = ttk.Button(
                                    self.navbar_frame,
                                    text=pythonlibs_text,
                                    style='navbar.TButton')
        self.button_pythonlibs.grid(row=3, column=0, sticky='nwe')

        self.button_alternate_repo = ttk.Button(
                                        self.navbar_frame,
                                        text=alternate_repo_text,
                                        style='navbar.TButton')
        self.button_alternate_repo.grid(row=4, column=0, sticky='nwe')


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
                    InstallFromPythonlibs,
                    InstallFromAlternateRepo)

        self.frames_dict = {}
        for F in frames_tuple:
            new_frame = F(self.container, self)
            new_frame.grid(row=0, column=1, sticky='nsew')
            self.frames_dict[F] = new_frame

        self.show_frame(InstallFromPyPI)

    def show_frame(self, frame_name):
        frame = self.frames_dict[frame_name]
        frame.tkraise()

    def adjustWindow(self):
        """
        Set the window at center position of the screen and adjust it's
        size depending on screen size
        """

        #Get the screen width and screen height
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        #Calculate the appropriate window width and height
        self.window_width = int(0.75*screen_width);
        self.window_height = int(0.75*screen_height);

        #Determine the position of the window
        x = (screen_width - self.window_width)//2
        y = (screen_height - self.window_height)//2

        self.parent.geometry('{}x{}+{}+{}'.format(
                                            str(self.window_width),
                                            str(self.window_height),
                                            str(x),str(y)))

    def onExit(self):
        self.parent.destroy()

class InstallFromPyPI(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Install Page")
        label.pack(pady=10, padx=10)

class InstallFromLocalArchive(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Install From Local Archive")
        label.pack(pady=10, padx=10)

class InstallFromRequirements(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Install From Requirements File")
        label.pack(pady=10, padx=10)

class InstallFromPythonlibs(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Install From Python libs")
        label.pack(pady=10, padx=10)

class InstallFromAlternateRepo(tk.Frame):

    def __init__(self, parent, controller):
        ttk.Frame.__init__(self, parent)
        label = tk.Label(self, text="Install From an alternate respository")
        label.pack(pady=10, padx=10)


if __name__ == "__main__":

    #If you want to check GUI
    root = tk.Tk()
    #root.resizable(width='false', height='false')
    install_app = InstallPage(root)
    root.mainloop()

    #If you want to check search command
    #print (pip_search_command(package_name))
