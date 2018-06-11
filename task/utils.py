from taskservice.exceptions import MissingRequiredParam, BadRequest
from task.models.user_node import UserNode
from taskservice.utils import userservice


def assert_uid_valid(uid):
    try:
        return userservice.get_user(uid)
    except Exception as e:
        raise BadRequest('Unable to find user with uid {0}. Detail: {1}'.format(uid, e))


def get_user_by_username(username):
    try:
        return userservice.get_user(username=username)
    except Exception as e:
        raise BadRequest(str(e))


def get_user(request):
    cookie = request.META['HTTP_COOKIE']
    uid = cookie.replace(' ', '')
    if 'uid' in uid:
        uid = uid.replace('uid=', '')
    assert_uid_valid(uid)
    return UserNode.get_or_create({'uid': uid})[0]


def process_single_field(request, field, kwargs):
    if field.method is None or field.method == request.method:
        if field.required and field.name not in request.data:
            raise MissingRequiredParam(field.name)
        elif field.name in request.data:
            kwargs[field.name] = request.data[field.name]


def process_fields(apiview, request, kwargs):
    fields = apiview.schema._manual_fields
    for field in fields:
        process_single_field(request, field, kwargs)


def tid_to_task(user, kwargs):
    if 'tid' in kwargs:
        task = user.tasks.get(tid=kwargs['tid'])
        del kwargs['tid']
        kwargs['task'] = task


def preprocess(func):
    def wrapper(apiview, request, *args, **kwargs):
        process_fields(apiview, request, kwargs)
        user = get_user(request)
        tid_to_task(user, kwargs)
        return func(apiview, request, user, *args, **kwargs)
    wrapper.func = func
    return wrapper
