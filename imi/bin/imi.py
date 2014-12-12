import argparse
import logging
from bottle import run as run_bottle
from ..daemon import Daemon
from ..web import init_app
from ..config import WEB_HOST, WEB_PORT, PIDFILE, LOGFILE

__all__ = ['main']


class ServerDaemon(Daemon):
    def run(self):
        log_config(True)
        run_server()


def run_server():
    run_bottle(init_app(), host=WEB_HOST, port=WEB_PORT)


def log_config(detached_mode=False):

    # Clear previuos logging configuration
    root = logging.getLogger()
    for handler in root.handlers:
        root.removeHandler(handler)
    if detached_mode:  # Log to file
        logging.basicConfig(filename=LOGFILE, level=logging.INFO)
    else:  # Log to stdout
        logging.basicConfig(level=logging.INFO)


class ServerCli:
    def __init__(self):
        self.daemon = ServerDaemon(PIDFILE)

    def start(self, detach):
        if detach:
            self.daemon.start()
        else:
            run_server()

    def stop(self):
        self.daemon.stop()

    def restart(self):
        self.daemon.restart()


def main():
    log_config()
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
