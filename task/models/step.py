from neomodel import (
    StructuredNode,
    BooleanProperty,
    FloatProperty,
    StringProperty,
    DateTimeProperty,
    ArrayProperty,
    UniqueIdProperty,
    RelationshipTo,
    RelationshipFrom,
)

from relationships import Next
from taskservice.constants import NODE_TYPE, STATUS, TIME_UNITS, STATUS_LIST, NODE_TYPES
from taskservice.exceptions import CannotComplete


class StepModel(StructuredNode):
    name = StringProperty(required=True)
    description = StringProperty()
    is_optional = BooleanProperty(default=False)
    expected_effort_num = FloatProperty()
    expected_effort_unit = StringProperty(choices=TIME_UNITS)
    deadline = DateTimeProperty()
    pos_x = FloatProperty()
    pos_y = FloatProperty()
    assignees = ArrayProperty(StringProperty(), default=[])
    reviewers = ArrayProperty(StringProperty(), default=[])
    node_type = StringProperty(default=NODE_TYPE.NORMAL, choices=NODE_TYPES)


class StepInst(StepModel):
    nexts = RelationshipTo('StepInst', 'Next', model=Next)
    prevs = RelationshipFrom('StepInst', 'Next', model=Next)
    sid = UniqueIdProperty()
    status = StringProperty(default=STATUS.NEW, choices=STATUS_LIST)

    def submit_for_review(self):
        """change the status to submit for review and save
        """
        self.status = STATUS.READY_FOR_REVIEW
        self.save()

    def check_parents_are_completed(self, node):
        parenstsRelations = node.prevs
        allCompleted = True
        for parent in parenstsRelations:
            parent = StepInst(id=parent.id)
            parent.refresh()

            # if parent is skip, find its grandparents
            if parent.status == STATUS.SKIPPED:
                if self.check_parents_are_completed(parent) is False:
                    allCompleted = False
            elif parent.status != STATUS.COMPLETED:
                allCompleted = False
        return allCompleted

    def trigger_next(self, node):
        for nextNode in node.nexts:
            nextNode = StepInst(id=nextNode.id)
            nextNode.refresh()
            if nextNode.status == STATUS.SKIPPED:
                self.trigger_next(nextNode)
            elif nextNode.status == STATUS.NEW and self.check_parents_are_completed(nextNode) is True:
                nextNode.status = STATUS.IN_PROGRESS
                nextNode.save()

    def complete(self):
        """complete a step.
        this one will be a little bit tricky since it may involves a lot of cases
        """
        if(self.status != STATUS.IN_PROGRESS and self.status != STATUS.READY_FOR_REVIEW):
            raise CannotComplete
        else:
            self.status = STATUS.COMPLETED
            self.save()
            self.trigger_next(self)
