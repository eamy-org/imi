#!/usr/bin/env python

import json
import unittest
from urllib.request import Request

import imi.handlers

__all__ = ['TestNoOpHandler']


class TestNoOpHandler(unittest.TestCase):

    def setUp(self):
        self.handler = imi.handlers.NoOpHandler()

    def test_noop_open(self):
        data = json.dumps({'a': 'b'}).encode('utf-8')
        req = Request('noop://example?b=c', data=data)
        res = json.loads(self.handler.noop_open(req).read().decode('utf-8'))
        self.assertEqual({'a': 'b', 'b': 'c'}, res)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
