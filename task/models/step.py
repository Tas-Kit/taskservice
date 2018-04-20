from neomodel import (
    StructuredNode,
    BooleanProperty,
    FloatProperty,
    StringProperty,
    DateTimeProperty,
    ArrayProperty,
    RelationshipTo,
    RelationshipFrom
)

from relations import HasChild
from taskservice.constants import EFFORT_UNITS, STATUS_LIST


class StepModel(StructuredNode):
    name = StringProperty(required=True)
    description = StringProperty(required=False)
    is_optional = BooleanProperty(default=False)
    expected_effort_num = FloatProperty(index=False, default=0)
    expected_effort_unit = StringProperty(default='h', choices=EFFORT_UNITS)
    deadline = DateTimeProperty(required=False)
    pos_x = FloatProperty(required=False)
    pos_y = FloatProperty(required=False)
    asignees = ArrayProperty(StringProperty(), default=[])
    reviewers = ArrayProperty(StringProperty(), default=[])

    children = RelationshipTo('StepModel', 'HasChild', model=HasChild)
    parents = RelationshipFrom('StepModel', 'HasChild', model=HasChild)


class StepInst(StepModel):
    status = StringProperty(default='n', choices=STATUS_LIST)

    def submit_for_review(self):
        """change the status to submit for review and save
        """
        pass

    def complete(self):
        """complete a step.
        this one will be a little bit tricky since it may involves a lot of cases
        """
        pass
