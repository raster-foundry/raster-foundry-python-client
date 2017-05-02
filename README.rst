raster-foundry-python-client
============================

A Python client for `Raster Foundry <https://www.rasterfoundry.com/>`_, a web platform for combining, analyzing, and publishing raster data.

Usage
-----

.. code-block:: python

   from rf.api import API
   refresh_token = '<>'

   api = API(refresh_token=refresh_token)

   # List all projects
   my_projects = api.projects

   one_project = my_projects[0]

   # Get TMS URl without token
   one_project.tms()


Installation
------------

.. code:: bash

   $ pip install rasterfoundry


Testing
-------

The test suite execution process is managed by ``tox``:

.. code:: bash

   $ tox
