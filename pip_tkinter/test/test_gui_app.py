#coding=utf-8
from __future__ import absolute_import

import unittest
import threading
import tkinter as tk

from pip_tkinter.__main__ import MainApp


class TestGUIApp(unittest.TestCase):
    """
    Test the GUI application and it's different GUI events
    """

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.main_app = MainApp(self.root)

        #gui_thread = threading.Thread(target=self.root.mainloop())
        #gui_thread.start()

    def test_A_welcome_page(self):
        pass

    def tearDown(self):
        self.root.destroy()
        del self.root
