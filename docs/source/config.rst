Toxicslave config
=================

The configuration of toxicslave is done using the a configuration file. The configuration
file can be passed using the  ``-c`` flag to the ``toxicslave`` command
or settings the environment variable ``TOXICSLAVE_SETTINGS``.

This file is a python file, so do what ever you want with it.

Config values
-------------

.. note::

   Although the config is done using a config file, the default
   configuration file created by ``toxicslave create`` can use
   environment variables instead.


* ``PORT`` - The port for the server to listen. Defaults to `7777`.
  Environment variable: ``SLAVE_PORT``

* ``USE_SSL`` - Defaults to False.
  Environment variable: ``SLAVE_USE_SSL``. Possible values are `0` or `1`.

* ``CERTIFILE`` - Path for a certificate file.
  Environment variable: ``SLAVE_CERTIFILE``

* ``KEYFILE`` - Path for a key file.
  Environment variable: ``SLAVE_KEYFILE``


Running builds inside docker containers
---------------------------------------

It is possible to run builds inside docker containers so each time we
run a build it is executed in a new environment. So, lets say you have
the following Dockerfile and you will tag the image as `my-deb-slim`:

.. code-block:: sh

   FROM	debian:buster-slim

   # You MUST to create a user in your image as we don't want to run tests
   # as  root. You may create a user with sudo if you want.
   RUN useradd -ms /bin/bash toxicuser
   USER toxicuser
   WORKDIR /home/toxicuser


Then you must to set the following config values:

* ``USE_DOCKER``- Must be True
  Environment variable: ``USE_DOCKER``. Set its value to `1`

* ``CONTAINER_USER`` - The name of the user you created in your image.
  Environment variable: ``SLAVE_CONTAINER_USER``

* ``DOCKER_IMAGES`` - This value is a json mapping platform names to
  docker image names e.g: `'{"debian-generic": "my-deb-slim"}'`
  Environment variable: ``SLAVE_DOCKER_IMAGES``

The default configuration for the docker images is:

.. code-block:: json

   {
     "linux-generic": "jucacrispim/toxiccontainers:debian-generic",
     "docker": "jucacrispim/toxiccontainers:debian-generic-docker",
     "docker-python3.5": "jucacrispim/toxiccontainers:debian-python3.5-docker",
     "docker-python3.6": "jucacrispim/toxiccontainers:debian-python3.6-docker",
     "docker-python3.7": "jucacrispim/toxiccontainers:debian-python3.7-docker",
     "docker-python3.8": "jucacrispim/toxiccontainers:debian-python3.8-docker",
     "docker-python3.9": "jucacrispim/toxiccontainers:debian-python3.9-docker",
     "docker-python3.10": "jucacrispim/toxiccontainers:debian-python3.10-docker",
     "docker-python3.11": "jucacrispim/toxiccontainers:debian-python3.11-docker",
     "python3.5": "jucacrispim/toxiccontainers:debian-python3.5",
     "python3.6": "jucacrispim/toxiccontainers:debian-python3.6",
     "python3.7": "jucacrispim/toxiccontainers:debian-python3.7",
     "python3.8": "jucacrispim/toxiccontainers:debian-python3.8",
     "python3.9": "jucacrispim/toxiccontainers:debian-python3.9",
     "python3.10": "jucacrispim/toxiccontainers:debian-python3.10",
     "python3.11": "jucacrispim/toxiccontainers:debian-python3.11",
     "go1.14": "jucacrispim/toxiccontainers:debian-go1.14",
     "docker-go1.14": "jucacrispim/toxiccontainers:debian-go1.14-docker",
     "go1.20": "jucacrispim/toxiccontainers:debian-go1.20",
     "docker-go1.20": "jucacrispim/toxiccontainers:debian-go1.20-docker",
   }


And that's it. Your builds will run inside docker containers.

To understand how toxicslave chooses which image to use, how the mapping keys
works and how you can use your own, check:

.. toctree::
   :maxdepth: 1

   build_images
