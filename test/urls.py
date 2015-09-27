# coding:utf-8

from django.conf.urls import patterns

urlpatterns = patterns(
    'test.views',
    (r'^getpageserverinfos/$', 'getpageserverinfos'),
    (r'^getenvnames/$', 'getenvnames'),
    (r'^getpdnames/$', 'getpdnames'),
    (r'^updateserver/$', 'updateserver')
)
