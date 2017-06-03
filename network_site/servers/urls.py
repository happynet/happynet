from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.server_list, name='list'),
    url(r'(?P<server_pk>\d+)/(?P<router_pk>\d+)/$', views.router_detail, name='router'),
    url(r'(?P<pk>\d+)/$', views.server_detail, name='detail'),
]
