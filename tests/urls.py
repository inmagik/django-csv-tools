# -*- coding: utf-8
from __future__ import unicode_literals, absolute_import

from django.conf.urls import url, include

from django_csv_tools.urls import urlpatterns as django_csv_tools_urls

urlpatterns = [
    url(r'^', include(django_csv_tools_urls, namespace='django_csv_tools')),
]
