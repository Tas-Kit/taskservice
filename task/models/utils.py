from datetime import datetime
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


def update_datetime(obj, key, task_info):
    time = task_info[key]
    if type(time) is str or type(time) is unicode:
        time = datetime.strptime(time, '%Y-%m-%dT%H:%M:%S.%fZ')
    setattr(obj, key, time)
    del task_info[key]


def set_diff(s1, s2):
    s1, s2 = set(s1), set(s2)
    return s1 - s2, s1 & s2, s2 - s1


def remove_ids(nodes):
    for node in nodes:
        if 'id' in node:
            del node['id']


def get_sid_edge_sets(nodes, edges):
    remove_ids(nodes)
    sids = [node['sid'] for node in nodes]
    edges = [(edge['from'], edge['to']) for edge in edges]
    return sids, edges


def get_node_edge_map(nodes, edges):
    node_map = {node['sid']: node for node in nodes}
    edge_map = {edge['from'] + '->' + edge['to']: edge for edge in edges}
    return node_map, edge_map
