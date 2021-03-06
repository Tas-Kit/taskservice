# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, MagicMock
from taskservice.constants import SUPER_ROLE, ACCEPTANCE, NODE_TYPE, STATUS
from task.models.user_node import UserNode
from task.models.task import TaskInst
from task.models.step import StepInst
from task.models.relationships import HasTask
from taskservice.exceptions import (
    NotAdmin,
    NotOwner,
    NotAccept,
    AlreadyHasTheTask,
    OwnerCannotChangeInvitation,
    NoSuchRole,
    BadRequest
)
from django.conf import settings
# Create your tests here.
neo4jdb = settings.NEO4JDB


class TestUserNode(TestCase):

    @classmethod
    def setUpClass(cls):
        neo4jdb.delete_all()

    @classmethod
    def tearDownClass(cls):
        # neo4jdb.delete_all()
        pass

    @patch('task.models.user_node.UserNode.assert_has_higher_permission')
    @patch('task.models.user_node.UserNode.assert_accept')
    @patch('task.models.user_node.UserNode.assert_has_task')
    def test_revoke_invitation(self,
                               mock_assert_has_task,
                               mock_assert_accept,
                               mock_assert_has_higher_permission):
        user1 = UserNode(uid='user3').save()
        user2 = UserNode(uid='user4').save()
        task = user1.create_task('sample task')
        user2.tasks.connect(task)
        user1.revoke_invitation(task, user2)
        self.assertEqual(mock_assert_has_task.call_count, 2)
        mock_assert_has_task.called_with(user1, task)
        mock_assert_has_task.called_with(user2, task)
        mock_assert_accept.assert_called_once_with(task)
        mock_assert_has_higher_permission.assert_called_once_with(task, user2)

    def test_assert_has_task(self):
        user = UserNode(uid='user node test uid 1').save()
        task = TaskInst(name='new task').save()
        with self.assertRaises(BadRequest):
            user.assert_has_task(task)

    def test_has_higher_permission(self):
        user1 = UserNode(uid='user1').save()
        user2 = UserNode(uid='user2').save()
        task = user1.create_task('sample task')
        user2.tasks.connect(task, {'acceptance': ACCEPTANCE.ACCEPT})
        with self.assertRaises(BadRequest):
            user2.assert_has_higher_permission(task, user1)

    def test_get_todo_list_with_role(self):
        user = UserNode(uid='test_get_todo_list_with_role').save()
        task = user.create_task('task', {
            'status': STATUS.IN_PROGRESS,
            'roles': ['teacher', 'student', 'parent']
        })
        step1 = StepInst(name='s1',
                         status=STATUS.IN_PROGRESS,
                         assignees=['student', 'parent'],
                         reviewers=['student', 'teacher']).save()
        step2 = StepInst(name='s2',
                         status=STATUS.READY_FOR_REVIEW,
                         assignees=['student', 'parent'],
                         reviewers=['student', 'teacher']).save()
        step3 = StepInst(name='s3',
                         status=STATUS.IN_PROGRESS,
                         assignees=['parent'],
                         reviewers=['teacher']).save()
        step4 = StepInst(name='s4',
                         status=STATUS.IN_PROGRESS,
                         assignees=['parent'],
                         reviewers=['teacher']).save()
        task.steps.connect(step1)
        task.steps.connect(step2)
        task.steps.connect(step3)
        task.steps.connect(step4)
        user.change_role(task, user, 'student')

        todo_list = user.get_todo_list()
        todo_set = set(todo['step']['sid'] for todo in todo_list)
        self.assertEqual(2, len(todo_set))
        self.assertIn(step1.sid, todo_set)
        self.assertIn(step2.sid, todo_set)

    def test_get_todo_list(self):
        user = UserNode(uid='test_get_todo_list').save()
        task1 = user.create_task('t1')
        task2 = user.create_task('t2')
        task3 = user.create_task('t3')

        self.assertEqual([], user.get_todo_list())
        task1.status = STATUS.IN_PROGRESS
        task2.status = STATUS.IN_PROGRESS
        task3.status = STATUS.COMPLETED
        task1.save()
        task2.save()
        task3.save()

        step1_1 = StepInst(name='s1_1', status=STATUS.COMPLETED).save()
        step1_2 = StepInst(name='s1_2', status=STATUS.IN_PROGRESS).save()
        step2_1 = StepInst(name='s2_1', status=STATUS.READY_FOR_REVIEW).save()
        step2_2 = StepInst(name='s2_2', status=STATUS.SKIPPED).save()
        step3_1 = StepInst(name='s3_1', status=STATUS.IN_PROGRESS).save()
        step3_2 = StepInst(name='s3_2', status=STATUS.READY_FOR_REVIEW).save()

        task1.steps.connect(step1_1)
        task1.steps.connect(step1_2)
        task2.steps.connect(step2_1)
        task2.steps.connect(step2_2)
        task3.steps.connect(step3_1)
        task3.steps.connect(step3_2)

        todo_list = user.get_todo_list()
        todo_set = set(todo['task']['tid'] + todo['step']['sid'] for todo in todo_list)
        self.assertEqual(2, len(todo_set))
        self.assertIn(task1.tid + step1_2.sid, todo_set)
        self.assertIn(task2.tid + step2_1.sid, todo_set)

    @patch('task.models.user_node.UserNode.clone_task')
    @patch('task.models.task.TaskModel.assert_no_user')
    def test_download(self, mock_assert_no_user, mock_clone_task):
        user = UserNode()
        task = TaskInst()
        new_task = MagicMock()
        mock_clone_task.return_value = new_task
        result = user.download(task)
        self.assertEqual(new_task, result)
        mock_assert_no_user.assert_called_once()
        mock_clone_task.assert_called_once_with(task)
        new_task.set_origin.assert_called_once_with(task)

    @patch('task.models.task.TaskModel.delete')
    @patch('task.models.user_node.UserNode.assert_owner')
    def test_delete_task(self, mock_assert_owner, mock_delete):
        user = UserNode()
        task = TaskInst()
        user.delete_task(task)
        mock_assert_owner.assert_called_once()
        mock_delete.assert_called_once()

    def test_create_task(self):
        user = UserNode(uid='user node test uid').save()
        task = user.create_task('sample task')
        self.assertEqual('sample task', task.name)
        self.assertTrue(user.tasks.is_connected(task))
        has_task = user.tasks.relationship(task)
        self.assertEqual(SUPER_ROLE.OWNER, has_task.super_role)
        self.assertEqual(None, has_task.role)
        self.assertEqual(ACCEPTANCE.ACCEPT, has_task.acceptance)
        steps = task.steps
        self.assertEqual(2, len(steps))
        start = steps.get(name='Start')
        end = steps.get(name='End')
        self.assertEqual(NODE_TYPE.START, start.node_type)
        self.assertEqual(NODE_TYPE.END, end.node_type)

    @patch('neomodel.RelationshipManager.relationship', return_value=MagicMock())
    @patch('task.models.user_node.UserNode.assert_accept')
    def test_trigger(self, mock_assert_accept, mock_relationship):
        user = UserNode()
        task = MagicMock()
        task.steps = MagicMock()
        user.trigger(task, 'any sid')
        mock_assert_accept.assert_called_once()
        task.steps.get.assert_called_once_with(
            sid='any sid')

    @patch('neomodel.RelationshipManager.relationship', return_value=MagicMock())
    @patch('task.models.user_node.UserNode.assert_accept')
    def test_trigger_start(self, mock_assert_accept, mock_relationship):
        user = UserNode()
        task = MagicMock()
        task.steps = MagicMock()
        user.trigger(task)
        mock_assert_accept.assert_called_once()
        task.steps.get.assert_called_once_with(node_type=NODE_TYPE.START)

    @patch('neomodel.RelationshipManager.connect')
    def test_clone(self, mock_connect):
        user = UserNode()
        task = MagicMock()
        task.assert_original = MagicMock()
        new_task = user.clone_task(task, {})
        mock_connect.assert_called_once_with(new_task, {
            'super_role': SUPER_ROLE.OWNER,
            'acceptance': ACCEPTANCE.ACCEPT
        })
        task.assert_original.assert_called_once()

    @patch('task.models.user_node.UserNode.assert_accept')
    @patch('task.models.user_node.UserNode.assert_admin')
    @patch('task.models.task.TaskInst.update')
    def test_update_task_success(self, mock_update, mock_assert_admin, mock_assert_accept):
        user = UserNode()
        task = TaskInst()
        data = {
            'name': 'task name',
            'description': 'task description'
        }
        user.update_task(task, data)
        mock_update.assert_called_once()
        mock_assert_admin.assert_called_once()
        mock_assert_accept.assert_called_once()

    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.WAITING))
    def test_update_task_not_accept(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAccept):
            user.update_task(task, {})

    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.ACCEPT))
    def test_update_task_not_admin(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAdmin):
            user.update_task(task, {})

    @patch('neomodel.StructuredRel.save')
    def test_respond_invitation_success(self, mock_save):
        user = UserNode()
        task = TaskInst()
        mock_has_task = HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.WAITING)
        user.tasks.relationship = MagicMock(return_value=mock_has_task)
        user.respond_invitation(task, ACCEPTANCE.ACCEPT)
        self.assertEqual(ACCEPTANCE.ACCEPT, mock_has_task.acceptance)

    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT))
    def test_respond_invitation_owner(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(OwnerCannotChangeInvitation):
            user.respond_invitation(task, ACCEPTANCE.WAITING)

    def test_change_role(self):
        user = UserNode(uid='test_change_role').save()
        task = user.create_task('task', {'roles': ['teacher', 'student']})
        user_has_task = user.tasks.relationship(task)
        user_has_task.super_role = SUPER_ROLE.STANDARD
        user_has_task.save()
        with self.assertRaises(NotAdmin):
            user.change_role(task, user, 'teacher')
        user_has_task.super_role = SUPER_ROLE.ADMIN
        user_has_task.save()
        user.change_role(task, user, 'teacher')
        user_has_task = user.tasks.relationship(task)
        self.assertEqual('teacher', user_has_task.role)
        with self.assertRaises(NoSuchRole):
            user.change_role(task, user, 'parent')

    def test_change_task_owner(self):
        user1 = UserNode(uid='test_change_task_owner_1').save()
        task = user1.create_task('task')
        user2 = UserNode(uid='test_change_task_owner_2').save()
        user2.tasks.connect(task)
        with self.assertRaises(NotAccept):
            user1.change_super_role(task, user2, SUPER_ROLE.OWNER)
        user2.respond_invitation(task, ACCEPTANCE.ACCEPT)
        user1.change_super_role(task, user2, SUPER_ROLE.OWNER)
        user1_has_task = user1.tasks.relationship(task)
        user2_has_task = user2.tasks.relationship(task)
        self.assertEqual(SUPER_ROLE.ADMIN, user1_has_task.super_role)
        self.assertEqual(SUPER_ROLE.OWNER, user2_has_task.super_role)

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_super_role_admin(self, mock_save):
        mock_owner_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        mock_user_has_task = HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.ACCEPT)
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        user.tasks.relationship = MagicMock(return_value=mock_owner_has_task)
        target_user.tasks.relationship = MagicMock(return_value=mock_user_has_task)
        user.change_invitation(task, target_user, super_role=SUPER_ROLE.ADMIN)
        self.assertEqual(SUPER_ROLE.ADMIN, mock_user_has_task.super_role)
        self.assertEqual(SUPER_ROLE.OWNER, mock_owner_has_task.super_role)

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_role(self, mock_save):
        mock_owner_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        mock_user_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        user = UserNode()
        task = TaskInst(roles=['teacher'])
        target_user = UserNode()
        user.tasks.relationship = MagicMock(return_value=mock_owner_has_task)
        target_user.tasks.relationship = MagicMock(return_value=mock_user_has_task)
        user.change_invitation(task, target_user, role='teacher')
        self.assertEqual('teacher', mock_user_has_task.role)
        self.assertEqual(SUPER_ROLE.OWNER, mock_user_has_task.super_role)

    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT))
    def test_change_invitation_has_no_role(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        with self.assertRaises(NoSuchRole):
            user.change_invitation(task, target_user, role='teacher')

    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_change_invitation_not_owner(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        with self.assertRaises(NotOwner):
            user.change_invitation(task, target_user, super_role=SUPER_ROLE.ADMIN)

    @patch('task.models.user_node.notifications.invite')
    @patch('neomodel.RelationshipManager.connect')
    @patch('neomodel.RelationshipManager.is_connected', return_value=False)
    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_invite_success(self, mock_relationship, mock_is_connected, mock_connect, mock_invite):
        user = UserNode()
        user.uid = 'abc'
        target_user = UserNode()
        target_user.uid = 'def'
        task = TaskInst(roles=['teacher'])
        task.tid = 'xyz'
        user.invite(task, target_user, role='teacher')
        mock_connect.assert_called_once_with(task, {
            'role': 'teacher',
            'super_role': SUPER_ROLE.STANDARD
        })
        mock_invite.assert_called_once_with(
            [target_user.uid],
            inviter_id=user.uid,
            task_id=task.tid)

    @patch('neomodel.RelationshipManager.is_connected', return_value=True)
    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_invite_user_already_has_task(self, mock_relationship, mock_is_connected):
        user = UserNode()
        target_user = UserNode()
        task = TaskInst(roles=['teacher'])
        with self.assertRaises(AlreadyHasTheTask):
            user.invite(task, target_user, role='teacher')

    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_invite_task_has_no_role(self, mock_relationship):
        user = UserNode()
        target_user = UserNode()
        task = TaskInst()
        with self.assertRaises(NoSuchRole):
            user.invite(task, target_user, role='teacher')

    @patch('neomodel.RelationshipManager.relationship',
           return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.WAITING))
    def test_invite_user_not_accepted(self, mock_relationship):
        user = UserNode()
        target_user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAccept):
            user.invite(task, target_user)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.STANDARD))
    def test_invite_not_admin(self, mock_relationship):
        user = UserNode()
        target_user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAdmin):
            user.invite(task, target_user)

    def test_assert_not_owner_exception(self):
        user = UserNode()
        has_task = HasTask(super_role=SUPER_ROLE.OWNER)
        with self.assertRaises(OwnerCannotChangeInvitation):
            user.assert_not_owner(has_task)

    def test_assert_not_owner_ok(self):
        user = UserNode()
        has_task = HasTask(super_role=SUPER_ROLE.ADMIN)
        user.assert_not_owner(has_task)

    @patch('neomodel.RelationshipManager.is_connected', return_value=True)
    def test_assert_not_have_task_true(self, mock_is_connected):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(AlreadyHasTheTask):
            user.assert_not_have_task(task)

    @patch('neomodel.RelationshipManager.is_connected', return_value=False)
    def test_assert_not_have_task_false(self, mock_is_connected):
        user = UserNode()
        task = TaskInst()
        user.assert_not_have_task(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(acceptance=ACCEPTANCE.WAITING))
    def test_assert_accept_waiting(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAccept):
            user.assert_accept(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(acceptance=ACCEPTANCE.REJECT))
    def test_assert_accept_reject(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAccept):
            user.assert_accept(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(acceptance=ACCEPTANCE.ACCEPT))
    def test_assert_accept_accept(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        user.assert_accept(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN))
    def test_assert_admin_is_not_owner(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotOwner):
            user.assert_owner(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.OWNER))
    def test_assert_owner_is_owner(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        user.assert_owner(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.STANDARD))
    def test_assert_standard_is_not_owner(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotOwner):
            user.assert_owner(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN))
    def test_assert_admin_is_admin(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        user.assert_admin(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.OWNER))
    def test_assert_owner_is_admin(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        user.assert_admin(task)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.STANDARD))
    def test_assert_standard_is_not_admin(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAdmin):
            user.assert_admin(task)
