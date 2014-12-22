"""
    @authors Tina Howard, Grant Gadomski, Nick Mattis, Nils Sohn
"""
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings
'''
renders all of the urls for each of the templates
'''
from registration import views

urlpatterns = patterns('',
    url(r'user_registration', views.user_registration, name='user_registration'), #Takes to form to register new user.
    url(r'register_user', views.register_user, name='register_user'),

    url(r'tool_registration', views.tool_registration, name='tool_registration'),
    url(r'register_tool', views.register_tool, name='register_tool'),
    url(r'^(?P<tool_id>\d+)/remove_tool/$', views.remove_tool, name='remove_tool'),

    url(r'my_tools', views.my_tools, name='my_tools'),
    url(r'^(?P<user_id>\d+)/user_profile/$', views.user_profile, name='user_profile'),

    url(r'profile/$', views.profile_editing, name='profile'),
    url(r'edit_prof_info/$', views.edit_profile, name='edit_profile'),
    url(r'^(?P<tool_id>\d+)/tool_editing/$', views.tool_editing, name='tool_editing'),
    url(r'^(?P<tool_id>\d+)/edit_tool/$', views.edit_tool, name='edit_tool'),


    url(r'user_login', views.user_login, name='user_login'),
    url(r'user_logout', views.user_logout, name='user_logout'),

    url(r'^(?P<reservation_id>\d+)/cancel_reservation/$', views.cancel_reservation, name='cancel_reservation'),
    url(r'^(?P<notification_id>\d+)/tool_returned/$', views.tool_returned, name='tool_returned'),
    url(r'^(?P<reservation_id>\d+)/return_tool/$', views.return_tool, name='return_tool'),
    url(r'^(?P<tool_id>\d+)/borrow_tool/$', views.borrow_tool, name='borrow_tool'),
    url(r'^(?P<tool_id>\d+)/change_tool_availability/$', views.change_tool_availability, name='change_tool_availability'),
    url(r'^(?P<tool_id>\d+)/add_address/$', views.add_address, name='add_address'),

    url(r'^(?P<tool_id>\d+)/tool/$', views.display_tool, name='display_tool'),

    url(r'^(?P<notification_id>\d+)/tool_request_accept/$', views.tool_request_accept, name='tool_request_accept'),
    url(r'^(?P<notification_id>\d+)/tool_request_decline/$', views.tool_request_decline, name='tool_request_decline'),

    url(r'^(?P<user_id>\d+)/show_user_messages/$', views.show_user_messages, name='show_user_messages'),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()
