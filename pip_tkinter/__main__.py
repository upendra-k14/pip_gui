# coding=utf-8
from __future__ import absolute_import

import tkinter as tk
from tkinter import ttk

class MainApp(tk.Tk):
    """
    Main application
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
        print (frame_name)

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

if __name__ == "__main__":

    # If you want to check GUI
    root = tk.Tk()
    # root.resizable(width='false', height='false')
    main_app = MainApp(root)
    root.mainloop()
