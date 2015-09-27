# coding:utf-8

from django.conf.urls import patterns

urlpatterns = patterns(
    'uat.views',
    (r'^apply/$', 'apply'),
    (r'^getunresolvedapply/$', 'getunresolvedapply'),
    (r'^getresolvedapply/$', 'getresolvedapply'),
    (r'^audit/$', 'audit'),
    (r'^getallservers/$', 'getallservers'),
)
