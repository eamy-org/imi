#!/usr/bin/env python

import unittest
from unittest.mock import patch, call, sentinel, MagicMock

import imi.web
import imi.context


__all__ = ['TestWebApp']


class TestWebApp(unittest.TestCase):

    def setUp(self):
        ensuredatadir = patch('imi.web.ensuredatadir')
        ctx = patch('imi.web.ContextAgent')
        db = patch('imi.web.Database')
        self.addCleanup(ensuredatadir.stop)
        self.addCleanup(ctx.stop)
        self.addCleanup(db.stop)
        self.ensuredatadir = ensuredatadir.start()
        self.ctx = ctx.start()
        self.db = db.start()
        self.app = imi.web.WebApp()

    def test__init__(self):
        self.ensuredatadir.assert_called_once_with()
        self.assertEqual(self.app.db, self.db.return_value)
        self.assertEqual(self.app.ctx, self.ctx.return_value)
        ctx_args = self.db.return_value.rules.return_value, self.app.db
        self.ctx.assert_called_once_with(*ctx_args)

    @patch('imi.web.request')
    def test_invoke(self, request):
        self.app.ctx.apply_message.return_value = sentinel.msg
        response = app.invoke()
        self.assertEqual(sentinel.msg, response)
        self.app.ctx.apply_message.assert_called_once_with(request.json)

    @patch('imi.web.request', MagicMock())
    def test_invoke(self):
        err = imi.context.ContextError('test error')
        self.app.ctx.apply_message.side_effect = [err]
        response = self.app.invoke()
        self.assertEqual("'test error'", response['error'])

    def tearDown(self):
        pass


class TestHelpers(unittest.TestCase):

    @patch('imi.web.Path')
    def test_ensuredatadir(self, path):
        imi.web.ensuredatadir()
        path.return_value.mkdir.assert_called_once_with()

    @patch('imi.web.Path')
    def test_ensuredatadir_exists(self, path):
        path.return_value.mkdir.side_effect = FileExistsError
        imi.web.ensuredatadir()
        path.return_value.mkdir.assert_called_once_with()

    @patch('imi.web.Bottle')
    @patch('imi.web.WebApp')
    def test_init_app(self, app, bott):
        imi.web.init_app()
        args = ('/invoke', ['POST'], app.return_value.invoke)
        bott.return_value.route.assert_called_once_with(*args)


if __name__ == '__main__':
    unittest.main()
