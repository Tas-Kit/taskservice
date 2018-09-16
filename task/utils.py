from taskservice.exceptions import MissingRequiredParam, BadRequest
from task.models.user_node import UserNode
from task.models.task import TaskInst
from task.models.step import StepInst
from taskservice.utils import userservice

from taskservice.constants import ACCEPTANCE


def assert_uid_valid(uid):
    try:
        user = userservice.get_user(uid)
        if not user:
            raise BadRequest('No user with given uid {0} could be found.')
    except Exception as e:
        raise BadRequest('Unable to find user with uid {0}. Detail: {1}'.format(uid, e))


def get_user_by_username(username):
    try:
        return userservice.get_user(username=username)
    except Exception as e:
        raise BadRequest(str(e))


def get_user(request):
    cookies = request._request.META['HTTP_COOKIE']
    cookies = cookies.replace(' ', '').split(';')
    uid = ''
    for cookie in cookies:
        uid = cookie.replace(' ', '')
        if uid.startswith('uid='):
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
        task = TaskInst.nodes.get(tid=kwargs['tid'])
        if task.allow_link_sharing:
            has_task = user.tasks.relationship(task)
            if has_task is None:
                user.tasks.connect(task, {'acceptance': ACCEPTANCE.ACCEPT})
            else:
                has_task.acceptance = ACCEPTANCE.ACCEPT
                has_task.save()
        else:
            task = user.tasks.get(tid=kwargs['tid'])
            has_task = user.tasks.relationship(task)
            has_task.acceptance = ACCEPTANCE.ACCEPT
            has_task.save()
        del kwargs['tid']
        kwargs['task'] = task


def sid_to_step(user, kwargs):
    if 'sid' in kwargs:
        step = StepInst.nodes.get(sid=kwargs['sid'])
        del kwargs['sid']
        kwargs['step'] = step


def preprocess(func):
    def wrapper(apiview, request, *args, **kwargs):
        process_fields(apiview, request, kwargs)
        user = get_user(request)
        tid_to_task(user, kwargs)
        sid_to_step(user, kwargs)
        return func(apiview, request, user, *args, **kwargs)
    wrapper.func = func
    return wrapper
