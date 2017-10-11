from django.conf.urls import url
from sms import views


app_name = 'sms'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'^sim_inbound/$', views.sim_inbound, name="sim_inbound"),
    url(r'^sim_outbound/$', views.sim_outbound, name="sim_outbound"),
]
