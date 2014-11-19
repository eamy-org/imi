#!/usr/bin/env python

import unittest

from imi.bin import imi


class TestImi(unittest.TestCase):

    def setUp(self):
        pass

    def test_main(self):
        imi.main()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
