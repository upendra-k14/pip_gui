import tkinter as tk
from tkinter import ttk

class WelcomePage(ttk.Frame):
    """
    Ask user about what to do :
    1. Install
    2. Uninstall or Update
    """

    def __init__(self, root, controller):
        ttk.Frame.__init__(self, root)
        self.parent = root
        self.controller = controller
        self.parent.rowconfigure(0, weight=1)
        self.parent.columnconfigure(0, weight=1)
        self.create_welcome_page()

    def create_welcome_page(self):
        """
        Add content to welcome page and radio buttons for selecting among
        two tasks :

        1. Search and Install Package
        2. Manage already installed packages
        """

        import base64
        import os
        import pkg_resources

        resource_package = __name__
        resource_path = os.path.join('sideimage.gif')
        data = pkg_resources.resource_string(resource_package, resource_path)
        side_image = base64.b64encode(data)
        s1 = tk.PhotoImage('side_image', data=side_image)
        self.side_label = tk.Label(self, image='side_image')
        self.side_label.grid(row=0, column=0, sticky='nsw')

        self.welcome_text = tk.StringVar()
        self.welcome_text.set("Welcome to GUI for PIP")
        self.welcome_label = ttk.Label(self, textvariable=self.welcome_text)
        self.welcome_label.grid(row=0, column=1, sticky='nwe')

        self.options_frame = ttk.LabelFrame(self, text="Do you want to :")
        self.options_frame.grid(row=1, column=1, sticky='nwe')

        self.radio_var = tk.IntVar()
        self.first_button = tk.Radiobutton(
            self.options_frame,
            text="Search and Install Packages",
            variable=self.radio_var,
            value=1)
        self.first_button.grid(row=0, column=0)
        self.second_button = tk.Radiobutton(
            self.options_frame,
            text="Manage Installed Packages (Update/Uninstall)",
            variable=self.radio_var,
            value=2)
        self.second_button.grid(row=1, column=0)


if __name__ == "__main__":

    # If you want to check GUI
    root = tk.Tk()
    # root.resizable(width='false', height='false')
    welcome_app = WelcomePage(root)
    root.mainloop()
