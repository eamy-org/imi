#!/usr/bin/env python

import io
from copy import deepcopy

import unittest
from unittest.mock import Mock, patch

from imi.context import (Context, Rule, Node, ContextError,
                         NodeResult, NodeState, ContextAgent)
from imi.index import extract as extract_index

__all__ = ['TestContextAgent']


def create_rules():
    node1 = Node('http://example.com/service1',
                 NodeState.initial, 0,
                 NodeResult({'e': 'f'}, None))
    node2 = Node('http://example.com/service2',
                 NodeState.initial, 0,
                 NodeResult({'g': 'h'}, None))
    node3 = Node('http://example.com/service3',
                 NodeState.initial, 0,
                 NodeResult({'i': 'j'}, None))
    nodes = (node1, node2, node3)
    rule1 = Rule('rule1', {'a': 'b'}, ('c',), nodes)
    rule2 = Rule('rule2', {'z': 'y'}, ('c',), ())
    return (rule1, rule2)


def create_context(rule, msg, node_num):
    nodes = deepcopy(rule.nodes)
    nodes[node_num].state = NodeState.current
    idx = extract_index(msg, rule.index)
    return Context(None, rule.name, idx, nodes)


class TestContextAgent(unittest.TestCase):

    def setUp(self):
        self.database = Mock()
        self.agent = ContextAgent(create_rules(), self.database)
        self.ctx = None

        def find(*args):
            return self.ctx

        def save(data):
            self.ctx = data

        self.database.find_by_idx.side_effect = find
        self.database.save.side_effect = save
        self.msg = {'a': 'b', 'c': 'd'}

        urlopen = patch('imi.context.urlopen')
        self.addCleanup(urlopen.stop)
        urlopen = urlopen.start()

        def make_response(req):
            return io.BytesIO(req.data)
        urlopen.side_effect = make_response

    def test_context_init(self):
        self.agent.apply_message(self.msg)
        rule_node = self.agent.rules[0].nodes[0]
        current = self.ctx.nodes[0]
        self.assertEqual(NodeState.initial, rule_node.state)
        self.assertEqual(NodeState.current, current.state)

    def test_context_next_node(self):
        self.msg['g'] = 'h'
        self.ctx = create_context(self.agent.rules[0], self.msg, 1)
        self.agent.apply_message(self.msg)
        prev_node = self.ctx.nodes[1]
        current = self.ctx.nodes[2]
        self.assertEqual(NodeState.passed, prev_node.state)
        self.assertEqual(NodeState.current, current.state)

    def test_context_last_node(self):
        self.msg['i'] = 'j'
        self.ctx = create_context(self.agent.rules[0], self.msg, 2)
        self.agent.apply_message(self.msg)
        current = self.ctx.nodes[2]
        self.assertEqual(NodeState.passed, current.state)

    def test_context_whole_chain(self):
        self.msg['e'] = 'f'
        self.msg['g'] = 'h'
        self.msg['i'] = 'j'
        self.agent.apply_message(self.msg)
        for node in self.ctx.nodes:
            self.assertEqual(NodeState.passed, node.state)
            self.assertEqual(self.msg, node.result.message)

    def test_context_rule_not_found_error(self):
        self.msg['a'] = 'z'
        try:
            self.agent.apply_message(self.msg)
        except ContextError as err:
            self.assertEqual('Cannot find a rule for the message', str(err))
            return
        self.fail('ContextError not raised')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
