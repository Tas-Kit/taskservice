# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from neomodel.exceptions import DoesNotExist
from mock import patch, MagicMock

from task import utils
from taskservice.exceptions import MissingRequiredParam, BadRequest
from task.models.user_node import UserNode
from task.models.task import TaskInst
from task.models.step import StepInst
from taskservice.constants import ACCEPTANCE
# Create your tests here.


class TestUtils(TestCase):

    @patch('taskservice.utils.userservice.get_user', return_value=[])
    def test_assert_uid_valid(self, mock_get_user):
        with self.assertRaises(BadRequest):
            utils.assert_uid_valid('bad uid')

    @patch('taskservice.utils.userservice.get_user', side_effect=BadRequest('bad request'))
    def test_assert_uid_error(self, mock_get_user):
        with self.assertRaises(BadRequest):
            utils.assert_uid_valid('bad uid')

    @patch('taskservice.utils.userservice.get_user', return_value='test user')
    def test_get_user_by_username(self, mock_get_user):
        self.assertEqual('test user', utils.get_user_by_username('test user'))

    def test_get_user_by_invalid_username(self):
        with self.assertRaises(BadRequest):
            utils.get_user_by_username('test_user')

    @patch('task.utils.assert_uid_valid')
    @patch('neomodel.StructuredNode.get_or_create')
    def test_get_user(self, mock_get_or_create, mock_assert_uid_valid):
        mock_request = MagicMock()
        mock_request._request.META = {'HTTP_COOKIE': 'hello=abc;uid=test_id'}
        utils.get_user(mock_request)
        mock_get_or_create.assert_called_once_with({'uid': 'test_id'})

    def test_process_single_field_method_not_equal(self):
        mock_request = MagicMock(method='GET')
        mock_field = MagicMock(method='POST', name='test_name')
        kwargs = {}
        utils.process_single_field(mock_request, mock_field, kwargs)
        self.assertEqual(kwargs, {})

    def test_process_single_field_method_not_in_request(self):
        mock_request = MagicMock(method='POST')
        mock_field = MagicMock(method='POST')
        mock_field.name = 'test_name'
        kwargs = {}
        with self.assertRaises(MissingRequiredParam):
            utils.process_single_field(mock_request, mock_field, kwargs)

    def test_process_single_field_method_replace_data(self):
        sample_data = {'test_name': 'sample_data'}
        mock_request = MagicMock(method='POST', data=sample_data)
        mock_field = MagicMock(method='POST', is_required=True)
        mock_field.name = 'test_name'
        kwargs = {}
        utils.process_single_field(mock_request, mock_field, kwargs)
        self.assertEqual(kwargs, sample_data)

    @patch('task.utils.process_single_field')
    def test_process_fields(self, mock_process_single_field):
        mock_view = MagicMock()
        mock_view.schema._manual_fields = ['a', 'b', 'c']
        utils.process_fields(mock_view, None, None)
        self.assertEqual(mock_process_single_field.call_count, 3)

    def test_tid_to_task(self):
        user = UserNode(uid='abc').save()
        task = TaskInst(name='hi').save()

        kwargs = {'tid': task.tid}
        with self.assertRaises(DoesNotExist):
            utils.tid_to_task(user, kwargs)

        task.allow_link_sharing = True
        task.save()

        utils.tid_to_task(user, kwargs)
        self.assertNotIn('tid', kwargs)
        self.assertEqual(task, kwargs['task'])
        has_task = user.tasks.relationship(task)
        self.assertEqual(ACCEPTANCE.ACCEPT, has_task.acceptance)

        has_task.acceptance = ACCEPTANCE.REJECT
        has_task.save()
        kwargs = {'tid': task.tid}
        utils.tid_to_task(user, kwargs)
        self.assertNotIn('tid', kwargs)
        self.assertEqual(task, kwargs['task'])
        has_task = user.tasks.relationship(task)
        self.assertEqual(ACCEPTANCE.ACCEPT, has_task.acceptance)

        task.allow_link_sharing = False
        has_task.acceptance = ACCEPTANCE.REJECT
        task.save()
        has_task.save()
        kwargs = {'tid': task.tid}
        utils.tid_to_task(user, kwargs)
        self.assertNotIn('tid', kwargs)
        self.assertEqual(task, kwargs['task'])
        has_task = user.tasks.relationship(task)
        self.assertEqual(ACCEPTANCE.ACCEPT, has_task.acceptance)

    def test_sid_to_step(self):
        user = UserNode(uid='user_abc').save()
        step = StepInst(name='step1').save()

        kwargs = {'sid': ''}
        with self.assertRaises(DoesNotExist):
            utils.sid_to_step(user, kwargs)

        kwargs = {'sid': step.sid}
        utils.sid_to_step(user, kwargs)
        self.assertNotIn('sid', kwargs)
        self.assertEqual(step, kwargs['step'])

    @patch('task.utils.tid_to_task')
    @patch('task.utils.get_user', return_value='mock_user')
    @patch('task.utils.process_fields')
    def test_preprocess(self, mock_process_fields, mock_get_user, mock_tid_to_task):
        mock_func = MagicMock()
        mock_apiview = MagicMock()
        mock_request = MagicMock()
        wrapper = utils.preprocess(mock_func)
        wrapper(mock_apiview, mock_request)
        mock_process_fields.assert_called_once_with(mock_apiview, mock_request, {})
        mock_get_user.assert_called_once_with(mock_request)
        mock_tid_to_task.assert_called_once_with('mock_user', {})
        mock_func.assert_called_once_with(mock_apiview, mock_request, 'mock_user')
