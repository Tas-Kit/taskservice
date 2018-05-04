# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from json import dumps
from task.models.user_node import UserNode
from task.models.step import StepInst
from taskservice.settings.dev import neo4jdb
from django.contrib.auth.models import User
from taskservice.constants import ACCEPTANCE, STATUS, SUPER_ROLE, NODE_TYPE
# Create your tests here.

api_url = '/api/v1/task/'


class TestTaskListView(TestCase):

    @classmethod
    def setUpTestData(cls):
        neo4jdb.delete_all()

    def setUp(self):
        self.client.cookies['uid'] = '1'

    def test_get(self):
        user = UserNode(uid='1').save()
        task1 = user.create_task('task 1')
        task2 = user.create_task('task 2')
        response = self.client.get(api_url)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[task1.tid]['task'], task1.__properties__)
        self.assertEqual(response.data[task1.tid]['has_task'], user.tasks.relationship(task1).__properties__)
        self.assertEqual(response.data[task2.tid]['task'], task2.__properties__)
        self.assertEqual(response.data[task2.tid]['has_task'], user.tasks.relationship(task2).__properties__)

    def test_post(self):
        response = self.client.post(api_url, data={
            'name': 'new task'
        })
        self.assertEqual('new task', response.data['name'])
        self.assertEqual(STATUS.NEW, response.data['status'])


class TestTaskGraphView(TestCase):

    @classmethod
    def setUpTestData(cls):
        neo4jdb.delete_all()

    def setUp(self):
        self.client.cookies['uid'] = '1'
        self.user1_data = {
            'pk': 1,
            'username': 'user 1',
            'first_name': 'first1',
            'last_name': 'last1'
        }
        self.user2_data = {
            'pk': 2,
            'username': 'user 2',
            'first_name': 'first2',
            'last_name': 'last2'
        }
        User(**self.user1_data).save()
        User(**self.user2_data).save()
        self.user1 = UserNode(uid='1').save()
        self.user2 = UserNode(uid='2').save()
        self.task = self.user1.create_task(name='test task')
        self.user2.tasks.connect(self.task)
        self.start_step = self.task.steps.get(node_type=NODE_TYPE.START)
        self.end_step = self.task.steps.get(node_type=NODE_TYPE.END)
        self.step1 = StepInst(name='step 1').save()
        self.step2 = StepInst(name='step 2').save()
        self.start_step.nexts.connect(self.step1)
        self.start_step.nexts.connect(self.step2)
        self.step1.nexts.connect(self.end_step)
        self.step2.nexts.connect(self.end_step)
        self.task.steps.connect(self.step1)
        self.task.steps.connect(self.step2)

    def test_get_graph(self):
        response = self.client.get('{0}graph/{1}/'.format(api_url, self.task.tid))
        nodes = response.data['nodes']
        edges = response.data['edges']
        users = response.data['users']
        del self.user1_data['pk']
        del self.user2_data['pk']
        self.assertEqual(self.user1_data, users[self.user1.uid]['basic'])
        self.assertEqual(self.user2_data, users[self.user2.uid]['basic'])
        self.assertEqual(self.start_step.__properties__, nodes[self.start_step.sid])
        self.assertEqual(self.end_step.__properties__, nodes[self.end_step.sid])
        self.assertEqual(self.step1.__properties__, nodes[self.step1.sid])
        self.assertEqual(self.step2.__properties__, nodes[self.step2.sid])
        self.assertEqual(4, len(edges))
        self.assertIn({
            'from': self.start_step.sid,
            'to': self.step1.sid,
            'value': None
        }, edges)
        self.assertIn({
            'from': self.start_step.sid,
            'to': self.step2.sid,
            'value': None
        }, edges)
        self.assertIn({
            'from': self.step1.sid,
            'to': self.end_step.sid,
            'value': None
        }, edges)
        self.assertIn({
            'from': self.step2.sid,
            'to': self.end_step.sid,
            'value': None
        }, edges)


class TestTaskDetailView(TestCase):

    @classmethod
    def setUpTestData(cls):
        neo4jdb.delete_all()

    def setUp(self):
        self.client.cookies['uid'] = '1'
        self.user = UserNode(uid='1').save()
        self.task = self.user.create_task('test task')
        self.url = '{0}{1}/'.format(api_url, self.task.tid)

    def tearDown(self):
        self.user.delete()
        self.task.delete()

    def test_get(self):
        response = self.client.get(self.url)
        self.assertEqual(self.task.__properties__, response.data)

    def test_update(self):
        self.task.name = 'new task'
        response = self.client.patch(self.url, content_type='application/json', data=dumps({
            'name': 'new task'
        }))
        self.assertEqual(self.task.__properties__, response.data)


class TestTaskInvitationView(TestCase):

    @classmethod
    def setUpTestData(cls):
        neo4jdb.delete_all()

    def setUp(self):
        self.client.cookies['uid'] = '1'
        self.user1 = UserNode(uid='1').save()
        self.user2 = UserNode(uid='2').save()
        User(pk=2, username='username').save()
        self.task = self.user1.create_task(name='test task')
        self.task.roles = ['teacher']
        self.task.save()

    def tearDown(self):
        self.user1.delete()
        self.user2.delete()
        self.task.delete()

    def test_invite(self):
        response = self.client.post('{0}invitation/{1}/'.format(api_url, self.task.tid), data={
            'username': 'username',
            'super_role': SUPER_ROLE.ADMIN,
            'role': 'teacher'
        })
        self.assertEqual(response.data, 'SUCCESS')
        self.assertTrue(self.user2.tasks.is_connected(self.task))
        has_task = self.user2.tasks.relationship(self.task)
        self.assertEqual(SUPER_ROLE.ADMIN, has_task.super_role)
        self.assertEqual('teacher', has_task.role)

    def test_revoke(self):
        self.user2.tasks.connect(self.task, {
            'acceptance': ACCEPTANCE.WAITING
        })
        response = self.client.post('{0}invitation/revoke/{1}/'.format(api_url, self.task.tid), data={
            'uid': '2'
        })
        self.assertEqual(response.data, 'SUCCESS')
        self.assertFalse(self.user2.tasks.is_connected(self.task))

    def test_respond_invitation(self):
        self.user2.tasks.connect(self.task, {
            'acceptance': ACCEPTANCE.WAITING
        })
        self.client.cookies['uid'] = '2'
        response = self.client.post('{0}invitation/respond/{1}/'.format(api_url, self.task.tid), data={
            'acceptance': ACCEPTANCE.ACCEPT
        })
        self.assertEqual(response.data, 'SUCCESS')
        has_task = self.user2.tasks.relationship(self.task)
        self.assertEqual(ACCEPTANCE.ACCEPT, has_task.acceptance)

    def test_change_invitation(self):
        self.user2.tasks.connect(self.task, {
            'super_role': SUPER_ROLE.ADMIN,
            'role': 'teacher'
        })
        response = self.client.post('{0}invitation/change/{1}/'.format(api_url, self.task.tid), data={
            'uid': '2',
            'super_role': SUPER_ROLE.STANDARD
        })
        self.assertEqual(response.data, 'SUCCESS')
        self.assertTrue(self.user2.tasks.is_connected(self.task))
        has_task = self.user2.tasks.relationship(self.task)
        self.assertEqual(SUPER_ROLE.STANDARD, has_task.super_role)
        self.assertIs(None, has_task.role)
