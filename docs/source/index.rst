:tocdepth: 1

Toxicslave: Build server for toxicbuild
=======================================

Toxicslave is a server that excutes builds requested by a
toxicbuild master.

Install
-------

To install it use pip:

.. code-block:: sh

   $ pip install toxicslave


.. note::

   Currently it only works on linux. Other platforms will be supported
   in the future.

.. note::

   Toxicslave uses the ``ps`` command. It must be available in the
   host system. The ``git`` command must also be available.


Setup & config
--------------

Before executing builds you must create an environment for toxicslave.
To do so use:

.. code-block:: sh

   $ toxicslave create ~/build-env

This is going to create a ``~/build-env`` directory with a ``toxicslave.conf``
file in it. This file is used to configure toxicslave.

Check the configuration instructions for details

.. toctree::
   :maxdepth: 1

   config


Run the server
--------------

When the configuration is done you can run the server with:

.. code-block:: sh

   $ toxicslave start ~/build-env


For all options for the toxicslave command execute

.. code-block:: sh

   $ toxicslave --help


Build server API
================

With the server running you can send build requests to it. Check the
api documentation for details

.. toctree::
   :maxdepth: 1

   build_api.rst


CHANGELOG
---------

.. toctree::
   :maxdepth: 1

   CHANGELOG
