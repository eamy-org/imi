#!/usr/bin/env python
import signal

import unittest
from unittest.mock import patch, call, Mock

from imi.daemon import Daemon

__all__ = ['TestDaemon']


class TestDaemonImpl(Daemon):
    def run():
        pass  # Do nothing


class TestDaemon(unittest.TestCase):

    def setUp(self):
        self.pidfile = '/test/path/test.pid'
        pathlib_mock = patch('imi.daemon.pathlib')
        self.addCleanup(pathlib_mock.stop)
        self.pathlib = pathlib_mock.start()
        self.daemon = TestDaemonImpl(self.pidfile)
        log = patch('imi.daemon.log')
        self.addCleanup(log.stop)
        log.start()

    def test_init(self):
        self.pathlib.Path.assert_called_once_with(self.pidfile)

    @patch('imi.daemon.os')
    @patch('imi.daemon.sys')
    def test_daemonize(self, sys, os):
        pid = 12345
        os.fork.side_effect = [0, 0]
        os.getpid.return_value = pid
        write_pid = call.Path('self.pidfile').open('w+').__enter__() \
            .write(str(pid)).call_list()[-1]
        self.daemon._daemonize()
        self.assertEqual(2, os.fork.call_count)
        self.assertIn(write_pid, self.pathlib.mock_calls)
        self.assertFalse(sys.exit.called)

    @patch('imi.daemon.os')
    @patch('imi.daemon.sys')
    def test_daemonize_1st_parent_exit(self, sys, os):
        os.fork.side_effect = [12345, 0]
        sys.exit.side_effect = [SystemExit]
        with self.assertRaises(SystemExit):
            self.daemon._daemonize()
        sys.exit.assert_called_once_with(0)

    @patch('imi.daemon.os')
    @patch('imi.daemon.sys')
    def test_daemonize_2nd_parent_exit(self, sys, os):
        os.fork.side_effect = [0, 12345]
        sys.exit.side_effect = [SystemExit]
        with self.assertRaises(SystemExit):
            self.daemon._daemonize()
        sys.exit.assert_called_once_with(0)

    @patch('imi.daemon.os')
    @patch('imi.daemon.sys')
    def test_daemonize_1st_fork_error(self, sys, os):
        os.fork.side_effect = [OSError, 0]
        sys.exit.side_effect = [SystemExit]
        with self.assertRaises(SystemExit):
            self.daemon._daemonize()
        sys.exit.assert_called_once_with(1)

    @patch('imi.daemon.os')
    @patch('imi.daemon.sys')
    def test_daemonize_2nd_fork_error(self, sys, os):
        os.fork.side_effect = [0, OSError]
        sys.exit.side_effect = [SystemExit]
        with self.assertRaises(SystemExit):
            self.daemon._daemonize()
        sys.exit.assert_called_once_with(1)

    @patch('imi.daemon.os')
    @patch('imi.daemon.sys')
    @patch('imi.daemon.signal')
    def test_sigterm_handler(self, sig, sys, os):
        os.fork.side_effect = [0, 0]
        sig.SIG_DFL = signal.SIG_DFL
        sig.signal.return_value = signal.SIG_DFL
        self.daemon._finalize = Mock()
        self.daemon._daemonize()
        handler = sig.signal.call_args[0][1]
        handler(None, None)
        self.daemon._finalize.assert_called_once_with()

    def test_start(self):
        open_pid = self.pathlib.Path.return_value.open
        open_pid.side_effect = [FileNotFoundError]
        self.daemon._daemonize = Mock()
        self.daemon.run = Mock()
        self.daemon._finalize = Mock()
        self.daemon.start()
        self.daemon._daemonize.assert_called_once_with()
        self.daemon.run.assert_called_once_with()
        self.daemon._finalize.assert_called_once_with()

    def test_finalize(self):
        self.daemon._finalize()
        unlink = self.pathlib.Path.return_value.unlink
        unlink.assert_called_once_with()

    def test_finalize_pidfile_missed(self):
        unlink = self.pathlib.Path.return_value.unlink
        unlink.side_effect = [FileNotFoundError]
        self.daemon._finalize()
        unlink.assert_called_once_with()

    @patch('imi.daemon.sys')
    def test_start_pidfile_exists(self, sys):
        open_pid = self.pathlib.Path.return_value.open
        read_pid = open_pid.return_value.__enter__.return_value.read
        read_pid.return_value = '12345'
        sys.exit.side_effect = [SystemExit]
        with self.assertRaises(SystemExit):
            self.daemon.start()
        sys.exit.assert_called_once_with(1)

    @patch('imi.daemon.time.sleep')
    @patch('imi.daemon.os')
    def test_stop(self, os, sleep):
        pid = 12345
        open_pid = self.pathlib.Path.return_value.open
        read_pid = open_pid.return_value.__enter__.return_value.read
        read_pid.return_value = str(pid)
        os.kill.side_effect = [None, None, ProcessLookupError]
        self.daemon.stop()
        self.assertEqual(2, len(sleep.mock_calls))

    @patch('imi.daemon.sys.stderr')
    def test_stop_pidfile_not_found(self, stderr):
        open_pid = self.pathlib.Path.return_value.open
        open_pid.side_effect = [FileNotFoundError]
        self.daemon.stop()
        # self.assertTrue(stderr.write.called)

    def test_restart(self):
        self.daemon.stop = Mock()
        self.daemon.start = Mock()
        self.daemon.restart()
        self.daemon.stop.assert_called_once_with()
        self.daemon.start.assert_called_once_with()

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
