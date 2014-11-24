#!/usr/bin/env python

import re
import unittest

from imi.query import match


class TestQuery(unittest.TestCase):

    def setUp(self):
        self.document = {
            'a': 'b',
            'c': ('d', 'e', 'f'),
            'g': ['h', 'i', 'j'],
            'k': {'l': 'm'},
            'n': [{'o': 'p'}, {'q': 'r'}]
        }

    def test_match_one_field(self):
        trueQuery = {'a': 'b'}
        falseQuery = {'a': 'a'}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_none_field(self):
        trueQuery = {'z': None}
        falseQuery = {'a': None}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_in_list(self):
        trueQuery = {'g': 'i'}
        falseQuery = {'g': 'g'}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_in_tuple(self):
        trueQuery = {'c': 'e'}
        falseQuery = {'c': 'c'}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_to_none(self):
        query = None
        self.assertTrue(match(self.document, query))

    def test_match_to_empty(self):
        query = {}
        self.assertTrue(match(self.document, query))

    def test_match_to_sub_doc(self):
        trueQuery = {'k': {'l': 'm'}}
        falseQuery = {'k': {'l': 'l'}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_not_op(self):
        trueQuery = {'a': {'$not': 'a'}}
        falseQuery = {'a': {'$not': 'b'}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_to_regex(self):
        trueQuery = {'a': re.compile('^[a-z]')}
        falseQuery = {'a': re.compile('[A-Z]')}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_subkey(self):
        trueQuery = {'k.l': 'm'}
        falseQuery1 = {'k.l': 'l'}
        falseQuery2 = {'k.k': 'k'}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery1))
        self.assertFalse(match(self.document, falseQuery2))

    def test_match_subkey_for_list(self):
        trueQuery = {'n.o': 'p'}
        falseQuery = {'n.o': 'o'}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_int_subkey_for_list(self):
        trueQuery1 = {'n.1.q': 'r'}
        trueQuery2 = {'n.1': {'q': 'r'}}
        falseQuery1 = {'n.1.q': 'q'}
        falseQuery2 = {'n.2.q': 'r'}
        self.assertTrue(match(self.document, trueQuery1))
        self.assertTrue(match(self.document, trueQuery2))
        self.assertFalse(match(self.document, falseQuery1))
        self.assertFalse(match(self.document, falseQuery2))

    def test_match_op_ne(self):
        trueQuery = {'a': {'$ne': 'a'}}
        falseQuery = {'a': {'$ne': 'b'}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_gt(self):
        trueQuery = {'a': {'$gt': 'a'}}
        falseQuery = {'a': {'$gt': 'c'}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_gte(self):
        trueQuery1 = {'a': {'$gte': 'a'}}
        trueQuery2 = {'a': {'$gte': 'b'}}
        falseQuery = {'a': {'$gte': 'c'}}
        self.assertTrue(match(self.document, trueQuery1))
        self.assertTrue(match(self.document, trueQuery2))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_lt(self):
        trueQuery = {'a': {'$lt': 'c'}}
        falseQuery = {'a': {'$lt': 'a'}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_lte(self):
        trueQuery1 = {'a': {'$lte': 'c'}}
        trueQuery2 = {'a': {'$lte': 'b'}}
        falseQuery = {'a': {'$lte': 'a'}}
        self.assertTrue(match(self.document, trueQuery1))
        self.assertTrue(match(self.document, trueQuery2))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_all(self):
        trueQuery1 = {'n': {'$all': [{'o': 'p'}, {'q': 'r'}]}}
        trueQuery2 = {'n': {'$all': [{'o': 'p'}]}}
        falseQuery = {'n': {'$all': [{'o': 'o'}]}}
        self.assertTrue(match(self.document, trueQuery1))
        self.assertTrue(match(self.document, trueQuery2))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_in(self):
        trueQuery = {'a': {'$in': ['a', 'b']}}
        falseQuery = {'a': {'$in': ['a', 'c']}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_nin(self):
        trueQuery = {'a': {'$nin': ['a', 'c']}}
        falseQuery = {'a': {'$nin': ['a', 'b']}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_exists(self):
        trueQuery1 = {'n.o': {'$exists': True}}
        trueQuery2 = {'n.n': {'$exists': False}}
        falseQuery = {'a': {'$exists': False}}
        self.assertTrue(match(self.document, trueQuery1))
        self.assertTrue(match(self.document, trueQuery2))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_regex(self):
        trueQuery = {'a': {'$regex': '^[a-z]$'}}
        falseQuery = {'a': {'$regex': 'a'}}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_elemMatch(self):
        trueQuery1 = {'n': {'$elemMatch': {}}}
        trueQuery2 = {'n': {'$elemMatch': {'o': 'p'}}}
        trueQuery3 = {'n': {'$elemMatch': {'o': {'$lt': 'q'}}}}
        falseQuery1 = {'n': {'$elemMatch': {'o': 'o'}}}
        falseQuery2 = {'a': {'$elemMatch': {}}}
        self.assertTrue(match(self.document, trueQuery1))
        self.assertTrue(match(self.document, trueQuery2))
        self.assertTrue(match(self.document, trueQuery3))
        self.assertFalse(match(self.document, falseQuery1))
        self.assertFalse(match(self.document, falseQuery2))

    def test_match_op_or(self):
        trueQuery1 = {'$or': [{'a': 'a'}, {'c': 'd'}]}
        trueQuery2 = {'$or': [{'a': 'b'}, {'c': 'c'}]}
        falseQuery = {'$or': [{'a': 'a'}, {'c': 'c'}]}
        self.assertTrue(match(self.document, trueQuery1))
        self.assertTrue(match(self.document, trueQuery2))
        self.assertFalse(match(self.document, falseQuery))

    def test_match_op_and(self):
        trueQuery = {'$and': [{'a': 'b'}, {'c': 'd'}]}
        falseQuery = {'$and': [{'a': 'b'}, {'c': 'c'}]}
        self.assertTrue(match(self.document, trueQuery))
        self.assertFalse(match(self.document, falseQuery))

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
