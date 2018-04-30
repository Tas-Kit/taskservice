from django.conf.urls import url
from task.views import (
    TaskListView,
    TaskDetailView,
    TaskGraphView,
    TaskInvitationView,
    TaskChangeInvitationView
)

from rest_framework.schemas import get_schema_view
from django.conf import settings

URLS = settings.URLS

schema_view = get_schema_view(title='Taskit Tast API v1', url=URLS['base'])

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^task/$', TaskListView.as_view()),
    url(r'^task/(?P<tid>[0-9a-z]*)$', TaskDetailView.as_view()),
    url(r'^task/graph/(?P<tid>[0-9a-z]*)/$', TaskGraphView.as_view()),
    url(r'^task/invitation/(?P<tid>[0-9a-z]*)/$', TaskInvitationView.as_view()),
    url(r'^task/invitation/change/(?P<tid>[0-9a-z]*)/$', TaskChangeInvitationView.as_view()),
    url(r'^schema/$', schema_view),
]
