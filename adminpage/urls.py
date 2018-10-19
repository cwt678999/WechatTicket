# -*- coding: utf-8 -*-
#

from django.conf.urls import url
from adminpage.views import AdminLogin, AdminLogout, AdminActivityList, AdminActivityDelete, \
AdminActivityCreate, AdminActivityDetail, AdminActivityMenu, AdminImageUpload, AdminActivityCheckin


__author__ = "Epsirom"


urlpatterns = [
    url(r'^login/?$', AdminLogin.as_view()),
    url(r'^logout/?$', AdminLogout.as_view()),
    url(r'^activity/list/?$', AdminActivityList.as_view()),
    url(r'^activity/delete/?$', AdminActivityDelete.as_view()),
    url(r'^activity/create/?$', AdminActivityCreate.as_view()),
    url(r'^activity/detail/?$', AdminActivityDetail.as_view()),
    url(r'^activity/menu/?$', AdminActivityMenu.as_view()),
    url(r'^activity/checkin/?$', AdminActivityCheckin.as_view()),
    url(r'^image/upload/?$', AdminImageUpload.as_view()),
]
