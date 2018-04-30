# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from task.models.step import StepModel, StepInst
from taskservice.settings import neo4jdb
from taskservice.constants import NODE_TYPE, STATUS, TIME_UNITS, STATUS_LIST, NODE_TYPES


# Create your tests here.

class CreateNodeTestCase(TestCase):
	def setUp(self):
		neo4jdb.delete_all()
		node = StepInst(name="world")
		node.save()
	def testGetNodeName(self):
		node = StepInst.nodes.get(name="world")
		node.submit_for_review()
		self.assertEqual(node.status, STATUS.READY_FOR_REVIEW)
		node.delete()

class changeToNew(TestCase):
	def setUp(Self):
		neo4jdb.delete_all()
		node2 = StepInst(name="PS", status = STATUS.READY_FOR_REVIEW).save()
		node3 = StepInst(name="Submit", status = STATUS.NEW).save()
		node2.nexts.connect(node3)
	def testSubmit(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submit = StepInst.nodes.get(name="Submit")
		self.assertEqual(submit.status, STATUS.IN_PROGRESS)

class changeToReady(TestCase):
	def setUp(Self):
		neo4jdb.delete_all()
		node2 = StepInst(name="PS", status = STATUS.READY_FOR_REVIEW).save()
		node3 = StepInst(name="Submit", status = STATUS.READY_FOR_REVIEW).save()
		node2.nexts.connect(node3)
	def testSubmit(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submit = StepInst.nodes.get(name="Submit")
		self.assertEqual(submit.status, STATUS.READY_FOR_REVIEW)


class threeToOneTestCase(TestCase):
	def setUp(self):
		neo4jdb.delete_all()
		node1 = StepInst(name="SAT", status = STATUS.READY_FOR_REVIEW).save()
		node2 = StepInst(name="PS", status = STATUS.READY_FOR_REVIEW).save()
		node3 = StepInst(name="Submit", status = STATUS.NEW).save()
		node4 = StepInst(name="Toefl", status = STATUS.COMPLETED).save()
		node4.nexts.connect(node3)
		node1.nexts.connect(node3)
		node2.nexts.connect(node3)
	def testSubmit(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submitNode = StepInst.nodes.get(name="Submit")
		self.assertEqual(submitNode.status, STATUS.NEW)
		sat = StepInst.nodes.get(name="SAT")
		sat.complete()
		submitNode = StepInst.nodes.get(name="Submit")
		self.assertEqual(submitNode.status, STATUS.IN_PROGRESS)

class twoToSkipAndTwoToOneTestCase(TestCase):
	def sefUp(self):
		neo4jdb.delete_all()
		sat = StepInst(name="SAT", status = STATUS.SKIPPED).save()
		ps = StepInst(name="PS", status = STATUS.READY_FOR_REVIEW).save()
		submit = StepInst(name="Submit", status = STATUS.NEW).save()
		toefl = StepInst(name="TOEFL", status=STATUS.COMPLETED).save()
		sat2 = StepInst(name="SAT2", status=STATUS.COMPLETED).save()
		sat.nexts.connect(submit)
		ps.nexts.connect(submit)
		sat2.nexts.connect(sat)
		toefl.nexts.connect(sat)
	def testSubmitSuccess(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submit = StepInst.nodes.get(name="Submit")
		self.assertEqual(submit.status, STATUS.IN_PROGRESS)

class completeToSkipAndTwoToOne(TestCase):
	def setUp(self):
		neo4jdb.delete_all()
		sat = StepInst(name="SAT", status = STATUS.SKIPPED).save()
		sat2 = StepInst(name="SAT2", status=STATUS.COMPLETED).save()
		ps = StepInst(name="PS", status = STATUS.READY_FOR_REVIEW).save()
		submit = StepInst(name="Submit", status = STATUS.NEW).save()
		sat2.nexts.connect(sat)
		sat.nexts.connect(submit)
		ps.nexts.connect(submit)
	def testSubmitSuccess(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submit = StepInst.nodes.get(name="Submit")
		self.assertEqual(submit.status, STATUS.IN_PROGRESS)

class readyToSkipAndTwoToOne(TestCase):
	def setUp(self):
		neo4jdb.delete_all()
		sat = StepInst(name="SAT", status = STATUS.SKIPPED).save()
		sat2 = StepInst(name="SAT2", status=STATUS.READY_FOR_REVIEW).save()
		ps = StepInst(name="PS", status = STATUS.READY_FOR_REVIEW).save()
		submit = StepInst(name="Submit", status = STATUS.NEW).save()
		sat2.nexts.connect(sat)
		sat.nexts.connect(submit)
		ps.nexts.connect(submit)
	def testSubmitSuccess(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submit = StepInst.nodes.get(name="Submit")
		self.assertEqual(submit.status, STATUS.NEW)

class changeToSkipToNew(TestCase):
	def setUp(self):
		neo4jdb.delete_all()
		sat = StepInst(name="SAT", status = STATUS.SKIPPED).save()
		ps = StepInst(name="PS", status = STATUS.READY_FOR_REVIEW).save()
		submit = StepInst(name="Submit", status = STATUS.NEW).save()
		ps.nexts.connect(sat)
		sat.nexts.connect(submit)
	def testSubmitSuccess(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submit = StepInst.nodes.get(name="Submit")
		self.assertEqual(submit.status, STATUS.IN_PROGRESS)		





