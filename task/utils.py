from taskservice.exceptions import MissingRequiredParam
from task.models.user_node import UserNode


def get_user(request):
    uid = request.META['HTTP_COOKIE']
    user = UserNode.get_or_create({'uid': uid})[0]
    return user


def check_required_fields(self, request):
    fields = self.schema._manual_fields
    for field in fields:
        if field.method is None or field.method == request.method:
            if field.required and field.name not in request.data:
                raise MissingRequiredParam(field.name)


def preprocess(func):
    def wrapper(self, request, *args, **kwargs):
        check_required_fields(self, request)
        user = get_user(request)
        return func(self, request, user, *args, **kwargs)
    return wrapper
