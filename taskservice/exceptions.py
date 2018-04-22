from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from neomodel.exceptions import NeomodelException
from django.http import Http404
from django.core.exceptions import PermissionDenied
from settings import logger


def handle_exception(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if isinstance(exc, NeomodelException):
        exc = APIException(str(exc))
        exc.status_code = 404
    elif not (isinstance(exc, APIException) or
              isinstance(exc, Http404) or
              isinstance(exc, PermissionDenied)):
        logger.error('Unhandled Exception: {0}'.format(str(exc)))
        exc = APIException('Internal Server Error: '.format(str(exc), code=500))
    response = exception_handler(exc, {})

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response
