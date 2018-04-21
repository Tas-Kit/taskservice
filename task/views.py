# -*- coding: utf-8 -*-
"""Views for Main."""
from __future__ import unicode_literals

# from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from task.models.task import TaskModel

# Create your views here.


class TaskView(APIView):

    def get(self, request, pk=None):
        if pk is None or pk == '':
            return Response('hello')
        else:
            task = TaskModel(id=int(pk))
            task.refresh()
            return Response(task.__properties__)
