import io
import json
from urllib.request import BaseHandler, build_opener, install_opener
from urllib.response import addinfourl
from urllib.parse import urlparse, parse_qs

__all__ = ['register']


def register():
    noop = build_opener(NoOpHandler())
    install_opener(noop)


def modify_from_query(url, data):
    doc = json.loads(data.decode('utf-8'))
    qs = parse_qs(urlparse(url).query)
    for key, val in qs.items():
        if len(val) == 1:
            val = val[0]
        doc[key] = val
    return json.dumps(doc).encode('utf-8')


class NoOpHandler(BaseHandler):

    def noop_open(self, req):
        headers = {'Content-Encoding': 'application/json'}
        data = io.BytesIO(modify_from_query(req.full_url, req.data))
        return addinfourl(data, headers, req.full_url, code=200)
