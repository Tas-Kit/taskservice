from neomodel import (
    StructuredNode,
    BooleanProperty,
    FloatProperty,
    StringProperty,
    DateTimeProperty,
    ArrayProperty,
    UniqueIdProperty,
    RelationshipTo,
    RelationshipFrom
)

from relations import Next
from taskservice.constants import EFFORT_UNITS, STATUS_LIST, NODE_TYPE


class StepModel(StructuredNode):
    sid = UniqueIdProperty()
    name = StringProperty(required=True)
    description = StringProperty()
    is_optional = BooleanProperty(default=False)
    expected_effort_num = FloatProperty()
    expected_effort_unit = StringProperty(choices=EFFORT_UNITS)
    deadline = DateTimeProperty()
    pos_x = FloatProperty()
    pos_y = FloatProperty()
    assignees = ArrayProperty(StringProperty(), default=[])
    reviewers = ArrayProperty(StringProperty(), default=[])
    node_type = StringProperty(default='n', choices=NODE_TYPE)

    nexts = RelationshipTo('StepModel', 'Next', model=Next)
    prevs = RelationshipFrom('StepModel', 'Next', model=Next)


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
