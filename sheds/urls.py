"""
    @author Grant Gadomski, Laura Silva, Nils Sohn, Nick Mattis
"""
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings

from sheds import views

urlpatterns = patterns('',
    url(r'^(?P<tool_id>\d+)/request_reservation/$', views.request_reservation, name='request_reservation'),
    url(r'^(?P<tool_id>\d+)/tool_reservation/$', views.tool_reservation, name='tool_reservation'),
    url(r'community_shed', views.community_shed, name='community_shed'),
    
    url(r'browse', views.tool_list, name='browse'),

    url(r'private_shed', views.private_shed, name='private_shed'),
    url(r'home_shed', views.home_shed, name='home_shed'),
    url(r'^(?P<shed_id>[^/]+)/(?P<error_for_user>[^/]+)/(?P<error_for_tool>[^/]+)/display_shed/$', views.view_shed, name='view_shed'),
    url(r'^(?P<shed_id>\d+)/edit_shed/$', views.edit_shed, name='edit_shed'),
    url(r'^(?P<shed_id>[^/]+)/(?P<tool_id>[^/]+)/remove_tool/$', views.remove_tool_from_shed, name='remove_tool_from_shed'),
    url(r'^(?P<shed_id>\d+)/(?P<user_id>\d+)/remove_user_from_shed/$', views.remove_user_from_shed, name='remove_user_from_shed'),

    url(r'global_search', views.global_search, name="global_search"),
    
    url(r'create_shed', views.create_privateshed, name='create_privateshed'),
    url(r'shed_creation', views.privateshed_create, name='privateshed_create'),
    url(r'tool_list', views.tool_list, name='tool_list'), #REMOVE
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()