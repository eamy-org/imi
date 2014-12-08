#!/usr/bin/env python

import unittest
import imi.web

__all__ = ['TestWeb']


class TestWeb(unittest.TestCase):

    def setUp(self):
        pass

    def test_init_app(self):
        imi.web.init_app()

    def test_index(self):
        name = 'test'
        response = imi.web.index(name)
        self.assertIn(name, response)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
