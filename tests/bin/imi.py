#!/usr/bin/env python
import shlex
import sys
import io
import argparse
from urllib.error import HTTPError

import unittest
from unittest.mock import patch, call, sentinel, Mock

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
        logging = patch('imi.bin.imi.logging.basicConfig')
        self.addCleanup(logging.stop)
        logging.start()

    def test_main_start_daemon(self):
        sys.argv = shlex.split('imi start --detach')
        imi.main()
        expected = call(self.pidfile).start().call_list()
        self.assertEqual(expected, self.deamon.mock_calls)

    @patch('imi.bin.imi.run_server')
    def test_main_start(self, run_server):
        sys.argv = shlex.split('imi start')
        imi.main()
        run_server.assert_called_once_with()

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

    @patch('imi.bin.imi.log')
    def test_main_exception(self, log):
        try:
            raise NotImplementedError
        except NotImplementedError:
            err = sys.exc_info()
            imi.handle_exception(*err)
        msg = 'Unhandled error occurred'
        log.error.assert_called_once_with(msg, exc_info=err)

    def tearDown(self):
        pass


class TestMainMessage(unittest.TestCase):

    def setUp(self):
        parser = patch('imi.bin.imi.argparse.ArgumentParser')
        self.addCleanup(parser.stop)
        self.parser = parser.start()
        args = argparse.Namespace(
            command='send',
            message=io.StringIO('test: val'))
        self.parser.return_value.parse_args.return_value = args

    @patch('imi.bin.imi.invoke')
    def test_main_send(self, invoke):
        invoke.return_value = {'res': 'ok'}
        with patch('sys.stdout', io.StringIO()):
            imi.main()
            out = '{\n  "res": "ok"\n}\n'
            self.assertEqual(out, sys.stdout.getvalue())
        invoke.assert_called_once_with({'test': 'val'})

    @patch('imi.bin.imi.invoke')
    def test_main_send_http_error(self, invoke):
        msg = io.BytesIO(b'{"test": "val"}')
        invoke.side_effect = HTTPError(None, None, None, None, msg)
        with patch('sys.stdout', io.StringIO()):
            try:
                with self.assertRaises(SystemExit):
                    imi.main()
            finally:
                out = '{\n  "test": "val"\n}\n'
                self.assertEqual(out, sys.stdout.getvalue())

    @patch('imi.bin.imi.invoke')
    def test_main_send_http_value_error(self, invoke):
        msg = io.BytesIO(b'not json')
        invoke.side_effect = HTTPError('', 400, 'test', {}, msg)
        with patch('sys.stdout', io.StringIO()):
            try:
                with self.assertRaises(SystemExit):
                    imi.main()
            finally:
                out = '{\n  "error": "HTTP Error 400: test"\n}\n'
                self.assertEqual(out, sys.stdout.getvalue())

    @patch('imi.bin.imi.invoke')
    def test_main_send_error(self, invoke):
        invoke.side_effect = Exception('test error')
        with patch('sys.stdout', io.StringIO()):
            try:
                with self.assertRaises(SystemExit):
                    imi.main()
            finally:
                out = '{\n  "error": "test error"\n}\n'
                self.assertEqual(out, sys.stdout.getvalue())

    @patch('imi.bin.imi.urlopen')
    def test_main_send_invoke(self, urlopen):
        urlopen.return_value = io.BytesIO(b'{"test": "result"}')
        res = imi.invoke({'test': 'message'})
        self.assertEqual({'test': 'result'}, res)

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
        self.assertIs(sys.excepthook, imi.handle_exception)

    def tearDown(self):
        pass


class TestLogWritter(unittest.TestCase):

    def setUp(self):
        pass

    def test__init__(self):
        writer = imi.LogWritter(sentinel.log, sentinel.level)
        self.assertEqual(sentinel.log, writer.log)
        self.assertEqual(sentinel.level, writer.level)

    def test_write(self):
        log = Mock()
        exp = Mock()
        writer = imi.LogWritter(log, sentinel.level)
        writer.write('Hello')
        writer.write('Hello\n\n')
        writer.write('\n\n')
        writer.write(None)
        exp.log(sentinel.level, 'Hello')
        exp.log(sentinel.level, 'Hello')
        exp.log(sentinel.level, 'None')
        self.assertEqual(exp.mock_calls, log.mock_calls)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
