# -*- coding: utf-8 -*-
"""Views for Main."""
from __future__ import unicode_literals

# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from task.models.user_node import UserNode
# from taskservice.exceptions import handle_exception

# Create your views here.


class TaskView(APIView):

    def get_user(self, request):
        uid = request.META['HTTP_COOKIE']
        user = UserNode.get_or_create({'uid': uid})[0]
        return user

    def get(self, request, tid=None):
        user = self.get_user(request)
        if tid is None or tid == '':
            tasks = user.tasks.all()
            response = Response([task.__properties__ for task in tasks])
        else:
            task = user.tasks.get(tid=tid)
            response = Response(task.__properties__)
        return response
