#!/usr/bin/env python

import unittest

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
        idx = ('a',)
        res = index.extract(self.document, idx)
        self.assertTrue(('a', 'b') in res)

    def test_extract_no_field(self):
        idx = ('z',)
        res = index.extract(self.document, idx)
        self.assertTrue(('z', None) in res)

    def test_extract_sub_field(self):
        idx = ('k.l',)
        res = index.extract(self.document, idx)
        self.assertTrue(('k.l', 'm') in res)

    def test_extract_sub_field_no_path(self):
        idx = ('k.l.z',)
        res = index.extract(self.document, idx)
        self.assertTrue(('k.l.z', None) in res)

    def test_extract_array(self):
        idx = ('g',)
        with self.assertRaises(TypeError):
            index.extract(self.document, idx)

    def test_extract_dict(self):
        idx = ('k',)
        with self.assertRaises(TypeError):
            index.extract(self.document, idx)

    def test_extract_array_sub_path(self):
        idx = ('n.o',)
        res = index.extract(self.document, idx)
        self.assertTrue(('n.o', None) in res)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
