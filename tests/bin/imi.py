#!/usr/bin/env python

import unittest
from unittest.mock import patch, sentinel, call

from imi.bin import imi
from imi.config import WEB_HOST, WEB_PORT

__all__ = ['TestImi']


class TestImi(unittest.TestCase):

    def setUp(self):
        pass

    @patch('imi.bin.imi.PIDFILE', '/test/path/test.pid')
    @patch('imi.bin.imi.ImiDaemon')
    def test_main(self, deamon):
        imi.main()
        expected = call('/test/path/test.pid').start().call_list()
        self.assertEqual(expected, deamon.mock_calls)

    @patch('imi.bin.imi.run')
    @patch('imi.bin.imi.init_app')
    def test_server(self, init_app, run):
        init_app.return_value = sentinel.app
        imi.server()
        init_app.assert_called_once_with()
        run.assert_called_once_with(sentinel.app, host=WEB_HOST, port=WEB_PORT)

    @patch('imi.bin.imi.server')
    def test_daemon(self, server):
        deamon = imi.ImiDaemon('/test/path/test.pid')
        deamon.run()
        server.assert_called_once_with()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
