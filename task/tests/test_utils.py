# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, MagicMock
from task import utils
from taskservice.exceptions import MissingRequiredParam
from task.models.user_node import UserNode
# Create your tests here.


class TestUtils(TestCase):

    @patch('neomodel.StructuredNode.get_or_create')
    def test_get_user(self, mock_get_or_create):
        mock_request = MagicMock(META={'HTTP_COOKIE': 'test_id'})
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
        user = UserNode()
        mock_task = MagicMock()
        kwargs = {'tid': 'anytaskid'}
        with patch('neomodel.RelationshipManager.get') as mock_get:
            mock_get.return_value = mock_task
            utils.tid_to_task(user, kwargs)
            self.assertTrue('tid' not in kwargs)
            self.assertIs(mock_task, kwargs['task'])
            mock_get.assert_called_once_with(tid='anytaskid')

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
