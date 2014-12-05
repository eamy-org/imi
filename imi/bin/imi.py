from bottle import run
from ..web import init_app
from ..config import WEB_HOST, WEB_PORT


def server():
    run(init_app(), host=WEB_HOST, port=WEB_PORT)


def main():
    server()
