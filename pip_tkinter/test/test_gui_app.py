#coding=utf-8
from __future__ import absolute_import

import unittest
import threading

from pip_tkinter.__main__ import MainApp


class TestGUIApp(unittest.TestCase):
    """
    Test the GUI application and it's different GUI events
    """

    def setUp(self):
        test_gui_thread = threading.Thread()

    def test_something(self):
        pass

    def tearDown(self):
        pass
