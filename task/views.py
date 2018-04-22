# -*- coding: utf-8 -*-
"""Views for Main."""
from __future__ import unicode_literals

# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from task.models.user_node import UserNode
import coreschema
from taskservice.schemas import Schema, Field
# from taskservice.exceptions import handle_exception

# Create your views here.


class ServiceView(APIView):

    def get_user(self, request):
        uid = request.META['HTTP_COOKIE']
        user = UserNode.get_or_create({'uid': uid})[0]
        return user


class TaskListView(ServiceView):
    schema = Schema(manual_fields=[
        Field(
            "task_name",
            method='POST',
            required=True,
            location="form",
            schema=coreschema.String()
        ),
    ])

    def get(self, request):
        user = self.get_user(request)
        tasks = user.tasks.all()
        return Response([task.__properties__ for task in tasks])

    def post(self, request):
        user = self.get_user(request)
        task_name = request.data['task_name']
        task = user.create_task(task_name)
        return Response(task.__properties__)


class TaskDetailView(ServiceView):

    def get(self, request, tid):
        user = self.get_user(request)
        task = user.tasks.get(tid=tid)
        return Response(task.__properties__)
