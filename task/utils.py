from taskservice.exceptions import MissingRequiredParam
from task.models.user_node import UserNode


def get_user(request):
    uid = request.META['HTTP_COOKIE']
    user = UserNode.get_or_create({'uid': uid})[0]
    return user


def process_fields(self, request, kwargs):
    fields = self.schema._manual_fields
    for field in fields:
        if field.method is None or field.method == request.method:
            if field.required and field.name not in request.data:
                raise MissingRequiredParam(field.name)
            elif field.name in request.data:
                kwargs[field.name] = request.data[field.name]


def tid_to_task(user, request, kwargs):
    if 'tid' in kwargs:
        task = user.tasks.get(tid=kwargs['tid'])
        del kwargs['tid']
        kwargs['task'] = task


def preprocess(func):
    def wrapper(self, request, *args, **kwargs):
        process_fields(self, request, kwargs)
        user = get_user(request)
        tid_to_task(user, request, kwargs)
        return func(self, request, user, *args, **kwargs)
    return wrapper
