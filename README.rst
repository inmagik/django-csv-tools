=============================
Django csv tools
=============================

.. image:: https://badge.fury.io/py/django-csv-tools.svg
    :target: https://badge.fury.io/py/django-csv-tools

.. image:: https://travis-ci.org/inmagik/django-csv-tools.svg?branch=master
    :target: https://travis-ci.org/inmagik/django-csv-tools

.. image:: https://codecov.io/gh/inmagik/django-csv-tools/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/inmagik/django-csv-tools

Your project description goes here

Documentation
-------------

The full documentation is at https://django-csv-tools.readthedocs.io.

Quickstart
----------

Install Django csv tools::

    pip install django-csv-tools

Add it to your `INSTALLED_APPS`:

.. code-block:: python

    INSTALLED_APPS = (
        ...
        'django_csv_tools.apps.DjangoCsvToolsConfig',
        ...
    )

Add Django csv tools's URL patterns:

.. code-block:: python

    from django_csv_tools import urls as django_csv_tools_urls


    urlpatterns = [
        ...
        url(r'^', include(django_csv_tools_urls)),
        ...
    ]

Features
--------

* TODO

Running Tests
-------------

Does the code actually work?

::

    source <YOURVIRTUALENV>/bin/activate
    (myenv) $ pip install tox
    (myenv) $ tox

Credits
-------

Tools used in rendering this package:

*  Cookiecutter_
*  `cookiecutter-djangopackage`_

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`cookiecutter-djangopackage`: https://github.com/pydanny/cookiecutter-djangopackage
