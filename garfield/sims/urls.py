from django.conf.urls import url
from sims import views


app_name = 'sims'
urlpatterns = [
    url(r'^sms/receive/$', views.receive_sms, name="receive_sms"),
    url(r'^sms/send/$', views.send_sms, name="send_sms"),
    url(r'^voice/receive/$', views.receive_call, name="receive_call"),
    url(r'^voice/send/$', views.send_call, name="send_call"),
]
