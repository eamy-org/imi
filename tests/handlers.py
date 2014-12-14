#!/usr/bin/env python

import json
import unittest
from unittest.mock import patch
from urllib.request import Request

import imi.handlers

__all__ = ['TestCustomHandler']


class TestCustomHandler(unittest.TestCase):

    def setUp(self):
        self.handler = imi.handlers.CustomHandler()

    def test_noop_open(self):
        data = json.dumps({'a': 'b'}).encode('utf-8')
        req = Request('noop://example?b=c', data=data)
        res = json.loads(self.handler.noop_open(req).read().decode('utf-8'))
        self.assertEqual({'a': 'b', 'b': 'c'}, res)

    @patch('imi.handlers.subprocess.check_output')
    def test_command_open(self, check_output):
        data = json.dumps({'a': 'b'}).encode('utf-8')
        check_output.return_value = json.dumps({'b': 'c'}).encode('utf-8')
        req = Request('command://example', data=data)
        res = json.loads(self.handler.command_open(req).read().decode('utf-8'))
        self.assertEqual({'b': 'c'}, res)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
