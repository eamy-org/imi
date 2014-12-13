#!/usr/bin/env python

import io

import unittest
from unittest.mock import patch, Mock, call

import imi.storage
from imi.context import Context, Node, NodeResult, NodeState


class TestDBFiles(unittest.TestCase):

    def setUp(self):
        pass

    @patch('imi.storage.Path')
    def test_load_rule_docs(self, path):
        file1 = Mock()
        file2 = Mock()
        file1.stem = 'file1'
        file2.stem = 'file2'
        file1.open.return_value = io.StringIO('name: 1')
        file2.open.return_value = io.StringIO('name: 2')
        globs = path.return_value.joinpath.return_value.glob
        globs.return_value = [file1, file2]
        results = imi.storage.load_rule_docs()
        expected = [{'name': 'file1-1'}, {'name': 'file2-2'}]
        self.assertEqual(expected, results)

    @patch('imi.storage.Path')
    def test_load_context_docs(self, path):
        file1 = Mock()
        file2 = Mock()
        file1.open.return_value = io.StringIO('{"name": 1}')
        file2.open.return_value = io.StringIO('{"name": 2}')
        globs = path.return_value.joinpath.return_value.glob
        globs.return_value = [file1, file2]
        results = imi.storage.load_context_docs()
        expected = [{'name': 1}, {'name': 2}]
        self.assertEqual(expected, results)

    @patch('imi.storage.Path')
    @patch('imi.storage.config.DATADIR', 'test')
    def test_ctx_db_path(self, path):
        imi.storage.ctx_db_path()
        expected = call('test').joinpath('contexts').call_list()
        self.assertEqual(expected, path.mock_calls)

    def tearDown(self):
        pass


def new_ctx():
    node_result = NodeResult({'c': 'd'}, {'a': 'z', 'c': 'd'})
    node = Node('http://example.com/1', NodeState.current, 1, node_result)
    return Context(None, 'rule-new', {('a', 'z')}, [node])


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.rules = [
            {
                'name': 'rule1',
                'criteria': {'a': {'$exists': True}},
                'index': ['a'],
                'nodes': [
                    {
                        'url': 'http://example.com/1',
                        'exit': {'c': 'd'}
                    },
                    {
                        'url': 'http://example.com/2',
                        'exit': {'e': 'f'}
                    },
                    {
                        'url': 'http://example.com/3',
                        'exit': {'g': 'h'}
                    }
                ]
            }
        ]

        self.contexts = [
            {
                'id': 'abc',
                'rule_name': 'rule1',
                'index': {'a': 'b'},
                'nodes': [
                    {
                        'url': 'http://example.com/1',
                        'state': 'passed',
                        'calls_count': 1,
                        'result': {
                            'criteria': {'c': 'd'},
                            'message': {'a': 'b', 'c': 'd'}
                        }
                    },
                    {
                        'url': 'http://example.com/2',
                        'state': 'current',
                        'calls_count': 1,
                        'result': {
                            'criteria': {'e': 'f'},
                            'message': {'a': 'b', 'c': 'd'}
                        }
                    },
                    {
                        'url': 'http://example.com/3',
                        'state': 'initial',
                        'calls_count': 0,
                        'result': {
                            'criteria': {'g': 'h'},
                            'message': None
                        }
                    }
                ]
            },
            {
                'id': 'zyx',
                'rule_name': 'rule1',
                'index': {'a': 'z'},
                'nodes': [
                    {
                        'url': 'http://example.com/1',
                        'state': 'passed',
                        'calls_count': 1,
                        'result': {
                            'criteria': {'c': 'd'},
                            'message': {'a': 'z', 'c': 'd'}
                        }
                    }
                ]
            }
        ]

        load_rule_docs = patch('imi.storage.load_rule_docs')
        self.addCleanup(load_rule_docs.stop)
        load_rule_docs = load_rule_docs.start()
        load_rule_docs.return_value = self.rules

        load_context_docs = patch('imi.storage.load_context_docs')
        self.addCleanup(load_context_docs.stop)
        load_context_docs = load_context_docs.start()
        load_context_docs.return_value = self.contexts

        ctx_db_path = patch('imi.storage.ctx_db_path')
        self.addCleanup(ctx_db_path.stop)
        ctx_db_path = ctx_db_path.start()
        self.open_to_save = ctx_db_path.return_value.joinpath.return_value.open

        def dump_ctx(*args, **kwargs):
            ctx_dict = args[0]
            self.contexts.append(ctx_dict)

        dump_json = patch('imi.storage.json.dump')
        self.addCleanup(dump_json.stop)
        dump_json = dump_json.start()
        dump_json.side_effect = dump_ctx

        self.db = imi.storage.Database()

    def test_rules(self):
        rules = self.db.rules()
        self.assertEqual(1, len(rules))
        self.assertEqual('rule1', rules[0].name)
        self.assertEqual(3, len(rules[0].nodes))
        self.assertEqual('http://example.com/3', rules[0].nodes[2].url)

    def test_find_by_idx_found(self):
        idx = {('a', 'b')}
        ctx = self.db.find_by_idx('rule1', idx)
        self.assertIsNotNone(ctx)

    def test_find_by_idx_idx_not_found(self):
        idx = {('a', 'z')}
        ctx = self.db.find_by_idx('rule1', idx)
        self.assertIsNone(ctx)

    def test_find_by_idx_rule_not_found(self):
        idx = {('a', 'b')}
        ctx = self.db.find_by_idx('no_rule', idx)
        self.assertIsNone(ctx)

    def test_save_new(self):
        ctx = new_ctx()
        self.db.save(ctx)
        ctx = self.contexts[-1]
        self.assertRegex(ctx['id'], '[a-z0-9]{8}')
        self.assertEqual('rule-new', ctx['rule_name'])
        self.assertEqual(3, len(self.db.contexts))

    def test_save_new_several_tries(self):
        ctx = new_ctx()
        self.open_to_save.side_effect = [FileExistsError] * 3 + [io.StringIO()]
        self.db.save(ctx)
        ctx = self.contexts[-1]
        self.assertRegex(ctx['id'], '[a-z0-9]{8}')
        self.assertEqual('rule-new', ctx['rule_name'])
        self.assertEqual(3, len(self.db.contexts))
        self.assertEqual(2, len(self.db.active))

    def test_save_new_tries_exceeded(self):
        ctx = new_ctx()
        self.open_to_save.side_effect = [FileExistsError] * 10
        try:
            self.db.save(ctx)
        except imi.storage.DatabaseError as error:
            self.assertEqual("'Unable to save context'", str(error))
            return
        self.fail('DatabaseError not raised')

    def test_save_update(self):
        ctx = self.db.contexts[0]
        nodes = ctx.nodes
        nodes[1].state = NodeState.passed
        nodes[2].state = NodeState.passed
        self.db.save(ctx)
        self.assertEqual(0, len(self.db.active))

    def test_save_new_if_index_exists(self):
        ctx = new_ctx()
        ctx = ctx._replace(index={('a', 'b')})
        ctx = ctx._replace(rule_name='rule1')
        try:
            self.db.save(ctx)
        except imi.storage.DatabaseError as error:
            self.assertEqual("'Context already exists'", str(error))
            return
        self.fail('DatabaseError not raised')

    def test_save_update_missed(self):
        ctx = self.db.contexts[0]
        ctx = ctx._replace(index={('a', 'z')})
        try:
            self.db.save(ctx)
        except imi.storage.DatabaseError as error:
            self.assertEqual("'Untracked context #abc'", str(error))
            return
        self.fail('DatabaseError not raised')

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
