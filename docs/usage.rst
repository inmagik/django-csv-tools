=====
Usage
=====

To use Django csv tools in a project, add it to your `INSTALLED_APPS`:

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
