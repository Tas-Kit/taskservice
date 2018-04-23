# -*- coding: utf-8 -*-
"""Views for Main."""
from __future__ import unicode_literals

# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from task.models.user_node import UserNode
from taskservice.schemas import Schema, Field
from task.models.step import StepInst
from task.utils import preprocess

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

    @preprocess
    def get(self, request, user):
        user = self.get_user(request)
        return Response({
            task.tid: {
                'task': task.__properties__,
                'relationship': user.tasks.relationship(task).__properties__
            }
            for task in user.tasks
        })

    @preprocess
    def post(self, request, user):
        task_name = request.data['name']
        task = user.create_task(task_name)
        return Response(task.__properties__)


class TaskInvitationView(ServiceView):
    schema = Schema(manual_fields=[
        Field(
            'uid',
            method='POST',
            required=True,
        ),
        Field(
            'role',
            method='POST',
            required=False
        )
    ])

    @preprocess
    def post(self, request, user, tid):
        uid = request.data['uid']
        role = None
        if 'role' in request.data:
            role = request.data['role']
        user.invite(tid, uid, role)
        return Response('SUCCESS')


class TaskGraphView(ServiceView):

    @preprocess
    def get(self, request, user, tid):
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

    @preprocess
    def get(self, request, user, tid):
        task = user.tasks.get(tid=tid)
        return Response(task.__properties__)

    @preprocess
    def put(self, request, user, tid):
        task = user.update_task(tid, request.data)
        return Response(task.__properties__)
