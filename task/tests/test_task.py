# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from task.models.step import StepInst
from taskservice.settings.dev import neo4jdb
from taskservice.constants import NODE_TYPE
from task.models.task import TaskInst


class DeleteStartEndTestCase(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        self.task = TaskInst(name='test').save()
        self.start = StepInst(
            name='Start',
            node_type=NODE_TYPE.START,
            sid="1").save()
        self.end = StepInst(
            name='End',
            node_type=NODE_TYPE.END,
            sid="2").save()
        self.task.steps.connect(self.start)
        self.task.steps.connect(self.end)
        self.data = self.task.get_graph()
        self.start.delete()
        self.end.delete()
        self.task.delete()

        self.new_task = TaskInst(name='test').save()
        self.new_start = StepInst(
            name='Start', node_type=NODE_TYPE.START, sid="1").save()
        self.new_end = StepInst(
            name='End', node_type=NODE_TYPE.END, sid="2").save()
        self.new_task.steps.connect(self.new_start)
        self.new_task.steps.connect(self.new_end)

    def testGraph(self):
        self.new_task.save_graph(self.data)
        self.assertEqual(
            self.new_task.steps.get_or_none(name="Start").name, "Start")
        self.assertEqual(self.new_task.steps.get_or_none(
            name="End").name, "End")


class SaveGraphTestCase(TestCase):

    def setUp(self):
        neo4jdb.delete_all()
        self.task = TaskInst(name='test').save()
        self.start = StepInst(
            name='Start',
            node_type=NODE_TYPE.START,
            sid="1",
            pos_x="5").save()
        self.end = StepInst(
            name='End',
            node_type=NODE_TYPE.END,
            sid="2").save()
        self.sat = StepInst(name="sat", sid="3").save()
        self.ps = StepInst(name="ps", sid="4").save()
        self.submit = StepInst(name="submit", sid="5").save()

        self.task.steps.connect(self.start)
        self.task.steps.connect(self.end)
        self.task.steps.connect(self.ps)
        self.task.steps.connect(self.submit)
        self.task.steps.connect(self.sat)

        self.start.nexts.connect(self.ps)
        self.ps.nexts.connect(self.submit)
        self.submit.nexts.connect(self.end)
        self.sat.nexts.connect(self.submit)

        self.data = self.task.get_graph()
        self.task.delete()
        self.start.delete()
        self.ps.delete()
        self.sat.delete()
        self.submit.delete()
        self.end.delete()

        self.new_task = TaskInst(name='test').save()
        self.new_start = StepInst(
            name='Start', node_type=NODE_TYPE.START, sid="1").save()
        self.new_end = StepInst(
            name='End', node_type=NODE_TYPE.END, sid="2").save()
        self.deleteNode = StepInst(name="delete", sid="7").save()
        self.new_task.steps.connect(self.new_start)
        self.new_task.steps.connect(self.new_end)
        self.new_task.steps.connect(self.deleteNode)
        self.new_start.nexts.connect(self.deleteNode)

    def testGraph(self):
        self.new_task.save_graph(self.data)
        self.assertEqual(self.new_task.steps.get_or_none(
            name="sat").name, "sat")
        self.assertEqual(self.new_task.steps.get_or_none(
            name="sat").nexts.get_or_none(name="submit").name, "submit")
        self.assertEqual(self.new_task.steps.get_or_none(name="delete"), None)
        self.assertEqual(self.new_task.steps.get_or_none(
            name="submit").nexts.get_or_none(name="End").name, "End")
        self.assertEqual(self.new_task.steps.get_or_none(
            name="Start").nexts.get_or_none(name="ps").name, "ps")
        self.assertEqual(self.new_task.steps.get_or_none(
            name="ps").nexts.get_or_none(name="submit").name, "submit")
        # test update
        self.assertEqual(self.new_task.steps.get_or_none(
            name="Start").pos_x, 5.0)
