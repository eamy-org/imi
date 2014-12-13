import sys
import argparse
import logging
import io
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


class LogWritter(io.TextIOBase):

    def __init__(self, log, level):
        self.log = log
        self.level = level

    def write(self, message):
        message = str(message).rstrip()
        if message:
            self.log.log(self.level, message)


def log_config(detached_mode=False):
    # Clear previuos logging configuration
    root = logging.getLogger()
    for handler in root.handlers:
        root.removeHandler(handler)
    fmt = '%(message)s'
    if detached_mode:
        # Log to file
        logging.basicConfig(filename=LOGFILE, level=logging.INFO, format=fmt)
        logging.captureWarnings(True)
        sys.excepthook = handle_exception
        sys.stdout = LogWritter(root, logging.INFO)
        sys.stderr = LogWritter(root, logging.INFO)
    else:
        # Log to stdout
        logging.basicConfig(level=logging.INFO, format=fmt)


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


def handle_exception(type, value, traceback):
    logging.getLogger().error(
        'Unhandled error occurred',
        exc_info=((type, value, traceback)))


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
