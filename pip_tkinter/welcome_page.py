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
        self.container = ttk.Frame(self.parent, padding=(1,1))
        self.container.grid(row=0, column=1, sticky='nsew')
        self.container.rowconfigure(1, weight=1)
        #self.container.columnconfigure(1, weight=1)
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

        #Create side frame
        self.side_frame = ttk.Frame(
            self.container,
            borderwidth=3,
            padding=0.5,
            relief='ridge')
        self.side_frame.grid(
            row=0,
            column=0,
            sticky='nsw',
            pady=(1,1),
            padx=(1,1))
        self.side_frame.rowconfigure(0, weight=1)
        self.side_frame.columnconfigure(0, weight=1)

        #Insert image in left side in side frame
        resource_package = __name__
        resource_path = os.path.join('sideimage.gif')
        data = pkg_resources.resource_string(resource_package, resource_path)
        side_image = base64.b64encode(data)
        s1 = tk.PhotoImage('side_image', data=side_image)
        self.side_label = tk.Label(self.side_frame, image='side_image')
        self.side_label.grid(row=0, column=0, sticky='nsew')

        #Create welcome text
        self.welcome_text = tk.StringVar()
        self.welcome_text.set("Welcome to GUI for PIP")
        self.welcome_label = tk.Label(
            self.container,
            textvariable=self.welcome_text,
            font=('Lucida Grande',22),
            justify='center',
            padx=20)
        self.welcome_label.grid(row=0, column=0, columnspan=2, sticky='nswe')

        #Create labelled frame for option
        self.options_frame = tk.LabelFrame(
            self.container,
            text='Do you want to :',
            padx=10,
            pady=10)
        self.options_frame.grid(row=1, column=0, columnspan=2, sticky='nwe', padx=(2,2), pady=(2,2))
        self.options_frame.rowconfigure(0, weight=1)
        self.options_frame.rowconfigure(1, weight=1)

        #Create radio buttons
        self.radio_var = tk.IntVar()
        self.first_button = tk.Radiobutton(
            self.options_frame,
            text='Search and Install Packages',
            variable=self.radio_var,
            value=1,
            justify='left')
        self.first_button.grid(row=0, column=0, pady=(15,5))
        self.second_button = tk.Radiobutton(
            self.options_frame,
            text='Manage Installed Packages (Update/Uninstall)',
            variable=self.radio_var,
            value=2,
            justify='left')
        self.second_button.grid(row=1, column=0, pady=(5,15))

        #Create 'next' navigation button
        self.next_button = ttk.Button(self.container, text='Next')
        self.next_button.grid(row=2, column=1, sticky='e')


if __name__ == "__main__":

    # If you want to check GUI
    root = tk.Tk()
    # root.resizable(width='false', height='false')
    welcome_app = WelcomePage(root)
    root.mainloop()
