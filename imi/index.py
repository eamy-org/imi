FSEP = '.'

def extract(document, index):
    result = dict(index)
    for key, _ in index.items():
        path = key.split(FSEP)
        val = document
        for node in path:
            if isinstance(val, dict):
                val = val.get(node)
            else:
                val = None
                break
        result[key] = val
    return result
