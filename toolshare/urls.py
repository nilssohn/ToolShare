'''
    @Grant Gadomski, Nick Mattis
'''
from django.conf.urls import patterns, include, url
from django.conf.urls.static import static
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^registration/', include('registration.urls', namespace="registration")),
    url(r'^home/', include('home.urls', namespace="home")),
    url(r'^sheds/', include('sheds.urls', namespace="sheds")),
    url(r'^notification/', include('notification.urls', namespace="notification")),
    url(r'^statistics/', include('statistics.urls', namespace="statistics")),
    url(r'^messaging/', include('messaging.urls', namespace="messaging")),
) 