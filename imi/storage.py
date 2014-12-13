import json
import yaml
import random
import string

from pathlib import Path
from . import config
from .context import Context, Rule, Node, NodeResult, NodeState

__all__ = ['Database', 'DatabaseError']

IDABC = string.ascii_lowercase + string.digits


def load_rule_docs():
    rules_dir = Path(config.DATADIR).joinpath('rules')
    rules = []
    for path in rules_dir.glob('*.y*ml'):
        with path.open(encoding='utf-8') as stream:
            for doc in yaml.load_all(stream.read()):
                doc['name'] = '{}-{}'.format(path.stem, doc['name'])
                rules.append(doc)
    return rules


def load_context_docs():
    contexts = []
    for path in ctx_db_path().glob('*.json'):
        with path.open(encoding='utf-8') as stream:
            ctx = json.load(stream)
            contexts.append(ctx)
    return contexts


def init_rules(rule_docs):
    rules = []
    for doc in rule_docs:
        name = doc['name']
        crit = doc['criteria']
        index = doc['index']
        nodes = []
        for node_doc in doc['nodes']:
            url = node_doc['url']
            exit_crit = node_doc['exit']
            node_result = NodeResult(exit_crit, None)
            node = Node(url, NodeState.initial, 0, node_result)
            nodes.append(node)
        rule = Rule(name, crit, index, nodes)
        rules.append(rule)
    return rules


def init_contexts(context_docs):
    contexts = []
    for doc in context_docs:
        ctxid = doc['id']
        rule_name = doc['rule_name']
        index = frozenset(doc['index'].items())
        nodes = [dict_to_node(node) for node in doc['nodes']]
        contexts.append(Context(ctxid, rule_name, index, nodes))
    return contexts


def context_to_dict(ctx):
    return {
        'id': ctx.id,
        'rule_name': ctx.rule_name,
        'index': dict(ctx.index),
        'nodes': [node_to_dict(node) for node in ctx.nodes]
    }


def node_to_dict(node):
    data = {
        'url': node.url,
        'state': node.state.name,
        'calls_count': node.calls_count,
        'result': {'criteria': node.result.criteria}}
    if node.result.message:
        data['result']['message'] = node.result.message
    return data


def dict_to_node(data):
    url = data['url']
    state = NodeState[data['state']]
    calls_count = data['calls_count']
    result_crit = data['result']['criteria']
    result_msg = data['result'].get('message')
    result = NodeResult(result_crit, result_msg)
    return Node(url, state, calls_count, result)


def is_active_ctx(ctx):
    return any(node.state == NodeState.current for node in ctx.nodes)


def random_id():
    return ''.join(random.choice(IDABC) for _ in range(8))


def get_fname(ctx):
    return 'ctx-{}-{}.json'.format(ctx.rule_name, ctx.id)


def ensure_ctx_dir():
    try:
        Path(config.DATADIR).joinpath('context').mkdir()
    except FileExistsError:
        pass


def ctx_db_path():
    return Path(config.DATADIR).joinpath('context')


def save_new_ctx(ctx):
    tries_count = 0
    ctxpath = ctx_db_path()
    while tries_count < 10:
        ctx = ctx._replace(id=random_id())
        try:
            with ctxpath.joinpath(get_fname(ctx)).open('x') as stream:
                json.dump(context_to_dict(ctx), stream, indent='  ')
        except FileExistsError:
            tries_count += 1
            continue
        return ctx
    raise DatabaseError('Unable to save the context')


def save_ctx(ctx):
    with ctx_db_path().joinpath(get_fname(ctx)).open('w') as stream:
        json.dump(context_to_dict(ctx), stream, indent='  ')


class DatabaseError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class Database:

    def __init__(self):
        ensure_ctx_dir()
        ctxs = load_context_docs()
        ctxs = init_contexts(ctxs)
        self.contexts = ctxs
        self._set_active()

    def find_by_idx(self, rule_name, index):
        candidates = self._get_canditates(rule_name, index)
        return next(iter(candidates), None)

    def save(self, ctx):
        is_new = not ctx.id
        exists = self.find_by_idx(ctx.rule_name, ctx.index)
        if is_new and exists:
            raise DatabaseError('The context already exists')
        if not is_new and not exists:
            raise DatabaseError('Untracked context #{}'.format(ctx.id))
        if is_new:
            ctx = save_new_ctx(ctx)
            self.contexts.append(ctx)
        else:
            save_ctx(ctx)
        self._set_active()
        return ctx

    def rules(self):
        rule_docs = load_rule_docs()
        return init_rules(rule_docs)

    def _set_active(self):
        self.active = []
        for ctx in self.contexts:
            if is_active_ctx(ctx):
                self.active.append(ctx)

    def _get_canditates(self, rule_name, idx):
        for ctx in self.active:
            if rule_name != ctx.rule_name:
                continue
            if idx != ctx.index:
                continue
            yield ctx
