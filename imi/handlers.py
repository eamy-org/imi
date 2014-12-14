import io
import json
import pathlib
import subprocess
from urllib.request import BaseHandler, build_opener, install_opener
from urllib.response import addinfourl
from urllib.parse import urlparse, parse_qs
from .config import DATADIR

__all__ = ['register']


def register():
    opener = build_opener(CustomHandler())
    install_opener(opener)


def modify_from_query(url, data):
    doc = json.loads(data.decode('utf-8'))
    qs = parse_qs(urlparse(url).query)
    for key, val in qs.items():
        if len(val) == 1:
            val = val[0]
        doc[key] = val
    return json.dumps(doc).encode('utf-8')


class CustomHandler(BaseHandler):

    def noop_open(self, req):
        headers = {'Content-Encoding': 'application/json'}
        data = io.BytesIO(modify_from_query(req.full_url, req.data))
        return addinfourl(data, headers, req.full_url, code=200)

    def command_open(self, req):
        headers = {'Content-Encoding': 'application/json'}
        url = req.full_url
        command = urlparse(url).netloc
        command_dir = pathlib.Path(DATADIR).joinpath('bin')
        command_path = command_dir.joinpath(command)
        command_args = [str(command_path), '-']
        out = subprocess.check_output(command_args, input=req.data)
        data = io.BytesIO(out)
        return addinfourl(data, headers, req.full_url, code=200)
