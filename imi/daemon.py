"""Generic linux daemon base class for python 3.x."""

import abc
import sys
import os
import time
import signal
import pathlib
import logging

log = logging.getLogger(__name__)


class Daemon(metaclass=abc.ABCMeta):
    """A generic daemon class.

    Usage: subclass the Daemon class and override the run() method."""

    def __init__(self, pidfile):
        self._pidfile = pathlib.Path(pidfile)

    def start(self):
        """Start the daemon."""

        # Check for a pidfile to see if the daemon already runs
        try:
            with self._pidfile.open('r') as stream:
                pid = int(stream.read().strip())
        except FileNotFoundError:
            pid = None

        if pid:
            message = 'PID file {} already exists. Is daemon already running?'
            log.error(message.format(self._pidfile))
            sys.exit(1)

        # Start the daemon
        self._daemonize()
        self.run()
        self._finalize()

    def stop(self):
        """Stop the daemon."""

        # Get the pid from the pidfile
        try:
            with self._pidfile.open('r') as stream:
                pid = int(stream.read().strip())
        except FileNotFoundError:
            pid = None

        # If pidfile doesn't exists than just return from method
        if not pid:
            message = "PID file {} does not exist. Isn't daemon running?"
            log.info(message.format(self._pidfile))
            return  # not an error in a restart

        # Try killing the daemon process
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except ProcessLookupError:
            pass

    def restart(self):
        """Restart the daemon."""
        self.stop()
        self.start()

    @abc.abstractmethod
    def run(self):
        """You should override this method when you subclass Daemon.

        It will be called after the process has been daemonized by
        start() or restart()."""

    def _daemonize(self):

        # Deamonize class. UNIX double fork mechanism.
        # Do first fork
        try:
            pid = os.fork()
            if pid > 0:  # exit first parent
                sys.exit(0)
        except OSError as err:
            log.error('fork #1 failed: {}'.format(err))
            sys.exit(1)

        # Decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # Do second fork
        try:
            pid = os.fork()
            if pid > 0:  # exit from second parent
                sys.exit(0)
        except OSError as err:
            log.error('fork #2 failed: {}'.format(err))
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        devnull = pathlib.Path(os.devnull)
        si = devnull.open('r')
        so = devnull.open('a+')
        se = devnull.open('a+')

        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # Delete pidfile in SIGTERM
        def handle_term(signum, frame):
            self._finalize()
            sys.exit(0)

        assert signal.signal(signal.SIGTERM, handle_term) == signal.SIG_DFL

        # Write pidfile
        pid = str(os.getpid())
        with self._pidfile.open('w+') as stream:
            print(pid, file=stream)

    def _finalize(self):
        log.info('Finalizing daemon')
        try:
            self._pidfile.unlink()
        except FileNotFoundError:
            pass
