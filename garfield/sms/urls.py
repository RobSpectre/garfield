from django.conf.urls import url
from sms import views


app_name = 'sms'
urlpatterns = [
    url(r'^$', views.index, name="index"),
]
