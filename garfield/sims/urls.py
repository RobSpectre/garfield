from django.conf.urls import url
from sims import views


app_name = 'sims'
urlpatterns = [
    url(r'^inbound/$', views.sim_inbound, name="sim_inbound"),
    url(r'^outbound/$', views.sim_outbound, name="sim_outbound"),
]
