from bottle import Bottle

__all__ = ['init_app']


def setup_routing(app):
    app.route('/<name>', ['GET', 'POST'], index)


def init_app():
    app = Bottle()
    setup_routing(app)
    return app


def index(name):
    return '<b>Hello {}</b>!'.format(name)
