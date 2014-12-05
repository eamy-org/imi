#!/usr/bin/env python

import unittest
from unittest.mock import patch, Mock

from imi import index


class TestIndex(unittest.TestCase):

    def setUp(self):
        self.document = {
            'a': 'b',
            'c': ('d', 'e', 'f'),
            'g': ['h', 'i', 'j'],
            'k': {'l': 'm'},
            'n': [{'o': 'p'}, {'q': 'r'}]
        }

    def test_extract_field(self):
        idx = {'a': 1}
        res = index.extract(self.document, idx)
        self.assertEqual('b', res['a'])

    def test_extract_no_field(self):
        idx = {'z': 1}
        res = index.extract(self.document, idx)
        self.assertIsNone(res['z'])

    def test_extract_sub_field(self):
        idx = {'k.l': 1}
        res = index.extract(self.document, idx)
        self.assertEqual('m', res['k.l'])

    def test_extract_sub_field_no_path(self):
        idx = {'k.l.z': 1}
        res = index.extract(self.document, idx)
        self.assertIsNone(res['k.l.z'])

    def test_extract_array(self):
        idx = {'g': 1}
        res = index.extract(self.document, idx)
        self.assertEqual(['h', 'i', 'j'], res['g'])

    def test_extract_array_sub_path(self):
        idx = {'n.o': 1}
        res = index.extract(self.document, idx)
        self.assertIsNone(res['n.o'])

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
