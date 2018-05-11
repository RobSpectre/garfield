from django.conf.urls import url
from deterrence import views


app_name = 'deterrence'
urlpatterns = [
    url(r'^$', views.index, name="index"),
    url(r'detererrence_campaigns/create/$',
        views.deter,
        name="deter"),
    url(r'deterrence_numbers/create/$',
        views.new_deterrence,
        name="new_deterrence"),
    url(r'deterrence_messages/status_callback/$',
        views.deterrence_message_status_callback,
        name="deterrence_message_status_callback"),
]
