from django.conf import settings

from django.conf.urls import url
from django.urls import include
from django.urls import path
from django.contrib import admin

from controlcenter.views import controlcenter

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^admin/dashboard/', controlcenter.urls),
    url(r'^sms/', include('sms.urls')),
    url(r'^sims/', include('sims.urls')),
    url(r'^deterrence/', include('deterrence.urls')),
    url(r'^lookup/', include('lookup.urls')),
    url(r'^bots/', include('bots.urls')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),

        # For django versions before 2.0:
        # url(r'^__debug__/', include(debug_toolbar.urls)),

    ] + urlpatterns
