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
    RelationshipFrom
)
from relationships import HasStep, HasTask
from taskservice.constants import STATUS, TIME_UNITS, STATUS_LIST
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

    def save_graph(self, data):
        """save all the step data

        Args:
            data (TYPE): Description

        Returns:
            TYPE: Description
        """
        return None


class TaskInst(TaskModel):

    """Summary

    Attributes:
        status (TYPE): Description
        users (TYPE): Description
    """

    tid = UniqueIdProperty()
    status = StringProperty(default=STATUS.NEW, choices=STATUS_LIST)
    users = RelationshipFrom('task.models.user_node.UserNode', 'HasTask', model=HasTask)
