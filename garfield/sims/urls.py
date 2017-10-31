from django.conf.urls import url
from sims import views


app_name = 'sims'
urlpatterns = [
    url(r'^sms/receive/$', views.sms_receive, name="sms_receive"),
    url(r'^sms/send/$', views.sms_send, name="sms_send"),
    url(r'^voice/receive/$', views.voice_receive, name="voice_receive"),
    url(r'^voice/send/$', views.voice_send, name="voice_send"),
    url(r'^whisper/$', views.whisper, name="whisper"),
    url(r'^voice/recording/$', views.voice_recording, name="recording"),
]
