#coding=utf-8
from __future__ import absolute_import

import unittest
import threading
import random

from pip_tkinter.utils import MultiItemsList

class TestMultiItemsList(unittest.TestCase):
    """
    Test the GUI application and it's different GUI events
    """

    def setUp(self):
        self.root = tk.Tk()
        self.headers = ['A', 'B', 'C']
        self.multi_items_list = MultiItemsList(self.root, self.headers)
        self.number_of_elements = 8 + random.randrange(15)

        results_tuple = []
        for i in range(self.number_of_elements):
            results_tuple.append(('X'+str(i), 'Y'+str(i), 'Z'+str(i)))
        self.multi_items_list.populate_rows(results_tuple)

    def test_if_only_single_selection_is_allowed(self):
        pass

    def check_number_of_elements_in_tree_view(self):
        pass

    def check_number_of_headers_in_tree_view(self):
        pass

    def test_vertical_scrollbar(self):
        pass

    def test_horizontal_scrollbar(self):
        pass

    def tearDown(self):
        self.root.destroy()
        del self.root
