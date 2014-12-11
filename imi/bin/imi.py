from bottle import run
from ..daemon import Daemon
from ..web import init_app
from ..config import WEB_HOST, WEB_PORT, PIDFILE

__all__ = ['main']


class ImiDaemon(Daemon):
    def run(self):
        server()


def server():
    run(init_app(), host=WEB_HOST, port=WEB_PORT)


def main():
    daemon = ImiDaemon(PIDFILE)
    daemon.start()
