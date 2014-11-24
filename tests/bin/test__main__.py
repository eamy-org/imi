#!/usr/bin/env python

import unittest

from imi.__main__ import main


class TestImi(unittest.TestCase):

    def setUp(self):
        pass

    def test_main(self):
        main()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
