import operator
import re

"""
Operators copied from MongoDB documentation
http://docs.mongodb.org/manual/reference/operator/query/

Comparison
----------
$gt -  Matches values that are greater than the value specified in the query.
$gte - Matches values that are greater than or equal
       to the value specified in the query.
$in - Matches any of the values that exist in an array specified in the query.
$lt - Matches values that are less than the value specified in the query.
$lte - Matches values that are less than or equal
       to the value specified in the query.
$ne - Matches all values that are not equal
      to the value specified in the query.
$nin - Matches values that do not exist in an array specified to the query.

Logical
-------
$and - Joins query clauses with a logical AND returns all documents
       that match the conditions of both clauses.
$nor - TODO: Joins query clauses with a logical NOR returns
       all documents that fail to match both clauses.
$not - Inverts the effect of a query expression and
       returns documents that do not match the query expression.
$or - Joins query clauses with a logical OR returns all documents
      that match the conditions of either clause.

Element
-------
$exists - Matches documents that have the specified field.
$type - TODO: Selects documents if a field is of the specified type.

Evaluation
----------
$mod - TODO: Performs a modulo operation on the value of a field
       and selects documents with a specified result.
$regex - Selects documents where values match a specified regular expression.
$text - MISSED: Performs text search.
$where - MISSED: Matches documents that satisfy a JavaScript expression.

Geospatial
----------
$geoIntersects - TODO: Selects geometries that intersect with a GeoJSON
                 geometry. The 2dsphere index supports $geoIntersects.
$geoWithin - TODO: Selects geometries within a bounding GeoJSON geometry.
             The 2dsphere and 2d indexes support $geoWithin.
$nearSphere - TODO: Returns geospatial objects in proximity to a point
              on a sphere. Requires a geospatial index. The 2dsphere
              and 2d indexes support $nearSphere.
$near - TODO: Returns geospatial objects in proximity to a point.
        Requires a geospatial index. The 2dsphere and 2d indexes support $near.

Array
-----
$all - Matches arrays that contain all elements specified in the query.
$elemMatch - Selects documents if element in the array field matches
             all the specified $elemMatch condition.
$size - TODO: Selects documents if the array field is a specified size.

"""

__all__ = ['match']

RE_TYPE = type(re.compile(''))
NOTHING = object()


def match(document, query):
    """
    This function implements MongoDB's matching strategy over documents
    in the find() method and other related scenarios (like $elemMatch)
    Inspired by https://github.com/vmalloc/mongomock project
    """
    if query is None:
        return True
    for key, search in query.items():
        for doc_val in iter_key_candidates(document, key):
            if isinstance(search, dict):
                is_match = dict_match(document, key, doc_val, search)
            elif isinstance(search, RE_TYPE):
                is_match = regex(doc_val, search)
            elif key in LOGICAL_OPERATOR_MAP:
                is_match = LOGICAL_OPERATOR_MAP[key](document, search)
            elif isinstance(doc_val, (list, tuple)):
                is_match = (search in doc_val or search == doc_val)
            else:
                is_none = search is None and doc_val is NOTHING
                is_match = doc_val == search or is_none
            if is_match:
                break
        else:
            return False
    return True


def dict_match(document, key, value, search):
    no_ops = not all(op.startswith('$') for op in search.keys())
    if no_ops:
        return value == search
    for op, arg in search.items():
        is_match = False
        handler = OPERATOR_MAP.get(op)
        if handler:
            is_match = handler(value, arg)
        elif op == '$not':
            is_match = not_op(document, key, arg)
        if not is_match:
            return False
    return True


def iter_key_candidates(document, key):
    """
    Get possible subdocuments or lists that are referred to by
    the key in question. Returns the appropriate nested value if
    the key includes dot notation.
    """
    if not key:
        return (document,)
    if isinstance(document, (list, tuple)):
        return iter_key_candidates_sublist(document, key)
    key_parts = key.split('.')
    if len(key_parts) == 1:
        return (document.get(key, NOTHING),)
    sub_key = '.'.join(key_parts[1:])
    sub_doc = document.get(key_parts[0], {})
    return iter_key_candidates(sub_doc, sub_key)


def iter_key_candidates_sublist(document, key):
    """
    :param document: a list to be searched for candidates for our key
    :param key: the string key to be matched
    """
    key_parts = key.split(".")
    sub_key = key_parts.pop(0)
    key_remainder = ".".join(key_parts)
    try:
        sub_key_int = int(sub_key)
    except ValueError:
        sub_key_int = None
    if sub_key_int is None:
        res = []
        for sub_doc in document:
            if isinstance(sub_doc, dict) and sub_key in sub_doc:
                val = iter_key_candidates(sub_doc[sub_key], key_remainder)
                res.append(val)
        return res
    else:
        if sub_key_int >= len(document):
            return ()
        sub_doc = document[sub_key_int]
        if key_remainder:
            return iter_key_candidates(sub_doc, key_remainder)
        return (sub_doc,)


def force_list(val):
    return val if isinstance(val, (list, tuple)) else (val,)


def all_op(document, search):
    document = force_list(document)
    return all(item in document for item in search)


def not_op(document, key, value):
    return not match(document, {key: value})


def not_nothing_and(func):
    "wrap an operator to return False if the first arg is NOTHING"
    return lambda a, b: a is not NOTHING and func(a, b)


def elem_match_op(document, query):
    if not isinstance(document, list):
        return False
    return any(match(item, query) for item in document)


def regex(document, regex):
    return any(regex.search(item) for item in force_list(document))


OPERATOR_MAP = {
    '$ne': operator.ne,
    '$gt': not_nothing_and(operator.gt),
    '$gte': not_nothing_and(operator.ge),
    '$lt': not_nothing_and(operator.lt),
    '$lte': not_nothing_and(operator.le),
    '$all': all_op,
    '$in': lambda dv, sv: any(x in sv for x in force_list(dv)),
    '$nin': lambda dv, sv: all(x not in sv for x in force_list(dv)),
    '$exists': lambda dv, sv: bool(sv) == (dv is not NOTHING),
    '$regex': not_nothing_and(lambda dv, sv: regex(dv, re.compile(sv))),
    '$elemMatch': elem_match_op
}


LOGICAL_OPERATOR_MAP = {
    '$or': lambda d, subq: any(match(d, q) for q in subq),
    '$and': lambda d, subq: all(match(d, q) for q in subq),
}
