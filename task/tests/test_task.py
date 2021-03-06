# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from task.models.task import TaskInst
from task.models.step import StepInst
from task.models.user_node import UserNode
from mock import patch, MagicMock
from taskservice.constants import STATUS, NODE_TYPE
from taskservice.exceptions import BadRequest
from dateutil.parser import parse


class TestTask(TestCase):

    def test_get_info_origin(self):
        task = TaskInst()
        task.origin = MagicMock()
        origin_task = MagicMock()
        origin_task.tid = 'hello'
        task.origin.all = MagicMock(return_value=[origin_task])
        origin = task.get_origin()
        self.assertEqual(origin_task, origin)
        info = task.get_info()
        info['tid'] = 'hello'

    def test_get_info_no_origin(self):
        task = TaskInst()
        task.origin = MagicMock()
        task.origin.all = MagicMock(return_value=[])
        origin = task.get_origin()
        self.assertIs(None, origin)

    def test_preprocess_edges(self):
        sample_edges = [
            {
                'from': 'node1',
                'to': 'node2'
            },
            {
                'from': 'node1',
                'to': 'node2'
            },
            {
                'from': 'node1',
                'to': 'node2'
            },
            {
                'from': 'node3',
                'to': 'node3'
            }
        ]
        processed_edges = TaskInst.preprocess_edges(sample_edges)
        self.assertEqual([{
            'from': 'node1',
            'to': 'node2'
        }], processed_edges)

    @patch('task.models.task.TaskInst.upgrade_graph')
    @patch('task.models.task.TaskInst.clone')
    @patch('task.models.task.TaskInst.assert_original')
    @patch('task.models.user_node.UserNode.assert_owner')
    def test_upload(self,
                    mock_assert_owner,
                    mock_assert_original,
                    mock_clone,
                    mock_upgrade_graph):
        user = UserNode()
        task = TaskInst()
        new_task = TaskInst()
        mock_clone.return_value = new_task
        result = user.upload(task)
        self.assertTrue(new_task is result)
        mock_assert_original.assert_called_once()
        mock_assert_owner.assert_called_once_with(task)
        mock_clone.assert_called_once()
        mock_upgrade_graph.assert_not_called()

    @patch('task.models.task.TaskInst.upgrade_graph')
    @patch('task.models.task.TaskInst.clone')
    @patch('task.models.task.TaskInst.assert_original')
    @patch('task.models.user_node.UserNode.assert_owner')
    def test_upload_existing_task(self,
                                  mock_assert_owner,
                                  mock_assert_original,
                                  mock_clone,
                                  mock_upgrade_graph):
        user = UserNode()
        task = TaskInst()
        target_task = TaskInst()
        new_task = user.upload(task, target_task)
        self.assertIs(new_task, target_task)
        mock_assert_owner.assert_called_once_with(task)
        mock_assert_original.assert_called_once()
        mock_clone.assert_not_called()
        mock_upgrade_graph.assert_called_once()

    @patch('taskservice.utils.userservice.get_user_list', return_value=[])
    def test_clone(self, mock_get_user):
        user = UserNode(uid='sample').save()
        task = user.create_task('task')
        task.status = STATUS.IN_PROGRESS
        step = StepInst(name='step', status=STATUS.IN_PROGRESS).save()
        start = task.steps.get(node_type=NODE_TYPE.START)
        end = task.steps.get(node_type=NODE_TYPE.END)
        start.nexts.connect(step)
        step.nexts.connect(end)
        task.steps.connect(step)
        new_task = task.clone()
        self.assertEqual(new_task.name, task.name)
        self.assertEqual(new_task.status, STATUS.NEW)
        new_start = new_task.steps.get(node_type=NODE_TYPE.START)
        new_step = new_task.steps.get(node_type=NODE_TYPE.NORMAL)
        new_end = new_task.steps.get(node_type=NODE_TYPE.END)
        self.assertEqual(new_step.name, 'step')
        self.assertEqual(new_step.status, STATUS.NEW)
        self.assertTrue(new_start.nexts.is_connected(new_step))
        self.assertTrue(new_step.nexts.is_connected(new_end))

    @patch('neomodel.StructuredNode.delete')
    def test_delete(self, mock_delete):
        task = TaskInst()
        mock_step = MagicMock()
        task.steps = [mock_step] * 2
        task.delete()
        self.assertEqual(2, mock_step.delete.call_count)
        mock_delete.assert_called_once()

    @patch('neomodel.StructuredNode.save')
    @patch('task.models.task.TaskModel.update_roles')
    def test_update(self, mock_update_roles, mock_save):
        t = '2018-05-12T21:54:43.562037Z'
        task_info = {
            'id': 'test id',
            'tid': 'test tid',
            'name': 'new task',
            'deadline': t,
            'description': 'new description',
            'roles': ['role1', 'role2']
        }
        task = TaskInst(name='hello', roles=['role2', 'role3'])
        task.update(task_info)
        self.assertEqual('new task', task.name)
        self.assertEqual('new description', task.description)
        self.assertEqual(['role1', 'role2'], task.roles)
        self.assertEqual(['role1', 'role2'], task.roles)
        self.assertFalse(hasattr(task, 'id'))
        self.assertNotEqual('test tid', task.tid)
        self.assertEqual(parse(t), task.deadline)
        mock_update_roles.assert_called_once_with(['role2', 'role3'])

    @patch('neomodel.StructuredNode.save')
    def test_update_step_roles(self, mock_save):
        task = TaskInst()
        step1 = StepInst(assignees=['role1', 'role2'],
                         reviewers=['role3', 'role4'])
        step2 = StepInst(assignees=['role2', 'role3'],
                         reviewers=['role2', 'role4'])
        task.steps.all = MagicMock(return_value=[step1, step2])
        roles = ['role2', 'role4']
        task.update_step_roles(roles)
        self.assertEqual(['role1'], step1.assignees)
        self.assertEqual(['role3'], step1.reviewers)
        self.assertEqual(['role3'], step2.assignees)
        self.assertEqual([], step2.reviewers)
        self.assertEqual(2, mock_save.call_count)

    def test_update_user_roles(self):
        task = TaskInst()
        user1 = MagicMock()
        user2 = MagicMock()
        user1_has_task = MagicMock()
        user1_has_task.role = 'role1'
        user2_has_task = MagicMock()
        user2_has_task.role = 'role2'
        user1.tasks.relationship = MagicMock(
            return_value=user1_has_task)
        user2.tasks.relationship = MagicMock(
            return_value=user2_has_task)
        task.users.all = MagicMock(return_value=[user1, user2])
        task.update_user_roles(['role2', 'role3'])
        self.assertEqual('role1', user1_has_task.role)
        self.assertEqual(None, user2_has_task.role)
        user1_has_task.save.assert_not_called()
        user2_has_task.save.assert_called_once()

    @patch('task.models.task.TaskModel.update_user_roles')
    @patch('task.models.task.TaskModel.update_step_roles')
    @patch('task.models.utils.set_diff',
           return_value=(MagicMock(),
                         MagicMock(),
                         MagicMock()))
    def test_update_roles(self,
                          mock_set_diff,
                          mock_update_step_roles,
                          mock_update_user_roles):
        task = TaskInst()
        task.update_roles({})
        mock_set_diff.assert_called_once()
        mock_update_user_roles.assert_called_once()
        mock_update_user_roles.assert_called_once()

    @patch('taskservice.utils.userservice.get_user_list')
    @patch('task.models.task.TaskModel.preprocess_edges', return_value='processed_edges')
    @patch('task.models.task.TaskModel.add_nodes', return_value=MagicMock())
    @patch('task.models.task.TaskModel.add_edges')
    @patch('task.models.task.TaskModel.change_nodes')
    @patch('task.models.task.TaskModel.change_edges')
    @patch('task.models.task.TaskModel.remove_nodes')
    @patch('task.models.task.TaskModel.remove_edges')
    @patch('task.models.task.utils.get_node_edge_map', return_value=(MagicMock(), MagicMock()))
    @patch('task.models.utils.set_diff', return_value=(MagicMock(), MagicMock(), MagicMock()))
    @patch('task.models.utils.get_sid_edge_sets', return_value=(MagicMock(), MagicMock()))
    @patch('task.models.utils.assert_start_end')
    def test_save_graph(self,
                        mock_assert_start_end,
                        mock_get_sid_edge_sets,
                        mock_set_diff,
                        mock_get_node_edge_map,
                        mock_remove_edges,
                        mock_remove_nodes,
                        mock_change_edges,
                        mock_change_nodes,
                        mock_add_edges,
                        mock_add_nodes,
                        mock_preprocess_edges,
                        mock_get_user_list):
        task = TaskInst(name='task').save()
        task.save_graph('my nodes', 'my edges')
        mock_assert_start_end.assert_called_once_with('my nodes')
        self.assertEqual(2, mock_get_sid_edge_sets.call_count)
        self.assertEqual(2, mock_set_diff.call_count)
        mock_get_node_edge_map.assert_called_once_with(
            'my nodes', 'processed_edges')
        mock_remove_edges.assert_called_once()
        mock_remove_nodes.assert_called_once()
        mock_change_edges.assert_called_once()
        mock_change_nodes.assert_called_once()
        mock_add_edges.assert_called_once()
        mock_add_nodes.assert_called_once()

    def test_upgrade_graph(self):
        data = {
            'nodes': 'abc',
            'edges': 'def',
            'task_info': 'ghi'
        }
        t1 = TaskInst()
        t2 = TaskInst()
        t1.save_graph = MagicMock()
        t2.get_graph = MagicMock(return_value=data)
        t1.upgrade_graph(t2)
        t2.get_graph.assert_called_once()
        t1.save_graph.assert_called_once_with('abc', 'def', 'ghi')

    def test_assert_no_user(self):
        user = UserNode(uid='abc').save()
        task = user.create_task(name='name')
        with self.assertRaises(BadRequest):
            task.assert_no_user()

        task = TaskInst(name='name').save()
        task.assert_no_user()

    def test_assert_original(self):
        task = TaskInst(name='name').save()
        task.assert_original()
        new_task = TaskInst(name='new').save()
        new_task.set_origin(task)
        task.assert_original()
        with self.assertRaises(BadRequest):
            new_task.assert_original()

    @patch('neomodel.StructuredNode.save')
    def test_start(self, mock_save):
        task = TaskInst()
        task.start()
        self.assertEqual(STATUS.IN_PROGRESS, task.status)
        mock_save.assert_called_once()

    @patch('neomodel.StructuredNode.save')
    def test_complete(self, mock_save):
        task = TaskInst()
        task.complete()
        self.assertEqual(STATUS.COMPLETED, task.status)
        mock_save.assert_called_once()

    @patch('neomodel.RelationshipManager.disconnect')
    def test_remove_edges(self, mock_disconnect):
        node1 = StepInst()
        node2 = StepInst()
        edges = [(node1.sid, node2.sid)]
        task = TaskInst()
        task.steps.get = MagicMock(side_effect=[node1, node2])
        task.remove_edges(edges)
        node1.nexts.disconnect.assert_called_once_with(node2)

    @patch('task.models.step.StepInst.delete_components')
    @patch('neomodel.StructuredNode.delete')
    def test_remove_nodes(self, mock_delete, mock_delete_components):
        node1 = StepInst()
        node2 = StepInst()
        task = TaskInst()
        task.steps.get = MagicMock(side_effect=[node1, node2])
        task.remove_nodes([node1.sid, node2.sid])
        self.assertEqual(2, mock_delete.call_count)

    def test_change_edges(self):
        node1 = StepInst()
        node2 = StepInst()
        task = TaskInst()
        next_step = MagicMock()
        node1.nexts.relationship = MagicMock(return_value=next_step)
        task.steps.get = MagicMock(side_effect=[node1, node2])
        task.change_edges([(node1.sid, node2.sid)], {
            node1.sid + '->' + node2.sid: {
                'label': 'test_value'
            }
        })
        next_step.save.assert_called_once()
        next_step.value = 'test_value'

    @patch('neomodel.StructuredNode.save')
    def test_change_node(self, mock_save):
        node1 = StepInst()
        node2 = StepInst()
        task = TaskInst()
        task.steps.get = MagicMock(side_effect=[node1, node2])
        task.change_nodes([node1.sid, node2.sid], {
            node1.sid: {
                'name': 'node1 name',
                'description': 'my description 1'
            },
            node2.sid: {
                'name': 'node2 name',
                'description': 'my description 2'
            }
        })
        self.assertEqual('node1 name', node1.name)
        self.assertEqual('node2 name', node2.name)
        self.assertEqual('my description 1', node1.description)
        self.assertEqual('my description 2', node2.description)
        self.assertEqual(2, mock_save.call_count)

    @patch('neomodel.RelationshipManager.connect')
    @patch('neomodel.StructuredNode.save')
    def test_add_nodes(self, mock_save, mock_connect):
        sids = ['newsid']
        node_map = {
            'newsid': {
                'name': 'new node',
                'description': 'new description',
                'sid': 'sid123',
                'id': '123'
            }
        }
        task = TaskInst()
        sid_map = task.add_nodes(sids, node_map)
        node = mock_connect.call_args[0][0]
        mock_save.assert_called_once()
        mock_connect.assert_called_once()
        self.assertEqual({'newsid': node.sid}, sid_map)
        self.assertEqual('new node', node.name)
        self.assertEqual('new description', node.description)
        self.assertNotEqual('sid123', node.sid)

    @patch('neomodel.RelationshipManager.connect')
    def test_add_edges(self, mock_connect):
        edges = [('old_sid_123', 'old_sid_321')]
        sid_map = {
            'old_sid_123': 'new_sid_123',
            'old_sid_321': 'new_sid_321'
        }
        node1 = StepInst()
        node2 = StepInst()
        task = TaskInst()
        task.steps.get = MagicMock(side_effect=[node1, node2])
        task.add_edges(edges, sid_map)
        sid_args_list = task.steps.get.call_args_list
        self.assertEqual('new_sid_123', sid_args_list[0][1]['sid'])
        self.assertEqual('new_sid_321', sid_args_list[1][1]['sid'])
        mock_connect.assert_called_once()
