'''
	@Grant Gadomski
	urls to connect the different statistics related to the views
'''
from django.conf.urls import patterns, url
from django.conf.urls.static import static

from statistics import views

urlpatterns = patterns('',
    url(r'^user_statistics', views.show_user_statistics, name='user_statistics'),
    url(r'^tool_statistics', views.show_tool_statistics, name='tool_statistics'),
    url(r'^user_ratings', views.show_user_ratings, name='user_ratings'),
)
                        
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()