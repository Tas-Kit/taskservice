# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from task.models.task import TaskInst
from task.models.step import StepInst
from mock import patch, MagicMock
from taskservice.constants import STATUS


class TestTask(TestCase):

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
        task = TaskInst(roles=['role2', 'role3'])
        task.update(task_info)
        self.assertEqual('new task', task.name)
        self.assertEqual('new description', task.description)
        self.assertEqual(['role1', 'role2'], task.roles)
        self.assertFalse(hasattr(task, 'id'))
        self.assertNotEqual('test tid', task.tid)
        self.assertEqual(t, task.deadline.isoformat() + 'Z')
        mock_save.assert_called_once()
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
        user1.has_task.relationship = MagicMock(
            return_value=user1_has_task)
        user2.has_task.relationship = MagicMock(
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
                        mock_add_nodes):
        task = TaskInst(name='task').save()
        task.save_graph('my nodes', 'my edges')
        mock_assert_start_end.assert_called_once_with('my nodes')
        self.assertEqual(2, mock_get_sid_edge_sets.call_count)
        self.assertEqual(2, mock_set_diff.call_count)
        mock_get_node_edge_map.assert_called_once_with(
            'my nodes', 'my edges')
        mock_remove_edges.assert_called_once()
        mock_remove_nodes.assert_called_once()
        mock_change_edges.assert_called_once()
        mock_change_nodes.assert_called_once()
        mock_add_edges.assert_called_once()
        mock_add_nodes.assert_called_once()

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

    @patch('neomodel.StructuredNode.delete')
    def test_remove_nodes(self, mock_delete):
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
                'value': 'test_value'
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
