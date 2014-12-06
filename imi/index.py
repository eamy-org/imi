FSEP = '.'


def extract(document, index):
    result = dict((key, None) for key in index)
    for key in index:
        path = key.split(FSEP)
        val = document
        for node in path:
            if isinstance(val, dict):
                val = val.get(node)

            # TODO: search in arrays
            else:
                val = None
                break
        result[key] = val
    return frozenset(result.items())
