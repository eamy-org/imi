#!/usr/bin/env python

import unittest
from unittest.mock import patch, Mock

from imi.__main__ import main


class TestMain(unittest.TestCase):

    def setUp(self):
        pass

    def test_main(self):
        mock = Mock()
        with patch.dict('sys.modules', {'imi.bin.imi': mock}):
            main()
        mock.main.assert_called_once_with()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
