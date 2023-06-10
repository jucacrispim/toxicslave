Build API
=========

The build api is very simple. It uses the `tpp <https://docs.poraodojuca.dev/toxiccore/tpp.html>`_
and has two known actions:

- ``healthcheck`` - Get no params an simply informs if the server is running.
- ``build`` - A request for a build from a master

Build params
------------

The following params are mandatory to the ``build`` action:

- ``repo_id`` - The repository id
- ``repo_url`` - The url of the clone/update url for the repository
- ``branch`` - The branch that triggered the build
- ``named_tree`` - Commit/tag that triggered the build.

The following params are optinal:

- ``config_filename`` - The name for the configuration file. Defaults
  to ``toxicbuild.yml``

- ``builders_from`` - The name for a branch to use the builders from the branch
  config. If not present builders from the ``branch`` param will be used.

- ``external`` - A external build is a build requested from a repository that
  is not the original code repository (ie a pull request from a third party repo).
  It must have the following keys:
  * ``url`` - The external repo url to clone the code
  * ``name`` - name to identify external remote repo
  * ``branch`` - Name of the external branch
  * ``into`` - name for the branch in the local repo


When a build request is sent to the slave, the connection is kept open until the build
is ended. While the connection is open, every line of the output will be sent to the
client. When the build is finished, full information of the build will be sent to the
client and the connection will be closed.
