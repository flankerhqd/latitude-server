from django.conf.urls import patterns, include, url

from django.contrib import admin
from latitudeapi import views
from rest_framework.routers import DefaultRouter
admin.autodiscover()
router = DefaultRouter()
router.register(r'location', views.LocationService)
router.register(r'friend', views.FriendService)
router.register(r'register', views.UserService)

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'latitude.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^', include(router.urls)),
    url(r'^locations/friends/', views.get_friends_loc,name='friend-location'),
    url(r'^admin/', include(admin.site.urls)),
    #url(r'^location/$', views.LocationService.as_view(),name='user-location'),
    #url(r'^register/$', views.UserService.as_view(),name='user-register'),
    url(r'^auth/', 'rest_framework.authtoken.views.obtain_auth_token',name="user-login"),
    #(r'^accounts/', include('registration.backends.simple.urls')),
)

urlpatterns += patterns('',
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
)