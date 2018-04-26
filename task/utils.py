from taskservice.exceptions import MissingRequiredParam
from task.models.user_node import UserNode


def get_user(request):
    cookie = request.META['HTTP_COOKIE']
    uid = cookie.replace(' ', '')
    if 'uid' in uid:
        uid = uid.replace('uid=', '')
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
