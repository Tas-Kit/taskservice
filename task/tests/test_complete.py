# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from models.step import StepModel, StepInst

# Create your tests here.

class CreateNodeTestCase(TestCase):
	def setUp(self):
		neo4jdb.delete_all()
		node = StepInst(name="world")
		node.save()
	def testGetNodeName(self):
		node = StepInst.nodes.get(name="world")
		node.submit_for_review()
		self.assertEqual(node.status, 'rr')
		node.delete()


class NodeDependanceCompleteTestCase(TestCase):
	def setUp(self):
		neo4jdb.delete_all()
		node1 = StepInst(name="SAT", status = 'rr').save()
		node2 = StepInst(name="PS", status = 'rr').save()
		node3 = StepInst(name="Submit", status = 'n').save()
		node1.nexts.connect(node3)
		node2.nexts.connect(node3)
		node1.save()
		node2.save()
		node3.save()
	def testSubmit(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submitNode = StepInst.nodes.get(name="Submit")
		self.assertEqual(submitNode.status, 'n')
		sat = StepInst.nodes.get(name="SAT")
		sat.complete()
		submitNode = StepInst.nodes.get(name="Submit")
		self.assertEqual(submitNode.status, 'ip')

class NodeDependanceWithSkipCompleteTestCase(TestCase):
	def sefUp(self):
		neo4jdb.delete_all()
		sat = StepInst(name="SAT", status = 's').save()
		ps = StepInst(name="PS", status = 'rr').save()
		submit = StepInst(name="Submit", status = 'n').save()
		toefl = StepInst(name="TOEFL", status='c').save()
		sat2 = StepInst(name="SAT2", status='c').save()
		sat.nexts.connect(submit)
		ps.nexts.connect(submit)
		sat2.nexts.connect(sat)
		toefl.nexts.connect(sat)
		sat.save()
		ps.save()
		sat2.save()
		toefl.save()
	def testSubmitSuccess(self):
		ps = StepInst.nodes.get(name="PS")
		ps.complete()
		submit = StepInst.nodes.get(name="Submit")
		self.assertEqual(submit.status, 'ip')
