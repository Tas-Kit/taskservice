from django.conf.urls import url
from task.views import TaskView
# from rest_framework.schemas import get_schema_view

# The API URLs are now determined automatically by the router.
urlpatterns = [
    # url(r'^api/(?P<url>.*)', views.api_redirect, name='api'),
    url(r'^task/(?P<tid>[0-9a-z]*)', TaskView.as_view()),
]
