# coding=utf-8
from __future__ import absolute_import

import traceback
import logging
import os.path
import sys
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)

class MainApp(tk.Tk):
    """
    Main application : initiation point for app

    :param self.parent: Parent of MainApp
    :param self.container: A child frame of MainApp to enclose contents of
    MainApp
    :param theme_style: to set theme of application , tkinter 'clam' theme

    """

    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        self.parent = root
        self.parent.title("PIP Package Manager")
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        theme_style = ttk.Style()
        if 'clam' in theme_style.theme_names():
            theme_style.theme_use('clam')
        self.container = ttk.Frame(self.parent)
        self.container.grid(row=0, column=0, sticky='nsew')
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)
        self.adjust_window(0.45, 0.40)
        self.manage_frames()

    def manage_frames(self):
        """
        Manage multiple frames. Creates dictionary of multiple frames to
        be used for showing user different GUI frames for different ways of
        installation.

        :param frames_tuple: A tuple to store the sub pages class
        :param frames_dict: Dictionary to store created sub pages, used to save
        a reference to sub pages in order to switch between tabs
        """

        from pip_tkinter.install_page import InstallPage
        from pip_tkinter.manage_installed_modules_page import ManageInstalledPage
        from pip_tkinter.welcome_page import WelcomePage

        frames_tuple = (
            WelcomePage,
            ManageInstalledPage,
            InstallPage,
        )

        self.frames_dict = {}
        for F in frames_tuple:
            frame_name = F.__name__
            new_frame = F(self.container, self)
            new_frame.grid(row=0, column=0, sticky='nsew')
            self.frames_dict[frame_name] = new_frame

        self.adjust_window(0.45, 0.40)
        self.show_frame('WelcomePage')

    def show_frame(self, frame_name):
        """
        Method to switch between different frames and set the size of sub
        pages

        :param frame: stores the reference of the frame to be shown on the top
        """

        if frame_name!='WelcomePage':
            self.adjust_window(0.75, 0.8)
        else:
            self.adjust_window(0.45, 0.40)

        frame = self.frames_dict[frame_name]
        frame.tkraise()
        frame.focus_set()

    def adjust_window(self, xratio, yratio):
        """
        Set the window at center position of the screen and adjust it's
        size depending on screen size. Sets the geometry of parent object

        :param screen_width: variable to store the current screen width
        :param screen_height: variable to store the current screen height
        :param self.window_width: stores the window width of tkinter frame
        :param self.window_height: stores the window height of tkinter frame
        :param x: stores the x coordinate of center of screen
        :param y: stores the y coordinate of center of screen
        """

        # Get the screen width and screen height
        screen_width = self.parent.winfo_screenwidth()
        screen_height = self.parent.winfo_screenheight()

        # Calculate the appropriate window width and height
        self.window_width = int(xratio*screen_width)
        self.window_height = int(yratio*screen_height)

        # Determine the position of the window
        x = (screen_width - self.window_width)//2
        y = (screen_height - self.window_height)//2

        self.parent.geometry(
            '{}x{}+{}+{}'.format(
                str(self.window_width),
                str(self.window_height),
                str(x),
                str(y))
        )

    def onExit(self):
        """
        Method to handle the wrap up to be done when exiting the application
        """

        self.parent.destroy()


class MainloopExceptionCatcher:
    """
    Class to catch tkinter mainloop exceptions
    """

    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = self.subst(*args)
            return self.func(*args)
        except KeyboardInterrupt:
            logger.info('Got keyboard interrupt from user. Application terminated')
            sys.exit()
        except:
            logger.exception('Logging an uncaught exception in tkinter mainloop')


def configure_loggers():
    """
    Configure the loggers for the pip_tkinter application

    :param logger: a Python logging object which serves purpose of logging
    errors and important information for sake of recording information
    :param logging_dir: directory in which logging files will be saved
    :param handler1: a Python logging handler with logging level 'INFO'
    :param handler2: a Python logging handler with logging level 'ERROR'
    :param handler3: a Python logging handler with logging level 'DEBUG'
    """

    logger.setLevel(logging.DEBUG)

    #Create a resource directory if not there
    from pip_tkinter.utils import create_resource_directory
    resource_dir = create_resource_directory()

    # creating logger for logging output to console
    handler1 = logging.StreamHandler()
    handler1.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler1.setFormatter(formatter)
    logger.addHandler(handler1)

    # Log to a file
    handler2 = logging.FileHandler(
        os.path.join(resource_dir, 'pip_error.log'),
        'a',
        encoding='utf-8',
        delay='true')
    handler2.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler2.setFormatter(formatter)
    logger.addHandler(handler2)

    # create debug file handler and set level to debug
    handler3 = logging.FileHandler(
        os.path.join(resource_dir, 'pip_all.log'),
        'a',
        encoding='utf-8')
    handler3.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler3.setFormatter(formatter)
    logger.addHandler(handler3)

def main(args=None):
    """
    The main function
    """

    configure_loggers()
    logger.info("Welcome today")
    root = tk.Tk()
    tk.CallWrapper = MainloopExceptionCatcher
    # root.resizable(width='false', height='false')
    main_app = MainApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
