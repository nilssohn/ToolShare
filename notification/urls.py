'''
@Authors Tina Howard, Grant Gadomski
adds in the url for the notification show and delete
'''
from django.conf.urls import patterns, url
from django.conf.urls.static import static
from django.conf import settings

from notification import views

urlpatterns = patterns('',
    url(r'show', views.show_notifications, name='show_notifications'),
    url(r'^delete/(?P<notification_id>\d+)/$', views.delete_notification, name='delete_notification'),
    url(r'^(?P<notification_id>\d+)/mark_as_read/$', views.mark_as_read, name='mark_as_read'),
    url(r'mark_all_as_read', views.mark_all_as_read, name='mark_all_as_read'),
    url(r'^(?P<notification_id>\d+)/rate_user/$', views.rate_user, name='rate_user'),
    url(r'^(?P<notification_id>\d+)/send_rating/$', views.send_rating, name='send_rating'),
)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()