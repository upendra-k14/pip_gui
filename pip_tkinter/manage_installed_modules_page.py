import tkinter as tk
from tkinter import ttk

class ManageInstalledPage(ttk.Frame):
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

if __name__ == "__main__":

    # If you want to check GUI
    root = tk.Tk()
    # root.resizable(width='false', height='false')
    manage_installed_app = ManageInstalledPage(root)
    root.mainloop()
