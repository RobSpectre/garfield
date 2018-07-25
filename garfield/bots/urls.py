from django.conf.urls import url
from bots import views


app_name = 'bots'
urlpatterns = [
    url(r'^sms/$', views.sms, name="sms"),
    url(r'^voice/$', views.voice, name="voice"),
]
