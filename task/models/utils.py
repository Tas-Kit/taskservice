from taskservice.exceptions import BadRequest
from taskservice.constants import NODE_TYPE


def assert_start_end(nodes):
    start, end = 0, 0
    for node in nodes:
        if 'node_type' in node:
            if node['node_type'] == NODE_TYPE.START:
                start += 1
            elif node['node_type'] == NODE_TYPE.END:
                end += 1
    if start != 1 or end != 1:
        raise BadRequest('Bad graph. Expect 1 start node and 1 end node in the graph')


def set_diff(s1, s2):
    return s1 - s2, s1 & s2, s2 - s1


def remove_ids(nodes):
    for node in nodes:
        if 'id' in node:
            del node['id']


def get_sid_edge_sets(nodes, edges):
    remove_ids(nodes)
    sid_set = set([node['sid'] for node in nodes])
    edge_set = set([(edge['from'], edge['to']) for edge in edges])
    return sid_set, edge_set


def get_node_edge_map(nodes, edges):
    node_map = {node['sid']: node for node in nodes}
    edge_map = {edge['from'] + '->' + edge['to']: edge for edge in edges}
    return node_map, edge_map
