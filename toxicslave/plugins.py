# -*- coding: utf-8 -*-

# Copyright 2015-2017, 2019, 2023 Juca Crispim <juca@poraodojuca.net>

# This file is part of toxicbuild.

# toxicbuild is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# toxicbuild is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with toxicbuild. If not, see <http://www.gnu.org/licenses/>.

import os
from toxiccore.plugins import Plugin
from toxiccore.utils import exec_cmd
from . import settings
from .build import BuildStep


class SlavePlugin(Plugin):
    """This is a base slave plugin. Slave plugins may add steps to a build
    before and/or after the used defined steps. It may also set enivronment
    variables to be used in the tests."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._data_dir = None

    # Your plugin must have an unique name
    name = 'BaseSlavePlugin'

    @property
    def data_dir(self):
        """The directory where the plugin store its data."""
        if self._data_dir:
            return self._data_dir

        try:
            data_dir = settings.PLUGINS_DATA_DIR
        except AttributeError:
            data_dir = os.path.join('..', '.')

        self._data_dir = os.path.join(data_dir, self.name)
        return self._data_dir

    @data_dir.setter
    def data_dir(self, data_dir):
        self._data_dir = data_dir

    def get_steps_before(self):
        """Returns a list of steps to be executed before the steps provided
        by the user."""

        return []

    def get_steps_after(self):
        """Returns a list of steps to be executed after the steps provided
        by the user."""

        return []

    def get_env_vars(self):
        """ Returns a dictionary containing values for environment
        variables."""

        return {}


class PythonCreateVenvStep(BuildStep):

    """Step that checks if the venv already exists before
    executing the command."""

    def __init__(self, data_dir, venv_dir, pyversion):
        self.data_dir = data_dir
        self.venv_dir = venv_dir
        self.pyversion = pyversion
        name = 'Create virtualenv'
        command = 'mkdir -p {} && {} -m venv {}'.format(
            self.data_dir, self.pyversion, self.venv_dir)

        super().__init__(name, command, stop_on_fail=True)

    async def execute(self, cwd, **envvars):
        pyexec = os.path.join(self.venv_dir, os.path.join('bin', 'python'))
        if os.path.exists(os.path.join(cwd, pyexec)):
            step_info = {'status': 'success',
                         'output': 'venv exists. Skipping...'}
        else:
            step_info = await super().execute(cwd, **envvars)

        return step_info


class PythonVenvPlugin(SlavePlugin):
    name = 'python-venv'

    def __init__(self, pyversion, requirements_file='requirements.txt',
                 remove_env=False, extra_indexes=None):
        super().__init__()
        self.pyversion = pyversion
        self.requirements_file = requirements_file
        self.remove_env = remove_env
        self.pip_command = 'pip'
        self.extra_indexes = extra_indexes or []

    @property
    def venv_dir(self):
        return os.path.join(
            self.data_dir, 'venv-{}'.format(
                self.pyversion.replace(os.sep, '')))

    def get_steps_before(self):
        create_env = PythonCreateVenvStep(self.data_dir,
                                          self.venv_dir, self.pyversion)

        extra_indexes = ''
        for i in self.extra_indexes:
            extra_indexes += f'--extra-index-url={i} '
        install_deps = BuildStep('install dependencies using pip',
                                 '{} install -r {} {}'.format(
                                     self.pip_command,
                                     self.requirements_file,
                                     extra_indexes),
                                 stop_on_fail=True)

        return [create_env, install_deps]

    def get_steps_after(self):
        steps = []
        if self.remove_env:
            steps.append(BuildStep('remove venv',
                                   'rm -rf {}'.format(self.venv_dir)))
        return steps

    def get_env_vars(self):
        path = f'{self.venv_dir}/bin:PATH'
        return {'PATH': path}


class AptUpdateStep(BuildStep):

    def __init__(self, timeout=600):
        cmd = 'sudo apt-get update'
        name = 'Updating apt packages list'
        super().__init__(name, cmd, stop_on_fail=True, timeout=timeout)


class AptInstallStep(BuildStep):

    def __init__(self, packages, timeout=600):
        self.packages = packages
        packages_str = ' '.join(packages)
        self.install_cmd = ' '.join(['sudo apt-get install -y', packages_str])
        self.reconf_cmd = ' '.join(['sudo dpkg-reconfigure', packages_str])
        self._cmd = None
        name = 'Installing packages with apt-get'
        super().__init__(name, self.install_cmd, stop_on_fail=True,
                         timeout=timeout)

    async def _is_everything_installed(self):
        """Checks if all the packages are installed"""

        cmd = 'sudo dpkg -l | egrep \'{}\' | wc -l'.format('|'.join(
            self.packages))
        installed = int(await exec_cmd(cmd, cwd='.'))
        return installed == len(self.packages)

    async def get_command(self):
        if self._cmd:  # pragma no cover
            return self._cmd

        if not await self._is_everything_installed():
            self._cmd = self.install_cmd
        else:
            self._cmd = self.reconf_cmd

        self.command = self._cmd
        return self._cmd


class AptInstallPlugin(SlavePlugin):

    """Installs packages using apt."""

    name = 'apt-install'

    def __init__(self, packages, timeout=600):
        """Initializes the plugin.
        :param packages: A list of packages names to be installed."""

        super().__init__()
        self.packages = packages

    def get_steps_before(self):
        update = AptUpdateStep()
        install = AptInstallStep(self.packages)
        return [update, install]

    def get_env_vars(self):
        return {'DEBIAN_FRONTEND': 'noninteractive'}
