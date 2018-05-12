# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from mock import patch, MagicMock
from task.models.step import StepInst
from taskservice.settings.dev import neo4jdb
from taskservice.constants import STATUS, NODE_TYPE
from taskservice.exceptions import CannotComplete


class TestStep(TestCase):

    @patch('neomodel.StructuredNode.save')
    def test_update(self, mock_save):
        t = '2018-05-12T21:54:43.562037Z'
        data = {
            'id': '123',
            'sid': 'sid123',
            'deadline': t,
            'name': 'new step',
            'description': 'new description'
        }
        step = StepInst()
        step.update(data)
        self.assertEqual('new step', step.name)
        self.assertEqual('new description', step.description)
        self.assertEqual(t, step.deadline.isoformat() + 'Z')
        self.assertNotIn('id', data)
        self.assertNotIn('sid', data)


# Create your tests here.
class TestStepTrigger(TestCase):

    @patch('task.models.step.StepInst.submit_for_review')
    def test_submit_for_review(self, mock_submit_for_review):
        node = StepInst(name='hello')
        node.assignees = ['student']
        node.reviewers = ['teacher']
        node.status = STATUS.IN_PROGRESS
        node.trigger('student')
        mock_submit_for_review.assert_called_once()

    @patch('task.models.step.StepInst.complete')
    def test_no_reviewer(self, mock_complete):
        node = StepInst(name='hello')
        node.assignees = ['student']
        node.status = STATUS.IN_PROGRESS
        node.trigger('student')
        mock_complete.assert_called_once()

    @patch('task.models.step.StepInst.complete')
    def test_trigger_start(self, mock_complete):
        node = StepInst(node_type=NODE_TYPE.START, status=STATUS.NEW)
        mock_task = MagicMock()
        node.task.get = MagicMock(return_value=mock_task)
        node.trigger()
        mock_complete.assert_called_once()
        mock_task.start.assert_called_once()

    @patch('neomodel.StructuredNode.save')
    def test_complete_end(self, mock_save):
        node = StepInst(node_type=NODE_TYPE.END, status=STATUS.NEW)
        mock_task = MagicMock()
        node.task.get = MagicMock(return_value=mock_task)
        node.complete()
        mock_task.complete.assert_called_once()
        self.assertEqual(STATUS.COMPLETED, node.status)

    @patch('task.models.step.StepInst.complete')
    def test_complete(self, mock_complete):
        node = StepInst(name='hello')
        node.assignees = ['student']
        node.reviewers = ['teacher']
        node.status = STATUS.READY_FOR_REVIEW
        node.trigger('teacher')
        mock_complete.assert_called_once()

    def test_status_not_correct(self):
        node = StepInst(name='hello')
        node.assignees = ['student']
        node.reviewers = ['teacher']
        with self.assertRaises(CannotComplete):
            node.trigger('student')

    def test_in_progress_not_assignee(self):
        node = StepInst(name='hello')
        node.reviewers = ['teacher']
        node.status = STATUS.IN_PROGRESS
        with self.assertRaises(CannotComplete):
            node.trigger('student')

    def test_ready_for_review_not_reviewer(self):
        node = StepInst(name='hello')
        node.status = STATUS.READY_FOR_REVIEW
        with self.assertRaises(CannotComplete):
            node.trigger('teacher')


class TestCreateNode(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        node = StepInst(name='world')
        node.save()

    def test_get_node_name(self):
        node = StepInst.nodes.get(name='world')
        node.submit_for_review()
        self.assertEqual(node.status, STATUS.READY_FOR_REVIEW)
        node.delete()


class TestChangeToNew(TestCase):

    def setUp(Self):
        neo4jdb.delete_all()
        node2 = StepInst(name='PS', status=STATUS.READY_FOR_REVIEW).save()
        node3 = StepInst(name='Submit', status=STATUS.NEW).save()
        node2.nexts.connect(node3)

    def test_submit(self):
        ps = StepInst.nodes.get(name='PS')
        ps.complete()
        submit = StepInst.nodes.get(name='Submit')
        self.assertEqual(submit.status, STATUS.IN_PROGRESS)


class TesthangeToReady(TestCase):

    def setUp(Self):
        neo4jdb.delete_all()
        node2 = StepInst(name='PS', status=STATUS.READY_FOR_REVIEW).save()
        node3 = StepInst(name='Submit', status=STATUS.READY_FOR_REVIEW).save()
        node2.nexts.connect(node3)

    def test_submit(self):
        ps = StepInst.nodes.get(name='PS')
        ps.complete()
        submit = StepInst.nodes.get(name='Submit')
        self.assertEqual(submit.status, STATUS.READY_FOR_REVIEW)


class TestThreeToOne(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        node1 = StepInst(name='SAT', status=STATUS.READY_FOR_REVIEW).save()
        node2 = StepInst(name='PS', status=STATUS.READY_FOR_REVIEW).save()
        node3 = StepInst(name='Submit', status=STATUS.NEW).save()
        node4 = StepInst(name='Toefl', status=STATUS.COMPLETED).save()
        node4.nexts.connect(node3)
        node1.nexts.connect(node3)
        node2.nexts.connect(node3)

    def test_submit(self):
        ps = StepInst.nodes.get(name='PS')
        ps.complete()
        submitNode = StepInst.nodes.get(name='Submit')
        self.assertEqual(submitNode.status, STATUS.NEW)
        sat = StepInst.nodes.get(name='SAT')
        sat.complete()
        submitNode = StepInst.nodes.get(name='Submit')
        self.assertEqual(submitNode.status, STATUS.IN_PROGRESS)


class TestTwoToSkipAndTwoToOne(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        sat = StepInst(name='SAT', status=STATUS.SKIPPED).save()
        ps = StepInst(name='PS', status=STATUS.READY_FOR_REVIEW).save()
        submit = StepInst(name='Submit', status=STATUS.NEW).save()
        toefl = StepInst(name='TOEFL', status=STATUS.COMPLETED).save()
        sat2 = StepInst(name='SAT2', status=STATUS.COMPLETED).save()
        sat.nexts.connect(submit)
        ps.nexts.connect(submit)
        sat2.nexts.connect(sat)
        toefl.nexts.connect(sat)

    def test_submit_success(self):
        ps = StepInst.nodes.get(name='PS')
        ps.complete()
        submit = StepInst.nodes.get(name='Submit')
        self.assertEqual(submit.status, STATUS.IN_PROGRESS)


class TestCompleteToSkipAndTwoToOne(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        sat = StepInst(name='SAT', status=STATUS.SKIPPED).save()
        sat2 = StepInst(name='SAT2', status=STATUS.COMPLETED).save()
        ps = StepInst(name='PS', status=STATUS.READY_FOR_REVIEW).save()
        submit = StepInst(name='Submit', status=STATUS.NEW).save()
        sat2.nexts.connect(sat)
        sat.nexts.connect(submit)
        ps.nexts.connect(submit)

    def test_submit_success(self):
        ps = StepInst.nodes.get(name='PS')
        ps.complete()
        submit = StepInst.nodes.get(name='Submit')
        self.assertEqual(submit.status, STATUS.IN_PROGRESS)


class TestReadyToSkipAndTwoToOne(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        sat = StepInst(name='SAT', status=STATUS.SKIPPED).save()
        sat2 = StepInst(name='SAT2', status=STATUS.READY_FOR_REVIEW).save()
        ps = StepInst(name='PS', status=STATUS.READY_FOR_REVIEW).save()
        submit = StepInst(name='Submit', status=STATUS.NEW).save()
        sat2.nexts.connect(sat)
        sat.nexts.connect(submit)
        ps.nexts.connect(submit)

    def test_submit_success(self):
        ps = StepInst.nodes.get(name='PS')
        ps.complete()
        submit = StepInst.nodes.get(name='Submit')
        self.assertEqual(submit.status, STATUS.NEW)


class TestChangeToSkipToNew(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        sat = StepInst(name='SAT', status=STATUS.SKIPPED).save()
        ps = StepInst(name='PS', status=STATUS.READY_FOR_REVIEW).save()
        submit = StepInst(name='Submit', status=STATUS.NEW).save()
        ps.nexts.connect(sat)
        sat.nexts.connect(submit)

    def test_submit_success(self):
        ps = StepInst.nodes.get(name='PS')
        ps.complete()
        submit = StepInst.nodes.get(name='Submit')
        self.assertEqual(submit.status, STATUS.IN_PROGRESS)
