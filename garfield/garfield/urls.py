from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^sms/', include('sms.urls')),
    url(r'^sims/', include('sims.urls')),
]
