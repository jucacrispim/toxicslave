# -*- coding: utf-8 -*-

# pylint: disable-all

from toxiccore.conf import Settings

__version__ = '0.10.0'

ENVVAR = 'TOXICSLAVE_SETTINGS'
DEFAULT_SETTINGS = 'toxicslave.conf'

settings = None


def create_settings():
    global settings

    settings = Settings(ENVVAR, DEFAULT_SETTINGS)
