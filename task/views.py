# -*- coding: utf-8 -*-
"""Views for Main."""
from __future__ import unicode_literals

# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from task.models.user_node import UserNode
from taskservice.schemas import Schema, Field
from taskservice.constants import SUPER_ROLE
from task.utils import preprocess, get_user_by_username, assert_uid_valid
from rest_framework_tracking.mixins import LoggingMixin
# Create your views here.


class UserView(LoggingMixin, APIView):

    @preprocess
    def get(self, request, user):
        return Response('Deprecated API')


class TaskTriggerView(LoggingMixin, APIView):
    schema = Schema(manual_fields=[
        Field(
            'sid',
            method='POST',
            required=True
        )
    ])

    @preprocess
    def post(self, request, user, task, sid):
        user.trigger(task, sid)
        return Response(task.get_graph())


class TaskListView(LoggingMixin, APIView):
    schema = Schema(manual_fields=[
        Field(
            'name',
            method='POST',
            required=True
        ),
        Field(
            'status',
            method='POST',
        ),
        Field(
            'roles',
            method='POST',
        ),
        Field(
            'deadline',
            method='POST',
        ),
        Field(
            'expected_effort_unit',
            method='POST',
        ),
        Field(
            'expected_effort_num',
            method='POST',
        ),
        Field(
            'description',
            method='POST',
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
    def post(self, request, user, **task_info):
        task = user.create_task(task_info['name'], task_info)
        return Response(task.get_graph())


class TaskChangeInvitationView(LoggingMixin, APIView):

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


class TaskRespondInvitationView(LoggingMixin, APIView):
    schema = Schema(manual_fields=[
        Field(
            'acceptance',
            method='POST',
            required=True
        )
    ])

    @preprocess
    def post(self, request, user, task, acceptance):
        user.respond_invitation(task, acceptance)
        return Response('SUCCESS')


class TaskRevokeInvitationView(LoggingMixin, APIView):
    schema = Schema(manual_fields=[
        Field(
            'uid',
            method='POST',
            required=True
        )
    ])

    @preprocess
    def post(self, request, user, task, uid):
        assert_uid_valid(uid)
        target_user = UserNode.get_or_create({'uid': uid})[0]
        user.revoke_invitation(task, target_user)
        return Response('SUCCESS')


class TaskInvitationView(LoggingMixin, APIView):
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
            'super_role',
            method='POST',
            required=False
        )
    ])

    @preprocess
    def post(self, request, user, task, username, super_role=SUPER_ROLE.STANDARD, role=None):
        target_user = get_user_by_username(username)
        target_user_node = UserNode.get_or_create({'uid': target_user.id})[0]
        user.invite(task, target_user_node, super_role, role)
        return Response({
            'basic': {
                'uid': str(target_user.id),
                'email': target_user.email,
                'username': target_user.username,
                'first_name': target_user.first_name,
                'last_name': target_user.last_name
            },
            'has_task': target_user_node.tasks.relationship(task).__properties__
        })


class TaskCloneView(LoggingMixin, APIView):
    schema = Schema(manual_fields=[
        Field(
            'task_info',
            method='POST',
            required=True
        )
    ])

    @preprocess
    def post(self, request, user, task, task_info):
        new_task = user.clone_task(task, task_info)
        return Response(new_task.get_graph())


class TaskGraphView(LoggingMixin, APIView):
    schema = Schema(manual_fields=[
        Field(
            'nodes',
            method='PATCH',
            required=True,
        ),
        Field(
            'edges',
            method='PATCH',
            required=True,
        ),
        Field(
            'task_info',
            method='PATCH',
            required=False,
        )
    ])

    @preprocess
    def get(self, request, user, task):
        return Response(task.get_graph())

    @preprocess
    def patch(self, request, user, task, nodes, edges, task_info=None):
        user.assert_admin(task)
        user.assert_accept(task)
        task.save_graph(nodes, edges, task_info)
        return Response(task.get_graph())


class TaskDetailView(LoggingMixin, APIView):
    schema = Schema(manual_fields=[
        Field(
            'name',
            method='PATCH',
        ),
        Field(
            'status',
            method='PATCH',
        ),
        Field(
            'roles',
            method='PATCH',
        ),
        Field(
            'deadline',
            method='PATCH',
        ),
        Field(
            'expected_effort_unit',
            method='PATCH',
        ),
        Field(
            'expected_effort_num',
            method='PATCH',
        ),
        Field(
            'description',
            method='PATCH',
        ),
    ])

    @preprocess
    def get(self, request, user, task):
        return Response(task.__properties__)

    @preprocess
    def patch(self, request, user, task, **task_info):
        user.update_task(task, task_info)
        return Response(task.__properties__)

    @preprocess
    def delete(self, request, user, task):
        user.delete_task(task)
        return Response('SUCCESS')
