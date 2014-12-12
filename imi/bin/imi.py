import argparse
from bottle import run as run_bottle
from ..daemon import Daemon
from ..web import init_app
from ..config import WEB_HOST, WEB_PORT, PIDFILE

__all__ = ['main']


class ServerDaemon(Daemon):
    def run(self):
        run_server()


def run_server():
    run_bottle(init_app(), host=WEB_HOST, port=WEB_PORT)


class ServerCli:
    def __init__(self):
        self.daemon = ServerDaemon(PIDFILE)

    def start(self, detach=False):
        if detach:
            self.daemon.start()
        else:
            self.daemon.run()

    def stop(self):
        self.daemon.stop()

    def restart(self):
        self.daemon.restart()


def main():
    server_cmd = ['start', 'stop', 'restart']
    message_cmd = ['send']
    commands = server_cmd + message_cmd
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=commands)
    parser.add_argument('--detach', action='store_true')
    ns = parser.parse_args()
    if ns.command in server_cmd:
        server = ServerCli()
        if ns.command == 'start':
            server.start(ns.detach)
        elif ns.command == 'stop':
            server.stop()
        elif ns.command == 'restart':
            server.restart()
    else:
        pass
