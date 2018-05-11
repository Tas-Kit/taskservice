"""Summary
"""
from neomodel import (
    StructuredNode,
    StringProperty,
    FloatProperty,
    DateTimeProperty,
    ArrayProperty,
    UniqueIdProperty,
    RelationshipTo,
    RelationshipFrom,
    db
)
from relationships import HasStep, HasTask
from taskservice.constants import STATUS, TIME_UNITS, STATUS_LIST
import utils
from step import StepInst
from taskservice.exceptions import NoSuchRole
from django.contrib.auth.models import User


class TaskModel(StructuredNode):

    """Summary

    Attributes:
        deadline (TYPE): Description
        description (TYPE): Description
        expected_effort_num (TYPE): Description
        expected_effort_unit (TYPE): Description
        name (TYPE): Description
        roles (TYPE): Description
        steps (TYPE): Description
    """

    name = StringProperty(required=True)
    description = StringProperty()
    expected_effort_num = FloatProperty()
    expected_effort_unit = StringProperty(choices=TIME_UNITS)
    deadline = DateTimeProperty()
    roles = ArrayProperty(StringProperty(), default=[])

    steps = RelationshipTo(StepInst, 'HasStep', model=HasStep)

    def assert_role(self, role):
        if role is not None and role not in self.roles:
            raise NoSuchRole(role)

    def start(self):
        self.status = STATUS.IN_PROGRESS
        self.save()

    def complete(self):
        self.status = STATUS.COMPLETED
        self.save()

    def get_graph(self):
        steps = self.steps
        user_map = {
            user_node.uid: user_node
            for user_node in self.users
        }
        users = [
            {
                'basic': {
                    'username': task_user.username,
                    'first_name': task_user.first_name,
                    'last_name': task_user.last_name
                },
                'has_task': self.users.relationship(user_map[str(task_user.id)]).__properties__
            }
            for task_user in User.objects.filter(pk__in=user_map.keys())
        ]

        edges = [
            {
                'from': step.sid,
                'to': edge.sid,
                'value': step.nexts.relationship(StepInst(id=edge.id)).value
            }
            for step in steps
            for edge in step.nexts
        ]
        nodes = [step.__properties__ for step in steps]
        data = {
            'nodes': nodes,
            'edges': edges,
            'users': users
        }
        return data

    def clone_graph(self):
        """clone all the step model data and relations

        Returns:
            TYPE: Description
        """
        return None

    def remove_edges(self, edges):
        for from_sid, to_sid in edges:
            self.steps.get(sid=from_sid).nexts.disconnect(self.steps.get(sid=to_sid))

    def remove_nodes(self, sids):
        for sid in sids:
            node = self.steps.get(sid=sid)
            node.delete()

    def change_edges(self, edges, edge_map):
        for from_sid, to_sid in edges:
            from_node = self.steps.get(sid=from_sid)
            to_node = self.steps.get(sid=to_sid)
            edge = from_node.nexts.relationship(to_node)
            edge_data = edge_map[from_sid + '->' + to_sid]
            if 'value' in edge_data:
                edge.value = edge_data['value']
                edge.save()

    def change_nodes(self, sids, node_map):
        for sid in sids:
            node = self.steps.get(sid=sid)
            node.update(node_map[sid])

    def add_nodes(self, sids, node_map):
        sid_map = {}
        for sid in sids:
            node = StepInst()
            node.update(node_map[sid])
            self.steps.connect(node)
            sid_map[sid] = node.sid
        return sid_map

    def add_edges(self, edges, sid_map):
        for from_sid, to_sid in edges:
            if from_sid in sid_map:
                from_sid = sid_map[from_sid]
            if to_sid in sid_map:
                to_sid = sid_map[to_sid]
            from_node = self.steps.get(sid=from_sid)
            to_node = self.steps.get(sid=to_sid)
            from_node.nexts.connect(to_node)

    def update_step_roles(self, roles):
        roles = set(roles)
        for step in self.steps.all():
            reviewers = set(step.reviewers)
            step.reviewers = list(reviewers - roles)
            assignees = set(step.assignees)
            step.assignees = list(assignees - roles)
            step.save()

    def update_user_roles(self, roles):
        for user in self.users.all():
            has_task = user.has_task.relationship(self)
            if has_task.role in roles:
                has_task.role = None
                has_task.save()

    def update_roles(self, old_roles):
        _, _, remove_roles = utils.set_diff(self.roles, old_roles)
        self.update_step_roles(remove_roles)
        self.update_user_roles(remove_roles)

    def update(self, task_info):
        if task_info:
            if 'id' in task_info:
                del task_info['id']
            if 'tid' in task_info:
                del task_info['tid']
            old_roles = self.roles
            for key in task_info:
                setattr(self, key, task_info[key])
            self.update_roles(old_roles)
            self.save()

    @db.transaction
    def save_graph(self, nodes, edges, task_info=None):
        """save all the step data

        Args:
            data (TYPE): Description

        Returns:
            TYPE: Description
        """
        utils.assert_start_end(nodes)
        new_sids, new_edges = utils.get_sid_edge_sets(nodes, edges)
        data = self.get_graph()
        old_sids, old_edges = utils.get_sid_edge_sets(data['nodes'], data['edges'])

        add_edges, change_edges, remove_edges = utils.set_diff(new_edges, old_edges)
        add_sids, change_sids, remove_sids = utils.set_diff(new_sids, old_sids)

        node_map, edge_map = utils.get_node_edge_map(nodes, edges)

        self.remove_edges(remove_edges)
        self.remove_nodes(remove_sids)
        self.change_edges(change_edges, edge_map)
        self.change_nodes(change_sids, node_map)
        sid_map = self.add_nodes(add_sids, node_map)
        self.add_edges(add_edges, sid_map)
        self.update(task_info)


class TaskInst(TaskModel):

    """Summary

    Attributes:
        status (TYPE): Description
        users (TYPE): Description
    """

    tid = UniqueIdProperty()
    status = StringProperty(default=STATUS.NEW, choices=STATUS_LIST)
    users = RelationshipFrom('task.models.user_node.UserNode', 'HasTask', model=HasTask)
