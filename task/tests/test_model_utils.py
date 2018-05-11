# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from task.models import utils
from taskservice.exceptions import BadRequest
from taskservice.constants import NODE_TYPE


class Test_Model_Utils(TestCase):

    def setUp(self):
        self.nodes = [
            {
                'id': '123',
                'name': 'node1',
                'sid': 'sid123'
            },
            {
                'id': '321',
                'name': 'node2',
                'sid': 'sid321'
            }
        ]
        self.edges = [
            {
                'from': 'sid123',
                'to': 'sid321',
                'value': 'values'
            }
        ]

    def test_assert_start_end_no_start(self):
        nodes = [{
            'node_type': NODE_TYPE.END
        }]
        with self.assertRaises(BadRequest):
            utils.assert_start_end(nodes)

    def test_assert_start_end_two_start(self):
        nodes = [{
            'node_type': NODE_TYPE.START
        }, {
            'node_type': NODE_TYPE.START
        }, {
            'node_type': NODE_TYPE.END
        }]
        with self.assertRaises(BadRequest):
            utils.assert_start_end(nodes)

    def test_assert_start_end_ok(self):
        nodes = [{
            'node_type': NODE_TYPE.START
        }, {
            'node_type': NODE_TYPE.END
        }]
        utils.assert_start_end(nodes)

    def test_set_diff(self):
        s1 = set([1, 2, 3])
        s2 = set([2, 3, 4])
        add, change, remove = utils.set_diff(s1, s2)
        self.assertEqual(set([1]), add)
        self.assertEqual(set([2, 3]), change)
        self.assertEqual(set([4]), remove)

    def test_remove_ids(self):
        utils.remove_ids(self.nodes)
        self.assertEqual([{
            'name': 'node1',
            'sid': 'sid123'
        },
            {
            'name': 'node2',
            'sid': 'sid321'
        }], self.nodes)

    def test_get_sid_edge_sets(self):
        sids, edges = utils.get_sid_edge_sets(self.nodes, self.edges)
        self.assertEqual(['sid123', 'sid321'], sids)
        self.assertEqual([('sid123', 'sid321')], edges)

    def test_get_edge_map(self):
        node_map, edge_map = utils.get_node_edge_map(self.nodes, self.edges)
        self.assertEqual({
            'sid123': self.nodes[0],
            'sid321': self.nodes[1]
        }, node_map)
        self.assertEqual({
            'sid123->sid321': self.edges[0]
        }, edge_map)
