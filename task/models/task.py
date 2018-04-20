"""Summary
"""
from neomodel import (
    StructuredNode,
    StringProperty,
    FloatProperty,
    DateTimeProperty,
    ArrayProperty,
    RelationshipTo,
    RelationshipFrom
)
from relations import HasStep, HasTask
from taskservice.constants import EFFORT_UNITS, STATUS_LIST


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
    description = StringProperty(required=False)
    expected_effort_num = FloatProperty(index=False, default=0)
    expected_effort_unit = StringProperty(default='h', choices=EFFORT_UNITS)
    deadline = DateTimeProperty(required=False)
    roles = ArrayProperty(StringProperty(), default=[])

    steps = RelationshipTo('StepModel', 'HasStep', model=HasStep)

    def get_steps(self):
        """get all steps of this task

        Returns:
            TYPE: Description
        """
        return None

    def save_steps(self, data):
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

    users = RelationshipFrom('UserNode', 'HasTask', model=HasTask)
