#!/usr/bin/env python
import shlex
import sys

import unittest
from unittest.mock import patch, call

from imi.bin import imi
from imi.config import WEB_HOST, WEB_PORT

__all__ = ['TestMainServer', 'TestMainMessage']


class TestMainServer(unittest.TestCase):

    def setUp(self):
        self.pidfile = '/test/path/test.pid'
        pidfile_patch = patch('imi.bin.imi.PIDFILE', self.pidfile)
        pidfile_patch.start()
        self.addCleanup(pidfile_patch.stop)
        deamon = patch('imi.bin.imi.ServerDaemon')
        self.addCleanup(deamon.stop)
        self.deamon = deamon.start()

    def test_main_start_daemon(self):
        sys.argv = shlex.split('imi start --detach')
        imi.main()
        expected = call(self.pidfile).start().call_list()
        self.assertEqual(expected, self.deamon.mock_calls)

    def test_main_start(self):
        sys.argv = shlex.split('imi start')
        imi.main()
        expected = call(self.pidfile).run().call_list()
        self.assertEqual(expected, self.deamon.mock_calls)

    def test_main_stop(self):
        sys.argv = shlex.split('imi stop')
        imi.main()
        expected = call(self.pidfile).stop().call_list()
        self.assertEqual(expected, self.deamon.mock_calls)

    def test_main_restart(self):
        sys.argv = shlex.split('imi restart')
        imi.main()
        expected = call(self.pidfile).restart().call_list()
        self.assertEqual(expected, self.deamon.mock_calls)

    def tearDown(self):
        pass


class TestMainMessage(unittest.TestCase):

    def setUp(self):
        pass

    def test_main_send(self):
        sys.argv = shlex.split('imi send')
        imi.main()

    def tearDown(self):
        pass


class TestServerDaemon(unittest.TestCase):

    def setUp(self):
        pass

    @patch('imi.bin.imi.run_bottle')
    @patch('imi.bin.imi.init_app')
    def test_run(self, init_app, run_bottle):
        daemon = imi.ServerDaemon('/test/path/test.pid')
        app = init_app.return_value
        daemon.run()
        run_bottle.assert_called_once_with(app, host=WEB_HOST, port=WEB_PORT)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
