# -*- coding: utf-8 -*-
"""Views for Main."""
from __future__ import unicode_literals

# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from task.models.user_node import UserNode
from taskservice.schemas import Schema, Field
from task.models.step import StepInst
from task.utils import preprocess, get_user_by_username, assert_uid_valid
from django.contrib.auth.models import User
# Create your views here.


class TaskListView(APIView):
    schema = Schema(manual_fields=[
        Field(
            'name',
            method='POST',
            required=True,
        ),
    ])

    @preprocess
    def get(self, request, user):
        return Response({
            task.tid: {
                'task': task.__properties__,
                'has_task': user.tasks.relationship(task).__properties__
            }
            for task in user.tasks
        })

    @preprocess
    def post(self, request, user, name):
        task = user.create_task(name)
        return Response(task.__properties__)


class TaskChangeInvitationView(APIView):

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
        ),
        Field(
            'super_role',
            method='POST',
            required=False
        )
    ])

    @preprocess
    def post(self, request, user, task, uid, role=None, super_role=None):
        assert_uid_valid(uid)
        target_user = task.users.get(uid=uid)
        user.change_invitation(task, target_user, role, super_role)
        return Response('SUCCESS')


class TaskInvitationView(APIView):
    schema = Schema(manual_fields=[
        Field(
            'username',
            method='POST',
            required=True,
        ),
        Field(
            'role',
            method='POST',
            required=False
        ),
        Field(
            'acceptance',
            method='PUT',
            required=True
        ),
        Field(
            'uid',
            method='DELETE',
            required=True
        )
    ])

    @preprocess
    def post(self, request, user, task, username, role=None):
        target_user = get_user_by_username(username)
        target_user_node = UserNode.get_or_create({'uid': target_user.id})[0]
        user.invite(task, target_user_node, role)
        return Response('SUCCESS')

    @preprocess
    def put(self, request, user, task, acceptance):
        user.respond_invitation(task, acceptance)
        return Response('SUCCESS')

    @preprocess
    def delete(self, request, user, task, uid):
        assert_uid_valid(uid)
        target_user = UserNode.get_or_create({'uid': uid})[0]
        user.delete_invitation(task, target_user)
        return Response('SUCCESS')


class TaskGraphView(APIView):

    @preprocess
    def get(self, request, user, task):
        steps = task.steps
        user_map = {
            user_node.uid: user_node
            for user_node in task.users
        }
        users = {
            task_user.id: {
                'basic': {
                    'first_name': task_user.first_name,
                    'last_name': task_user.last_name
                },
                'has_task': task.users.relationship(user_map[str(task_user.id)]).__properties__
            }
            for task_user in User.objects.filter(pk__in=user_map.keys())
        }

        edges = [
            {
                'from': step.sid,
                'to': edge.sid,
                'value': step.nexts.relationship(StepInst(id=edge.id)).value
            }
            for step in steps
            for edge in step.nexts
        ]
        nodes = {
            step.sid: step.__properties__
            for step in steps
        }
        data = {
            'nodes': nodes,
            'edges': edges,
            'users': users
        }
        return Response(data)


class TaskDetailView(APIView):
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
    def get(self, request, user, task):
        return Response(task.__properties__)

    @preprocess
    def put(self, request, user, task, **data):
        task = user.update_task(task, data)
        return Response(task.__properties__)
