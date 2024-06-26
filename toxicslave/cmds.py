# -*- coding: utf-8 -*-
# Copyright 2023 Juca Crispim <juca@poraodojuca.net>

# This file is part of toxicbuild.

# toxicbuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# toxicbuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with toxicbuild. If not, see <http://www.gnu.org/licenses/>.

# pylint: disable-all

import os
import pkg_resources
from secrets import token_urlsafe
import shutil
import sys
from time import sleep

from toxiccore.cmd import command, main
from toxiccore.utils import (daemonize as daemon, bcrypt_string,
                             changedir, set_loglevel)

from toxicslave import create_settings

PIDFILE = 'toxicslave.pid'
LOGFILE = 'toxicslave.log'


@command
def start(workdir, daemonize=False, stdout=LOGFILE,
          stderr=LOGFILE, conffile=None, loglevel='info',
          pidfile=PIDFILE):
    """Starts toxicslave.

    Starts the build server to listen on the specified port for
    requests from addr (0.0.0.0 means everyone). Addr and port params
    came from the config file

    :param workdir: Work directory for server.
    :param --daemonize: Run as daemon. Defaults to False
    :param --stdout: stdout path. Defaults to /dev/null
    :param --stderr: stderr path. Defaults to /dev/null
    :param -c, --conffile: path to config file. Defaults to None.
      If not conffile, will look for a file called ``toxicslave.conf``
      inside ``workdir``
    :param --loglevel: Level for logging messages. Defaults to `info`.
    :param --pidfile: Name of the file to use as pidfile.  Defaults to
      ``toxicslave.pid``
    """

    print('Starting toxicslave')
    if not os.path.exists(workdir):
        print('Workdir `{}` does not exist'.format(workdir))
        sys.exit(1)

    if conffile:
        os.environ['TOXICSLAVE_SETTINGS'] = conffile
    else:
        os.environ['TOXICSLAVE_SETTINGS'] = os.path.join(workdir,
                                                         'toxicslave.conf')

    create_settings()

    from toxicslave import settings

    addr = settings.ADDR
    port = settings.PORT
    try:
        use_ssl = settings.USE_SSL
    except AttributeError:
        use_ssl = False

    try:
        certfile = settings.CERTFILE
    except AttributeError:
        certfile = None

    try:
        keyfile = settings.KEYFILE
    except AttributeError:
        keyfile = None

    if daemonize:
        daemon(call=slave_init, cargs=(addr, port),
               ckwargs={'use_ssl': use_ssl, 'certfile': certfile,
                        'keyfile': keyfile, 'loglevel': loglevel},
               stdout=stdout, stderr=stderr, workdir=workdir, pidfile=pidfile)
    else:
        with changedir(workdir):
            slave_init(addr, port, use_ssl=use_ssl,
                       certfile=certfile, keyfile=keyfile,
                       loglevel=loglevel)


def _process_exist(pid):
    try:
        os.kill(pid, 0)
        r = True
    except OSError:
        r = False

    return r


@command
def stop(workdir, pidfile=PIDFILE, kill=False):
    """ Stops toxicslave.

    The instance of toxicslave in ``workdir`` will be stopped.

    :param workdir: Workdir for master to be killed.
    :param --pidfile: Name of the file to use as pidfile.  Defaults to
      ``toxicslave.pid``
    :param kill: If true, send signum 9, otherwise, 15.
    """

    print('Stopping toxicslave')
    with changedir(workdir):
        with open(pidfile) as fd:
            pid = int(fd.read())

        sig = 9 if kill else 15

        os.kill(pid, sig)
        if sig != 9:
            print('Waiting for the process shutdown')
            while _process_exist(pid):
                sleep(0.5)

        os.remove(pidfile)


@command
def restart(workdir, pidfile=PIDFILE, loglevel='info'):
    """Restarts toxicslave

    The instance of toxicslave in ``workdir`` will be restarted.

    :param workdir: Workdir for master to be killed.
    :param --pidfile: Name of the file to use as pidfile.  Defaults to
        ``toxicslave.pid``
    :param --loglevel: Level for logging messages.
    """

    stop(workdir, pidfile=pidfile)
    start(workdir, pidfile=pidfile, daemonize=True, loglevel=loglevel)


@command
def create_token(conffile, show_encrypted=False):
    """Creates the access token to the slave.

    :param conffile: The path for the toxicslave.conf
    :param --show-encrypted: Show the encrypted token?
    """
    access_token = token_urlsafe()
    encrypted_token = bcrypt_string(access_token)

    with open(conffile, 'r') as fd:
        content = fd.read()

    content = content.replace('{{ACCESS_TOKEN}}', encrypted_token)
    with open(conffile, 'w') as fd:
        fd.write(content)

    if show_encrypted:
        print('Created encrypted token:{}'.format(encrypted_token))
    print('Created access token:{}'.format(access_token))
    return access_token


@command
def create(root_dir, no_token=False):
    """ Create a new toxicslave environment.

    :param --root_dir: Root directory for toxicslave.
    :param --no-token: Should we create a access token?
    """
    print('Creating environment on `{}` for toxicslave'.format(root_dir))

    # First we create the directory
    os.makedirs(root_dir)

    # after that we copy the config file to the root dir
    template_fname = 'toxicslave.conf.tmpl'
    template_dir = pkg_resources.resource_filename('toxicslave',
                                                   'templates')
    template_file = os.path.join(template_dir, template_fname)
    dest_file = os.path.join(root_dir, 'toxicslave.conf')
    shutil.copyfile(template_file, dest_file)
    if no_token:
        access_token = None
    else:
        access_token = create_token(dest_file)
    print('Done!')
    return access_token


def slave_init(addr, port, use_ssl, certfile, keyfile, loglevel):
    from toxicslave.server import run_server

    set_loglevel(loglevel)
    run_server(addr, port, use_ssl=use_ssl,
               certfile=certfile, keyfile=keyfile)


if __name__ == '__main__':
    main()
