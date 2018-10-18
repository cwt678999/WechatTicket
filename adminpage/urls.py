# -*- coding: utf-8 -*-
#

from django.conf.urls import url
from adminpage.views import Admin


__author__ = "Epsirom"


urlpatterns = [
    url(r'login', Admin.as_view()),
    url(r'logout', Admin.as_view()),
    url(r'^activity/', Admin.as_view()),
    url(r'image', Admin.as_view()),
]

