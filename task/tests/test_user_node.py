# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, MagicMock
from taskservice.constants import SUPER_ROLE, ACCEPTANCE
import neomodel
from task.models.user_node import UserNode
from task.models.task import TaskInst
from task.models.relationships import HasTask
from taskservice.exceptions import NotAdmin, NotOwner, NotAccept, AlreadyHasTheTask, OwnerCannotChangeInvitation, NoSuchRole
# Create your tests here.


class TestUserNode(TestCase):

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_owner(self, mock_save):
        mock_owner_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        mock_user_has_task = HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.ACCEPT)
        neomodel.RelationshipManager.relationship = MagicMock(side_effect=[mock_owner_has_task, mock_user_has_task, mock_owner_has_task, mock_user_has_task])
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        user.change_invitation(task, target_user, super_role=SUPER_ROLE.OWNER)
        self.assertEqual(SUPER_ROLE.OWNER, mock_user_has_task.super_role)
        self.assertEqual(SUPER_ROLE.ADMIN, mock_owner_has_task.super_role)

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_owner_user_not_accepted(self, mock_save):
        mock_owner_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        mock_user_has_task = HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.WAITING)
        neomodel.RelationshipManager.relationship = MagicMock(side_effect=[mock_owner_has_task, mock_user_has_task, mock_owner_has_task, mock_user_has_task])
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        with self.assertRaises(NotAccept):
            user.change_invitation(task, target_user, super_role=SUPER_ROLE.OWNER)

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_super_role_admin(self, mock_save):
        mock_owner_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        mock_user_has_task = HasTask(super_role=SUPER_ROLE.STANDARD, acceptance=ACCEPTANCE.ACCEPT)
        neomodel.RelationshipManager.relationship = MagicMock(side_effect=[mock_owner_has_task, mock_user_has_task])
        user = UserNode()
        task = TaskInst()
        target_user = UserNode()
        user.change_invitation(task, target_user, super_role=SUPER_ROLE.ADMIN)
        self.assertEqual(SUPER_ROLE.ADMIN, mock_user_has_task.super_role)
        self.assertEqual(SUPER_ROLE.OWNER, mock_owner_has_task.super_role)

    @patch('neomodel.StructuredRel.save')
    def test_change_invitation_change_role(self, mock_save):
        mock_has_task = HasTask(super_role=SUPER_ROLE.OWNER, acceptance=ACCEPTANCE.ACCEPT)
        neomodel.RelationshipManager.relationship = MagicMock(return_value=mock_has_task)
        user = UserNode()
        task = TaskInst(roles=['teacher'])
        target_user = UserNode()
        user.change_invitation(task, target_user, role='teacher')
        self.assertEqual('teacher', mock_has_task.role)
        self.assertEqual(SUPER_ROLE.OWNER, mock_has_task.super_role)

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
