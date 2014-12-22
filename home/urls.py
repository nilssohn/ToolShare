"""
    @authors Grant Gadomski
"""
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings

from home import views
#This is importing the basic html for the homepage before you log in
urlpatterns = patterns('',
    url(r'^index', views.index, name='index'),

    url(r'^answer_questions', views.answer_questions, name='answer_questions'),
    url(r'^(?P<user_id>\d+)/answer_questions$', views.give_password, name='give_password'),

    url(r'^(?P<notification_id>\d+)/remove_tools$', views.remove_tools, name='remove_tools'),
    url(r'^(?P<notification_id>\d+)/(?P<tool_id>\d+)/move_tool$', views.move_tool, name='move_tool'),

    url(r'^welcome', views.welcome, name='welcome'),
    url(r'^(?P<zipcode>\d+)/add_community_shed_address', views.add_community_shed_address, name='add_community_shed_address'),

    url(r'^get_started', views.get_started, name='get_started'),
)
#gets the static file for the url patterns
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()