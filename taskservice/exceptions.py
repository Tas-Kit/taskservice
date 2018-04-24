from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler
from neomodel.exceptions import NeomodelException
from django.http import Http404
from django.core.exceptions import PermissionDenied
from settings import logger


# def assert_required_params(params, data):
#     for param in params:
#         if param not in data:
#             exc = MissingRequiredParam()
#             exc.default_detail = exc.default_detail.format(param)
#             raise exc


def handle_exception(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    if isinstance(exc, NeomodelException):
        exc = APIException(str(exc))
        exc.status_code = 404
    # elif not (isinstance(exc, APIException) or
    #           isinstance(exc, Http404) or
    #           isinstance(exc, PermissionDenied)):
    #     logger.error('Unhandled Exception: {0}'.format(str(exc)))
    #     exc = APIException('Internal Server Error: '.format(str(exc), code=500))
    response = exception_handler(exc, {})

    # Now add the HTTP status code to the response.
    if response is not None:
        response.data['status_code'] = response.status_code

    return response


class OwnerCannotChangeInvitation(APIException):
    status_code = 400
    default_detail = 'Bad Request. Task owner cannot change the invitation.'
    default_code = 'owner_cannot_reject_task'


class AlreadyHasTheTask(APIException):
    status_code = 400
    default_detail = 'Bad Request. The user already has the task'
    default_code = 'already_has_the_task'


class NoSuchRole(APIException):

    def __init__(self, role):
        self.detail = 'Bad Request. No such role "{0}".'.format(role)
        super(APIException, self).__init__()

    status_code = 400
    default_code = 'no_such_role'


class MissingRequiredParam(APIException):
    status_code = 400
    default_code = 'missing_required_param'

    def __init__(self, name):
        self.detail = 'Bad Request. Missing required parameter "{0}".'.format(name)
        super(APIException, self).__init__()


class NotAccept(APIException):
    status_code = 403
    default_detail = 'Permission Denied. User needs to accept the task before performing this action.'
    default_code = 'not_accept'


class NotAdmin(APIException):
    status_code = 403
    default_detail = 'Permission Denied. You need at least admin super role to perform this action.'
    default_code = 'not_admin'


class NotOwner(APIException):
    status_code = 403
    default_detail = 'Permission Denied. You need at least owner super role to perform this action.'
    default_code = 'not_admin'
