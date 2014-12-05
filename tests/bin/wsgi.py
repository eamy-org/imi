#!/usr/bin/env python

import unittest
from unittest.mock import patch, sentinel, Mock

__all__ = ['TestWsgi']


class TestWsgi(unittest.TestCase):

    def setUp(self):
        pass

    def test_app(self):
        mock = Mock()
        with patch.dict('sys.modules', {'imi.web': mock}):
            mock.init_app.return_value = sentinel.app
            from imi.bin.wsgi import app
        mock.init_app.assert_called_once_with()
        self.assertEqual(sentinel.app, app)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
