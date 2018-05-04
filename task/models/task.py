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
        """get all steps of this task

        Returns:
            TYPE: Description
        """
        return None

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
