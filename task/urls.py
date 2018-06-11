from django.conf.urls import url
from task.views import (
    TaskListView,
    TaskDetailView,
    TaskGraphView,
    TaskCloneView,
    TaskTriggerView,
    TaskInvitationView,
    TaskChangeInvitationView,
    TaskRespondInvitationView,
    TaskRevokeInvitationView
)

from rest_framework.schemas import get_schema_view
from django.conf import settings

URLS = settings.URLS

schema_view = get_schema_view(title='Taskit Tast API v1', url=URLS['base'])

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^task/$', TaskListView.as_view()),
    url(r'^task/(?P<tid>[0-9a-z]*)/$', TaskDetailView.as_view()),
    url(r'^task/trigger/(?P<tid>[0-9a-z]*)/$', TaskTriggerView.as_view()),
    url(r'^task/graph/(?P<tid>[0-9a-z]*)/$', TaskGraphView.as_view()),
    url(r'^task/clone/(?P<tid>[0-9a-z]*)/$', TaskCloneView.as_view()),
    url(r'^task/invitation/(?P<tid>[0-9a-z]*)/$', TaskInvitationView.as_view()),
    url(r'^task/invitation/revoke/(?P<tid>[0-9a-z]*)/$', TaskRevokeInvitationView.as_view()),
    url(r'^task/invitation/respond/(?P<tid>[0-9a-z]*)/$', TaskRespondInvitationView.as_view()),
    url(r'^task/invitation/change/(?P<tid>[0-9a-z]*)/$', TaskChangeInvitationView.as_view()),
    url(r'^schema/$', schema_view),
]
