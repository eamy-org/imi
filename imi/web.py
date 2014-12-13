import logging
from bottle import Bottle, request, response
from pathlib import Path
from .storage import Database
from .context import ContextAgent, ContextError
from .config import DATADIR
from . import handlers

__all__ = ['init_app']

log = logging.getLogger(__name__)


def setup_routing(bottle_app, app):
    bottle_app.route('/invoke', ['POST'], app.invoke)


def init_app():
    handlers.register()
    bottle_app = Bottle(catchall=False)
    app = WebApp()
    setup_routing(bottle_app, app)
    return bottle_app


def ensuredatadir():
    try:
        Path(DATADIR).mkdir()
    except FileExistsError:
        pass


def force_json():
    json_type = 'application/json'
    ctype = request.environ.get('CONTENT_TYPE', '').lower().split(';')[0]
    if ctype != json_type:
        request.environ['CONTENT_TYPE'] = json_type


class WebApp:

    def __init__(self):
        ensuredatadir()
        self.db = Database()
        self.ctx = ContextAgent(self.db.rules(), self.db)

    def invoke(self):
        force_json()
        log.info('Received a message')

        def handle_error(err):
            response.status = 400
            return {'error': str(err)}
        try:
            res = self.ctx.apply_message(request.json)
        except ContextError as err:
            res = handle_error(err)
        except ValueError as err:
            res = handle_error(err)
        return res
