from django.conf.urls import url
from django.conf.urls import include
from django.contrib import admin

from controlcenter.views import controlcenter

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/dashboard/', controlcenter.urls),
    url(r'^sms/', include('sms.urls')),
    url(r'^sims/', include('sims.urls')),
    url(r'^deterrence/', include('deterrence.urls')),
    url(r'^lookup/',include('lookup.urls'))
]
