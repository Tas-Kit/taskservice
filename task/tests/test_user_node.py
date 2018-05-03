# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, MagicMock
from taskservice.constants import SUPER_ROLE, ACCEPTANCE, NODE_TYPE
from task.models.user_node import UserNode
from task.models.task import TaskInst
from task.models.relationships import HasTask
from taskservice.exceptions import NotAdmin, NotOwner, NotAccept, AlreadyHasTheTask, OwnerCannotChangeInvitation, NoSuchRole
from taskservice.settings.dev import neo4jdb
# Create your tests here.


class TestUserNode(TestCase):

    @classmethod
    def setUpClass(cls):
        neo4jdb.delete_all()

    @classmethod
    def tearDownClass(cls):
        # neo4jdb.delete_all()
        pass

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

    @patch('neomodel.StructuredRel.save')
    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_update_task_success(self, mock_relationship, mock_save):
        user = UserNode()
        task = TaskInst()
        data = {
            'name': 'task name',
            'description': 'task description'
        }
        user.update_task(task, data)
        self.assertEqual(data['name'], task.name)
        self.assertEqual(data['description'], task.description)

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.WAITING))
    def test_update_task_not_accept(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(NotAccept):
            user.update_task(task, {})

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.ACCEPT))
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

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT))
    def test_respond_invitation_owner(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        with self.assertRaises(OwnerCannotChangeInvitation):
            user.respond_invitation(task, ACCEPTANCE.WAITING)

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_owner(self, mock_save):
        mock_owner_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        mock_user_has_task = HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.ACCEPT)
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        user.tasks.relationship = MagicMock(return_value=mock_owner_has_task)
        target_user.tasks.relationship = MagicMock(return_value=mock_user_has_task)
        user.change_invitation(task, target_user, super_role=SUPER_ROLE.OWNER)
        self.assertEqual(SUPER_ROLE.OWNER, mock_user_has_task.super_role)
        self.assertEqual(SUPER_ROLE.ADMIN, mock_owner_has_task.super_role)

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_owner_user_not_accepted(self, mock_save):
        mock_owner_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        mock_user_has_task = HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.WAITING)
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        user.tasks.relationship = MagicMock(return_value=mock_owner_has_task)
        target_user.tasks.relationship = MagicMock(return_value=mock_user_has_task)
        with self.assertRaises(NotAccept):
            user.change_invitation(task, target_user, super_role=SUPER_ROLE.OWNER)

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

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT))
    def test_change_invitation_has_no_role(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        with self.assertRaises(NoSuchRole):
            user.change_invitation(task, target_user, role='teacher')

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_change_invitation_not_owner(self, mock_relationship):
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        with self.assertRaises(NotOwner):
            user.change_invitation(task, target_user)

    @patch('neomodel.RelationshipManager.connect')
    @patch('neomodel.RelationshipManager.is_connected', return_value=False)
    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_invite_success(self, mock_relationship, mock_is_connected, mock_connect):
        user = UserNode()
        target_user = UserNode()
        task = TaskInst(roles=['teacher'])
        user.invite(task, target_user, role='teacher')
        mock_connect.assert_called_once_with(task, {
            'role': 'teacher'
        })

    @patch('neomodel.RelationshipManager.is_connected', return_value=True)
    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_invite_user_already_has_task(self, mock_relationship, mock_is_connected):
        user = UserNode()
        target_user = UserNode()
        task = TaskInst(roles=['teacher'])
        with self.assertRaises(AlreadyHasTheTask):
            user.invite(task, target_user, role='teacher')

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.ACCEPT))
    def test_invite_task_has_no_role(self, mock_relationship):
        user = UserNode()
        target_user = UserNode()
        task = TaskInst()
        with self.assertRaises(NoSuchRole):
            user.invite(task, target_user, role='teacher')

    @patch('neomodel.RelationshipManager.relationship', return_value=HasTask(super_role=SUPER_ROLE.ADMIN, acceptance=ACCEPTANCE.WAITING))
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
