# -*- coding: utf-8 -*-

import os
import sys
from unittest import TestCase

from tests import TEST_DATA_DIR

PYVERSION = ''.join([str(n) for n in sys.version_info[:2]])
REPO_DIR = os.path.join(TEST_DATA_DIR, 'repo')
SLAVE_ROOT_DIR = TEST_DATA_DIR
SOURCE_DIR = os.path.join(TEST_DATA_DIR, '..')
TOXICSLAVE_CMD = os.path.join(SOURCE_DIR, 'toxicslave', 'cmds.py')

toxicslave_conf = os.environ.get('TOXICSLAVE_SETTINGS')
if not toxicslave_conf:
    toxicslave_conf = os.path.join(SLAVE_ROOT_DIR, 'toxicslave.conf')
    os.environ['TOXICSLAVE_SETTINGS'] = toxicslave_conf


class BaseFunctionalTest(TestCase):
    """An AsyncTestCase that a slave process on
    setUpClass and stops it on tearDownClass"""

    @classmethod
    def start_slave(cls):
        start_slave()

    @classmethod
    def stop_slave(cls):
        stop_slave()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.start_slave()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.stop_slave()


def start_slave():
    """Starts an slave server in a new process for tests"""

    toxicslave_conf = os.environ.get('TOXICSLAVE_SETTINGS')
    pidfile = 'toxicslave{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&', 'python',
           TOXICSLAVE_CMD, 'start', SLAVE_ROOT_DIR, '--daemonize',
           '--pidfile', pidfile, '--loglevel', 'debug']

    if toxicslave_conf:
        cmd += ['-c', toxicslave_conf]

    print(' '.join(cmd))
    os.system(' '.join(cmd))


def stop_slave():
    """Stops the test slave"""
    pidfile = 'toxicslave{}.pid'.format(PYVERSION)
    cmd = ['export', 'PYTHONPATH="{}"'.format(SOURCE_DIR), '&&',
           'python', TOXICSLAVE_CMD, 'stop', SLAVE_ROOT_DIR,
           '--pidfile', pidfile, '--kill']

    os.system(' '.join(cmd))
