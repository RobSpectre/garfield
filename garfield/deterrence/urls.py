from django.conf.urls import url
from deterrence import views


app_name = 'deterrence'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'deter/$', views.deter, name="deter"),
    url(r'new_deterrence/$', views.new_deterrence, name="new_deterrence"),
]
