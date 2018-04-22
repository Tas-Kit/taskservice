from django.conf.urls import url
from task.views import TaskListView, TaskDetailView
from rest_framework.schemas import get_schema_view
from taskservice.settings import URLS

schema_view = get_schema_view(title='Taskit API v1', url=URLS['base'])

# The API URLs are now determined automatically by the router.
urlpatterns = [
    url(r'^task/$', TaskListView.as_view()),
    url(r'^task/(?P<tid>[0-9a-z]*)', TaskDetailView.as_view()),
    url(r'^schema/$', schema_view),
]
