#!/usr/bin/env python

import unittest
from unittest.mock import patch, sentinel

from imi.bin import imi
from imi.config import WEB_HOST, WEB_PORT

__all__ = ['TestImi']


class TestImi(unittest.TestCase):

    def setUp(self):
        pass

    @patch('imi.bin.imi.server')
    def test_main(self, server):
        imi.main()
        server.assert_called_once_with()

    @patch('imi.bin.imi.run')
    @patch('imi.bin.imi.init_app')
    def test_server(self, init_app, run):
        init_app.return_value = sentinel.app
        imi.server()
        init_app.assert_called_once_with()
        run.assert_called_once_with(sentinel.app, host=WEB_HOST, port=WEB_PORT)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
