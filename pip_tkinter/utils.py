#encoding=utf-8
from __future__ import absolute_import

import sys
import threading
import multiprocessing
import http.client
import asyncio
import logging
import os
import subprocess
import select
import codecs

from pip_tkinter.config import get_build_platform
from pip.commands.search import highest_version
from pip import parseopts
from io import StringIO
from io import TextIOWrapper

import tkinter as tk
from tkinter import ttk

search_hits = {}

class MultiItemsList(object):

    """
    Class for creating Treeview to show list of packages : provides options
    for selecting items and specifying number of headers for the treeview

    :param self.scroll_tree: tkinter treeview variable
    :param parent: parent frame for treeview
    :param headers_list: list of headers or fields in treeview
    :param self.items_list: list of items for treeview
    """

    def __init__(self, parent, headers_list=None):
        """
        Initialize variables needed for creating Treeview
        """

        #: Initialized with None, will store reference to tkinter treeview
        self.scroll_tree = None
        self.parent = parent
        self.headers_list = headers_list
        self.items_list = None
        self.create_treeview()
        self.create_headers()

    def create_treeview(self):
        """
        Create a multi items list consisting of a frame, horizontal and vertical
        scroll bar and Treeview

        :param self.myframe: a tkinter frame for encapsulating treeview
            contents with parent frame as self.parent
        :param vrtl_scrbar: vertical scrollbar for treeview
        :param hrtl_scrbar: horizontal scrollbar for treeview
        """

        self.myframe = ttk.Frame(self.parent)
        self.myframe.grid(row=1, column=0, columnspan=2, sticky='nswe')

        self.scroll_tree = ttk.Treeview(
            self.myframe,
            columns=self.headers_list,
            show='headings',
            selectmode='browse')

        vrtl_scrbar = ttk.Scrollbar(
            self.myframe,
            orient="vertical",
            command=self.scroll_tree.yview)
        hrtl_scrbar = ttk.Scrollbar(
            self.myframe,
            orient="horizontal",
            command=self.scroll_tree.xview)

        self.scroll_tree.configure(
            yscrollcommand=vrtl_scrbar.set,
            xscrollcommand=hrtl_scrbar.set)

        self.scroll_tree.grid(column=0, row=0, sticky='nswe', in_=self.myframe)
        vrtl_scrbar.grid(column=1, row=0, sticky='ns', in_=self.myframe)
        hrtl_scrbar.grid(column=0, row=1, sticky='ew', in_=self.myframe)

        self.myframe.grid_columnconfigure(0, weight=1)
        self.myframe.grid_rowconfigure(0, weight=1)

    def create_headers(self):
        """
        Specifies headers and width of header columns for the treeview
        """

        for header in self.headers_list:
            self.scroll_tree.heading(header, text=header)
            self.scroll_tree.column(header, width=30)

    def populate_rows(self, items_list=None):
        """
        Populate treeview with list of items

        :param items_list: list of items by which treeview is populated
        """
        self.scroll_tree.delete(*self.scroll_tree.get_children())
        self.items_list = items_list
        for item in self.items_list:
            self.scroll_tree.insert('', 'end', values=item)



class Redirect:
    """Context manager for temporarily redirecting stdout/err.
    Simplified and generalize from contextlib.redirect_stdout.
    (DEPRECATED)
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
    """
    Run pip with argument string containing command and options.(DEPRECATED and
    replaced with runpip_using_subprocess method)

    :param argstring: is quoted version of what would follow 'pip' on command \
    line.
    """
    sysout = StringIO()
    syserr = StringIO()

    import pip

    with Redirect('stdout', sysout) as f1, Redirect('stderr', syserr) as f2:
        #Clear all loggers
        pip.logger.consumers = []

        status = pip.main(argstring.split())
        out = sysout.getvalue()
        err = syserr.getvalue()

    sysout.seek(0); sysout.truncate(0)
    syserr.seek(0); syserr.truncate(0)
    return status, out, err

def runpip_using_subprocess(argstring):
    """
    Run pip with argument string containing command and options. Uses
    subprocess module for executing pip commands. Returns output and error
    once execution of process teriminates

    :param argstring: is quoted version of what would follow 'pip' on command \
    line.
    """

    #Explicitly specify encoding of environment for subprocess in order to
    #avoid errors
    my_env = os.environ
    my_env['PYTHONIOENCODING'] = 'utf-8'
    
    pip_process = subprocess.Popen(
        argstring.split(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env = my_env,
    )
    
    pip_output, pip_error = pip_process.communicate()
    
    return (pip_output.decode('utf-8'), pip_error.decode('utf-8'))

class RunpipSubprocess():
    """
    Run pip with argument string containing command and options. Uses
    subprocess module for executing pip commands. Logs real time output in
    output queue and error queue.
    """

    def __init__(self, argstring, output_queue):
        """
        Initialize subprocess for running pip commands.

        :param output_queue: queue for buffering line by line output
        :param argstring: is quoted version of what would follow 'pip' on
         command line.
        """

        self.pip_process = subprocess.Popen(
            argstring.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        self.output_queue = output_queue

    def start_logging_threads(self):
        """
        Starts logging to output and error queue
        """

        fileio_streams = [
            self.pip_process.stdout.fileno(),
            self.pip_process.stderr.fileno(),]
        io_iterator = select.select(fileio_streams, [], [])

        self.output_queue.put((0,'process_started'))

        while True:
            for file_descrp in io_iterator[0]:
                if file_descrp == self.pip_process.stdout.fileno():
                    pipout = self.pip_process.stdout.readline()
                    self.output_queue.put((1,pipout))
                elif file_descrp == self.pip_process.stderr.fileno():
                    piperr = self.pip_process.stderr.readline()
                    self.output_queue.put((2,piperr))

            if self.pip_process.poll() != None:
                self.output_queue.put((3,self.pip_process.poll()))
                break


    def getoutput(self):
        """
        Iterate over output line by line : multiplexing output and error
        stream
        """

        self.output_queue.put('start_logging_installation')
        for line in iter(self.pip_process.stdout.readline, b''):
            print ('utils',line)
            self.output_queue.put(line)
        self.output_queue.put('end_logging_installation')
        self.pip_process.stdout.close()
        self.pip_process.wait()

    def geterror(self):
        """
        Iterate over error line by line (DEPRECATED)
        """

        self.error_queue.put('start_logging_error')
        for line in iter(self.pip_process.stderr.readline, b''):
            print ('error',line)
            self.error_queue.put(line)
        self.error_queue.put('end_logging_error')
        self.pip_process.stderr.close()
        self.pip_process.wait()

def pip_search_command(package_name=None, thread_queue=None):
    """
    Uses subprocess to retrieve results of 'pip search'
    """
    import re

    search_result, errors = runpip_using_subprocess(
        'pip3 search {}'.format(package_name))

    print (errors)

    if errors.strip() != '':
        thread_queue.put(errors)

    count = 0
    installed_packages = []
    
    for x in search_result.split("\n"):
        try:
            if ('INSTALLED:' not in x) and (
                ('(' in x) and (')' in x) and (
                    not x.startswith('-'))):
                open_bracket_index = x.index('(')
                close_bracket_index = x.index(')')
                pkg_name = x[:open_bracket_index-1].strip()
                latest_version = x[open_bracket_index+1:close_bracket_index]
                summary = re.split(r'\)\s+- ',x)[1].strip()
                installed_packages.append(
                    [pkg_name,'Not installed',latest_version,summary])
                count = count + 1
            elif 'INSTALLED:' in x:
                st_index = x.index(':')
                end_index = x.index('(')
                installed_packages[-1][1] = x[st_index+1:end_index].strip()
            else:
                installed_packages[-1][3] = '{} {}'.format(
                    installed_packages[-1][3],x.strip())
        except e:
            pass
    thread_queue.put([tuple(x) for x in installed_packages])

def pip_list_command():
    """
    Lists all installed packages
    """

    list_output, error = runpip_using_subprocess('pip3 list')
    installed_pkg_list = list_output.splitlines()
    for i in range(len(installed_pkg_list)):
        pkg_name, pkg_version = installed_pkg_list[i].split('(')
        pkg_version = pkg_version[:len(pkg_version)-1]
        latest_version = '  '
        installed_pkg_list[i] = (pkg_name, pkg_version)
    return installed_pkg_list

def pip_list_outdated_command():
    """
    Lists all outdated installed packages
    """

    list_output, error = runpip_using_subprocess('pip3 list --outdated')
    installed_pkg_list = list_output.splitlines()
    formatted_list = []
    for i in range(len(installed_pkg_list)):
        try:
            open_bracket_index = installed_pkg_list[i].index('(')
            close_bracket_index = installed_pkg_list[i].index(')')
            pkg_name = installed_pkg_list[i][:open_bracket_index-1]
            pkg_version = installed_pkg_list[i][
                open_bracket_index+1:close_bracket_index]
            latest_version = installed_pkg_list[i].split(
                ' - Latest: ')[1].split(' [')[0]
            formatted_list.append((pkg_name, pkg_version, latest_version))
        except IndexError:
            pass
        except ValueError:
            pass
    return formatted_list

def pip_show_command(package_args):
    """
    Show details of a installed package
    """
    return runpip('show --no-cache-dir {}'.format(package_args))

def pip_install_from_PyPI(package_args=None, install_queue=None):
    """
    Wrapper for installing pip package from PyPI
    """
    if get_build_platform()=='Windows':
        permission_prefix = ''
    elif get_build_platform()=='Linux':
        permission_prefix = 'gksudo -- '
    package_args = '{}pip3 install -U --no-cache-dir {}'.format(permission_prefix, package_args)
    install_process = RunpipSubprocess(package_args, install_queue)
    install_process.start_logging_threads()

def pip_install_from_local_archive(package_args, install_queue=None):
    """
    Wrapper for installing pip package from local Archive
    """
    if get_build_platform()=='Windows':
        permission_prefix = ''
    elif get_build_platform()=='Linux':
        permission_prefix = 'gksudo -- '
    package_args = '{}pip3 install {}'.format(permission_prefix, package_args)
    install_process = RunpipSubprocess(package_args, install_queue)
    install_process.start_logging_threads()

def pip_install_from_requirements(package_args, install_queue=None):
    """
    Wrapper for installing pip package from requirements file
    """
    if get_build_platform()=='Windows':
        permission_prefix = ''
    elif get_build_platform()=='Linux':
        permission_prefix = 'gksudo -- '
    package_args = '{}pip3 install -r {}'.format(permission_prefix, package_args)
    install_process = RunpipSubprocess(package_args, install_queue)
    install_process.start_logging_threads()

def pip_install_from_alternate_repo(package_args):
    """
    Wrapper for installing pip package from Pythonlibs
    """
    return (runpip('install --index-url{}'.format(package_args)))

def pip_uninstall(package_args, uninstall_queue=None):
    """
    Uninstall packages
    """
    if get_build_platform()=='Windows':
        permission_prefix = ''
    elif get_build_platform()=='Linux':
        permission_prefix = 'gksudo -- '
    package_args = 'pip3 uninstall --yes {}'.format(permission_prefix, package_args)
    uninstall_process = RunpipSubprocess(package_args, uninstall_queue)
    uninstall_process.start_logging_threads()

def verify_pypi_url():
    """
    Check if URL can be accessed
    """
    try:
        http_conn = http.client.HTTPConnection('https://pypi.python.org/pypi')
        http_conn.connect()
        return True
    except http.client.HTTPException:
        return False
