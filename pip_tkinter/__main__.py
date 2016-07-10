# coding=utf-8
from __future__ import absolute_import

import traceback
import logging
import os.path
import tkinter as tk
from tkinter import ttk

logger = logging.getLogger(__name__)

class MainApp(tk.Tk):
    """
    Main application
    """

    def __init__(self, root):
        ttk.Frame.__init__(self, root)
        self.parent = root
        self.parent.report_call
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
        size depending on screen size
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
        self.parent.destroy()


class MainloopExceptionCatcher:

    def __init__(self, func, subst, widget):
        self.func = func
        self.subst = subst
        self.widget = widget

    def __call__(self, *args):
        try:
            if self.subst:
                args = apply(self.subst, args)
            return apply(self.func, args)
        except SystemExit, msg:
            raise SystemExit, msg
        except:
            logger.exception('Logging an uncaught exception in tkinter mainloop')


def configure_loggers(logging_dir):
    """
    Configure the loggers for the pip_tkinter application
    """

    logger.setLevel(logging.DEBUG)

    # creating logger for logging output to console
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Log to a file
    handler = logging.FileHandler(
        os.path.join(output_dir, 'pip_error.log'),
        'a',
        encoding='utf-8',
        delay='true')
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(
        os.path.join(output_dir, 'pip_all.log'),
        'a',
        encoding='utf-8')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)


if __name__ == "__main__":

    configure_loggers()
    tk.CallWrapper = MainloopExceptionCatcher
    root = tk.Tk()
    # root.resizable(width='false', height='false')
    main_app = MainApp(root)
    root.mainloop()
