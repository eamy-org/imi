from collections import namedtuple
from copy import deepcopy
from enum import Enum
from .query import match
from .index import extract as extract_index

__all__ = ['Context', 'Rule', 'Node', 'ContextError',
           'NodeResult', 'NodeState', 'ContextAgent']


class NodeState(Enum):
    initial, current, passed = range(3)

Rule = namedtuple('Rule', ('name', 'criteria', 'index', 'nodes'))
Context = namedtuple('Context', ('id', 'rule_name', 'index', 'nodes'))


class Node:
    def __init__(self, url, state, calls_count, result):
        self._url = url
        self.state = state
        self.calls_count = calls_count
        self._result = result

    @property
    def url(self):
        return self._url

    @property
    def result(self):
        return self._result


class NodeResult:
    def __init__(self, criteria, message):
        self._criteria = criteria
        self.message = message

    @property
    def criteria(self):
        return self._criteria


class ContextError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


def skip_to_current(nodes):
    # Node with state NodeState.current must be present,
    # that is context should be in active state
    def is_current(node):
        return node.state == NodeState.current
    chain = iter(nodes)
    current = next(chain)
    while not is_current(current):
        current = next(chain)
    return current, chain


def invoke_context(message, ctx):
    current, chain = skip_to_current(ctx.nodes)
    current.calls_count += 1
    response = invoke_service(current.url, message)
    current.result.message = response
    return next_step(response, current, chain)


def invoke_service(url, payload):
    return payload


def next_step(response, current, chain):
    go_next = match(response, current.result.criteria)
    if go_next:
        current.state = NodeState.passed
        next_node = next(chain, None)
        if next_node:
            next_node.state = NodeState.current
            return True
    return False


class ContextAgent:

    def __init__(self, rules, database):
        self.rules = rules
        self.database = database

    def apply_message(self, message):
        go_next = True
        while go_next:
            rule, idx = self.find_metadata(message)
            ctx = self.get_context(message, rule, idx)
            go_next = invoke_context(message, ctx)
            self.database.save(ctx)
        try:
            active_node, _ = skip_to_current(ctx.nodes)
        except StopIteration:
            active_node = ctx.nodes[-1]
        return active_node.result.message

    def find_metadata(self, message):
        rule = self.find_rule(message)
        idx = extract_index(message, rule.index)
        return rule, idx

    def find_rule(self, message):
        for rule in self.rules:
            if match(message, rule.criteria):
                return rule
        else:
            raise ContextError('Cannot find rule for message')

    def get_context(self, message, rule, idx):
        ctx = self.database.find_by_idx(rule.name, idx)
        if not ctx:
            ctx = self.init_context(rule, idx)
        return ctx

    def init_context(self, rule, idx):
        nodes = deepcopy(rule.nodes)
        nodes[0].state = NodeState.current
        return Context(None, rule.name, idx, nodes)
