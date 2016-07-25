#coding=utf-8
from __future__ import absolute_import

import unittest
import threading
import random
import tkinter as tk

from pip_tkinter.utils import MultiItemsList

class TestMultiItemsList(unittest.TestCase):
    """
    Test the GUI application and it's different GUI events
    """

    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

        #Create list of headers
        self.headers = ['A', 'B', 'C']
        self.multi_items_list = MultiItemsList(self.root, self.headers)
        self.number_of_elements = 8 + random.randrange(15)

        #Create a result tuple for testing multi_items_list
        results_tuple = []
        for i in range(self.number_of_elements):
            results_tuple.append(('X'+str(i), 'Y'+str(i), 'Z'+str(i)))
        self.multi_items_list.populate_rows(results_tuple)

        #Get Id of all elements in treeview
        self.iid_tuple = self.multi_items_list.scroll_tree.get_children()

    def test_only_single_selection_is_allowed(self):
        check_browse_option = self.multi_items_list.scroll_tree['selectmode']
        self.assertEqual(str(check_browse_option),'browse')

    def test_number_of_elements_in_tree_view(self):
        self.assertEqual(self.number_of_elements, len(self.iid_tuple))

    def test_number_of_headers_in_tree_view(self):
        count_headers = 0
        headers_list = []
        while True:
            try:
                headers_list.append(
                    self.multi_items_list.scroll_tree.heading(
                        column=count_headers,
                        option='text'))
            except tk.TclError:
                break
            count_headers = count_headers + 1
        self.assertTrue(count_headers<=len(self.headers))

    def tearDown(self):
        self.root.destroy()
        del self.root
