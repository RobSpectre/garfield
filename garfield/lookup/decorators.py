from __future__ import unicode_literals, absolute_import

import sys
from functools import wraps

from django.conf import settings
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseNotAllowed
from django.views.decorators.csrf import csrf_exempt

from twilio.twiml import TwiML
from twilio.request_validator import RequestValidator

import logging

logger = logging.getLogger(__name__)


if sys.version_info[0] == 3:  # pragma: no cover
    text_type = str  # pragma: no cover
else:  # pragma: no cover
    text_type = unicode  # pragma: no cover


def twilio_view(func, **kwargs):
    @csrf_exempt
    @wraps(func)
    def decorator(request, *args, **kwargs):
        use_forgery_protection = getattr(
            settings,
            'DJANGO_TWILIO_FORGERY_PROTECTION',
            not settings.DEBUG,
        )

        if use_forgery_protection:
            test = protect_forged_request(request)

            if isinstance(test, HttpResponseForbidden) or \
               isinstance(test, HttpResponseNotAllowed):

                logger.error("Request did not validate.")

                return test

        response = func(request, *args, **kwargs)

        if isinstance(response, (text_type, bytes)):  # pragma: no cover
            return HttpResponse(response, content_type='application/xml')
        elif isinstance(response, TwiML):
            return HttpResponse(str(response), content_type='application/xml')
        else:
            return response

    return decorator


def protect_forged_request(request):
    if request.method not in ['GET', 'POST']:
        return HttpResponseNotAllowed(request.method)

    try:
        validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
        url = request.build_absolute_uri()
        signature = request.META['HTTP_X_TWILIO_SIGNATURE']
    except (AttributeError, KeyError):
        return HttpResponseForbidden()

    if request.method == 'POST':
        if not validator.validate(url, request.POST, signature):
            return HttpResponseForbidden()
    if request.method == 'GET':
        if not validator.validate(url, request.GET, signature):
            return HttpResponseForbidden()
