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
from relations import HasStep, HasTask
from taskservice.constants import EFFORT_UNITS, STATUS_LIST
from step import StepModel
# from user_node import UserNode


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

    tid = UniqueIdProperty()
    name = StringProperty(required=True)
    description = StringProperty(required=False)
    expected_effort_num = FloatProperty(index=False, default=0)
    expected_effort_unit = StringProperty(default='h', choices=EFFORT_UNITS)
    deadline = DateTimeProperty(required=False)
    roles = ArrayProperty(StringProperty(), default=[])

    steps = RelationshipTo(StepModel, 'HasStep', model=HasStep)

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

    status = StringProperty(default='n', choices=STATUS_LIST)

    users = RelationshipFrom('task.models.user_node.UserNode', 'HasTask', model=HasTask)
