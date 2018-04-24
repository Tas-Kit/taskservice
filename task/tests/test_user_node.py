# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from mock import patch
from taskservice.constants import SUPER_ROLE, ACCEPTANCE
from task.models.user_node import UserNode
from task.models.task import TaskInst
from task.models.relationships import HasTask
from taskservice.exceptions import NotAdmin, NotOwner, NotAccept
# from neomodel import RelationshipManager
# Create your tests here.


class TestUserNode(TestCase):

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
