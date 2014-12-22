"""
@author Grant Gadomski
"""
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings

from messaging import views

urlpatterns = patterns('',
	url(r'view_messages', views.view_messages, name='view_messages'),
	url(r'^(?P<user_id>\d+)/message_user/$', views.message_user, name='message_user'),
	url(r'^(?P<shed_id>\d+)/message_shed/$', views.message_shed, name='message_shed'),
	url(r'^(?P<message_id>\d+)/mark_message_as_viewed/$', views.mark_message_as_viewed, name='mark_message_as_viewed'),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()