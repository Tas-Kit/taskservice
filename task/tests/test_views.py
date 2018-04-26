# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from task.views import TaskListView
from mock import patch, MagicMock
from task.models.relationships import HasTask
from task.models.task import TaskInst
from task.models.user_node import UserNode
from taskservice.constants import SUPER_ROLE
from taskservice.settings import neo4jdb
# Create your tests here.


class TestTaskListView(TestCase):

    @classmethod
    def setUpClass(cls):
        neo4jdb.delete_all()
        cls.user = UserNode(uid='1').save()
        cls.task1 = TaskInst(name='task 1').save()
        cls.task2 = TaskInst(name='task 2').save()
        cls.user.tasks.connect(cls.task1)
        cls.user.tasks.connect(cls.task2)

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.client.cookies['uid'] = '1'

    def test_get(self):
        response = self.client.get('/api/v1/task/')
        self.assertEqual(len(response.data), 2)
