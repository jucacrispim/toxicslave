# -*- coding: utf-8 -*-

# Copyright 2017, 2019, 2023 Juca Crispim <juca@poraodojuca.net>

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

from unittest import TestCase
from unittest.mock import patch, Mock, AsyncMock
from toxicslave import docker
from tests import async_test


DOCKER_ENV = """
PYTHON_PIP_VERSION=19.0.3\r
HOME=/home/toxicuser\r
TERM=xterm\r
PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin\r
LANG=C.UTF-8\r
PYTHON_VERSION=3.7.3\r
PWD=/home/toxicuser\r
"""


class DockerContainerBuilderManagerTest(TestCase):

    @patch.object(docker, 'settings', Mock())
    def setUp(self):
        docker.settings.CONTAINER_USER = 'bla'
        docker.settings.DOCKER_IMAGES = {'linux-generic': 'my-image'}
        manager = Mock()
        self.container = docker.DockerContainerBuilder(
            manager, {'name': 'b1', 'steps': []}, 'source', 'linux-generic')

    @patch.object(docker, 'settings', Mock())
    def test_is_dind_docker(self):
        docker.settings.CONTAINER_USER = 'bla'
        docker.settings.DOCKER_IMAGES = {'docker': 'my-image'}
        manager = Mock()
        container = docker.DockerContainerBuilder(
            manager, {'name': 'b1', 'steps': []}, 'source', 'docker')

        self.assertTrue(container._is_dind)

    @patch.object(docker, 'settings', Mock())
    def test_is_dind_not_docker(self):
        docker.settings.CONTAINER_USER = 'bla'
        docker.settings.DOCKER_IMAGES = {'some-plat': 'my-image'}
        manager = Mock()
        container = docker.DockerContainerBuilder(
            manager, {'name': 'b1', 'steps': []}, 'source', 'some-plat')

        self.assertFalse(container._is_dind)

    @patch.object(docker, 'settings', Mock())
    def test_is_dind_startswith_docker(self):
        docker.settings.CONTAINER_USER = 'bla'
        docker.settings.DOCKER_IMAGES = {'dockerkube': 'my-image'}
        manager = Mock()
        container = docker.DockerContainerBuilder(
            manager, {'name': 'b1', 'steps': []}, 'source', 'dockerkube')

        self.assertTrue(container._is_dind)

    @async_test
    async def test_aenter(self):
        self.container.wait_service = AsyncMock()
        self.container.start_container = AsyncMock()
        self.container.kill_container = AsyncMock()
        self.container.rm_container = AsyncMock()
        self.container.rm_from_container = AsyncMock()
        self.container.copy2container = AsyncMock()
        async with self.container:
            self.assertTrue(self.container.start_container.called)

    @async_test
    async def test_aexit(self):
        self.container.wait_service = AsyncMock()
        self.container.start_container = AsyncMock()
        self.container.kill_container = AsyncMock()
        self.container.rm_container = AsyncMock()
        self.container.rm_from_container = AsyncMock()
        self.container.copy2container = AsyncMock()
        async with self.container:
            pass
        self.assertTrue(self.container.kill_container.called)
        self.assertTrue(self.container.rm_container.called)

    @async_test
    async def test_aexit_no_remove(self):
        self.container.wait_service = AsyncMock()
        self.container.start_container = AsyncMock()
        self.container.kill_container = AsyncMock()
        self.container.rm_container = AsyncMock()
        self.container.copy2container = AsyncMock()
        self.container.rm_from_container = AsyncMock()
        self.container.remove_env = False
        async with self.container:
            pass
        self.assertTrue(self.container.kill_container.called)
        self.assertFalse(self.container.rm_container.called)
        self.assertTrue(self.container.rm_from_container.called)

    @patch.object(docker, 'exec_cmd',
                  AsyncMock(side_effect=docker.ExecCmdError))
    @async_test
    async def test_container_exisits_do_not_exist_error(self):
        exists = await self.container.container_exists()
        self.assertFalse(exists)

    @patch.object(docker, 'exec_cmd', AsyncMock(return_value='1'))
    @async_test
    async def test_container_exisits_do_not_exist(self):
        exists = await self.container.container_exists()
        self.assertFalse(exists)

    @patch.object(docker, 'exec_cmd', AsyncMock(return_value='2'))
    @async_test
    async def test_container_exisits(self):
        exists = await self.container.container_exists()
        self.assertTrue(exists)

    @async_test
    async def test_is_running(self):
        self.container.container_exists = AsyncMock(return_value=True)
        r = await self.container.is_running()
        self.assertTrue(r)

    @patch.object(docker, 'exec_cmd', AsyncMock(side_effect=Exception))
    @async_test
    async def test_service_is_up_false(self):
        r = await self.container.service_is_up()
        self.assertIs(r, False)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_service_is_up_true(self):
        r = await self.container.service_is_up()
        self.assertIs(r, True)

    @patch.object(docker.asyncio, 'sleep', AsyncMock())
    @async_test
    async def test_wait_service(self):
        self.container.service_is_up = AsyncMock(
            side_effect=[False, True])
        await self.container.wait_service()
        self.assertTrue(docker.asyncio.sleep.called)

    @patch.object(docker.asyncio, 'sleep', AsyncMock())
    @async_test
    async def test_wait_start(self):
        self.container.is_running = AsyncMock(
            side_effect=[False, True])
        await self.container.wait_start()
        self.assertTrue(docker.asyncio.sleep.called)

    def test_get_dind_opts_not_dind(self):
        self.container._is_dind = False
        opts = self.container._get_dind_opts()
        self.assertFalse(opts.strip())

    def test_get_dind_opts_no_volume(self):
        self.container._is_dind = True
        self.container._dind_volume = False
        self.container.manager.repo_id = 'i'
        opts = self.container._get_dind_opts()
        e = '--privileged '
        self.assertEqual(opts, e)

    def test_get_dind_opts(self):
        self.container._is_dind = True
        self.container.manager.repo_id = 'i'
        opts = self.container._get_dind_opts()
        e = '--privileged --mount source=i-b1-volume,'\
            'destination=/var/lib/docker/'
        self.assertEqual(opts, e)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_start_container_dont_exists(self):
        self.container.wait_start = AsyncMock()
        self.container.container_exists = AsyncMock(return_value=False)
        expected = 'docker run -d -t   --name {} my-image'.format(
            self.container.cname)
        await self.container.start_container()
        called = docker.exec_cmd.call_args[0][0]

        self.assertEqual(expected, called)
        self.assertTrue(self.container.wait_start.called)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_start_container_dont_exists_privileged(self):
        self.container.wait_start = AsyncMock()
        self.container.cname = 'b'
        self.container._is_dind = True
        self.container.manager.repo_id = 'repo_id'
        self.container.container_exists = AsyncMock(return_value=False)
        mount = '--mount source=repo_id-b1-volume,destination=/var/lib/docker/'
        exp = 'docker run -d -t --privileged {} --name {} my-image'.format(
            mount, self.container.cname)
        await self.container.start_container()
        called = docker.exec_cmd.call_args[0][0]

        self.assertEqual(exp, called)
        self.assertTrue(self.container.wait_start.called)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_start_container(self):
        self.container.container_exists = AsyncMock(return_value=True)
        self.container.wait_start = AsyncMock()
        expected = 'docker start {}'.format(self.container.cname)
        await self.container.start_container()
        called = docker.exec_cmd.call_args[0][0]

        self.assertEqual(expected, called)
        self.assertTrue(self.container.wait_start.called)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_kill_container(self):
        expected = 'docker kill {}'.format(self.container.cname)
        await self.container.kill_container()
        called = docker.exec_cmd.call_args[0][0]

        self.assertEqual(expected, called)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_copy2container(self):
        expected = 'docker cp source {}:/home/bla/src'.format(
            self.container.cname)

        src_dir = '/home/bla/src'
        exp_chown = 'docker exec -u root -t {} chown -R bla:bla {}'.format(
            self.container.cname, src_dir)

        await self.container.copy2container()
        called = docker.exec_cmd.call_args_list[0][0][0]
        called_chown = docker.exec_cmd.call_args_list[1][0][0]

        self.assertEqual(expected, called)
        self.assertEqual(exp_chown, called_chown)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_rm_from_container(self):
        src_dir = '/home/bla/src'
        expected_source = 'docker exec -u root {} rm -rf {}'.format(
            self.container.cname, src_dir)

        await self.container.rm_from_container()
        called_source = docker.exec_cmd.call_args_list[0][0][0]

        self.assertEqual(expected_source, called_source)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @async_test
    async def test_rm_container(self):
        expected = 'docker rm -v {}'.format(self.container.cname)
        await self.container.rm_container()
        called = docker.exec_cmd.call_args[0][0]
        self.assertEqual(expected, called)

    @patch.object(docker, 'settings', Mock())
    def test_get_steps(self):
        self.container.conf['steps'] = ['ls', {'name': 'other',
                                               'command': 'cmd2'}]
        self.container.conf['plugins'] = [{'name': 'apt-install',
                                           'packages': []}]
        self.container.plugins = self.container._load_plugins()

        steps = self.container._get_steps()
        self.assertEqual(len(steps), 4)
        self.assertIsInstance(steps[0], docker.BuildStepDocker)
        self.assertEqual(len(self.container.plugins), 1)
        for plugin in self.container.plugins:
            self.assertEqual(plugin.data_dir,
                             self.container.docker_plugin_data_dir)


class BuildStepDockerTest(TestCase):

    @patch.object(docker, 'settings', Mock())
    def setUp(self):
        docker.settings.CONTAINER_USER = 'bla'
        self.step = docker.BuildStepDocker('cmd', 'sh cmd.sh',
                                           container_name='container')

    @patch.object(docker, 'exec_cmd', AsyncMock(return_value=DOCKER_ENV))
    @async_test
    async def test_get_cmd_line_envvars(self):
        expected = 'export VAR=bla'
        envvars = {'VAR': 'bla', 'PATH': 'bla:PATH'}

        r = await self.step._get_cmd_line_envvars(envvars)

        self.assertIn(expected, r)
        self.assertIn('PATH=', r)

    @patch.object(docker, 'exec_cmd', AsyncMock())
    @patch.object(docker.BuildStepDocker, '_get_docker_env',
                  AsyncMock(return_value={}))
    @async_test
    async def test_exec_cmd(self):
        src_dir = '/home/bla/src'
        envvars = await self.step._get_cmd_line_envvars({})
        user_opts = '-u bla'
        exp = "docker exec {} container /bin/bash -c '{} cd {} && ls'".format(
            user_opts, envvars, src_dir)

        await self.step.exec_cmd('ls', src_dir, 10, lambda *a, **kw: None)

        called = docker.exec_cmd.call_args[0][0]

        self.assertEqual(exp, called)

    @patch.object(docker, 'settings', Mock())
    def test_from_buildstep(self):
        step = docker.BuildStep('some step', 'cmd', warning_on_fail=False,
                                timeout=10, stop_on_fail=True)

        docker_step = docker.BuildStepDocker.from_buildstep(step, 'container')

        self.assertEqual(docker_step.command, step.command)

    @patch.object(docker, 'exec_cmd', AsyncMock(return_value=DOCKER_ENV))
    @async_test
    async def test_get_docker_env(self):
        env = await self.step._get_docker_env()

        self.assertTrue(env['PATH'])
        self.assertFalse(env['PATH'].endswith('\r'))
