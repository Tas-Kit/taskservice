# -*- coding: utf-8 -*-
"""Views for Main."""
from __future__ import unicode_literals

# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from task.models.user_node import UserNode
from taskservice.schemas import Schema, Field
from task.models.step import StepInst
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
            'name',
            method='POST',
            required=True,
        ),
    ])

    def get(self, request):
        user = self.get_user(request)
        return Response({
            task.tid: {
                'task': task.__properties__,
                'relationship': user.tasks.relationship(task).__properties__
            }
            for task in user.tasks
        })

    def post(self, request):
        user = self.get_user(request)
        task_name = request.data['name']
        task = user.create_task(task_name)
        return Response(task.__properties__)


class TaskGraphView(ServiceView):

    def get(self, request, tid):
        user = self.get_user(request)
        task = user.tasks.get(tid=tid)
        steps = task.steps
        edges = [
            {
                'from': step.sid,
                'to': edge.sid,
                'value': step.nexts.relationship(StepInst(id=edge.id)).value
            }
            for step in steps
            for edge in step.nexts
        ]
        data = {
            'nodes': {
                step.sid: step.__properties__
                for step in steps
            },
            'edges': edges
        }
        return Response(data)


class TaskDetailView(ServiceView):
    schema = Schema(manual_fields=[
        Field(
            'name',
            method='PUT',
        ),
        Field(
            'status',
            method='PUT',
        ),
        Field(
            'roles',
            method='PUT',
        ),
        Field(
            'deadline',
            method='PUT',
        ),
        Field(
            'expected_effort_unit',
            method='PUT',
        ),
        Field(
            'expected_effort_num',
            method='PUT',
        ),
        Field(
            'description',
            method='PUT',
        ),
    ])

    def get(self, request, tid):
        user = self.get_user(request)
        task = user.tasks.get(tid=tid)
        return Response(task.__properties__)

    def put(self, request, tid):
        user = self.get_user(request)
        task = user.update_task(tid, request.data)
        return Response(task.__properties__)
