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
    OUTGOING,
    INCOMING,
    Traversal
)

from relationships import Next
from taskservice.constants import NODE_TYPE, STATUS, TIME_UNITS, STATUS_LIST, NODE_TYPES


class StepModel(StructuredNode):
    sid = UniqueIdProperty()
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

    nexts = RelationshipTo('StepModel', 'Next', model=Next)
    prevs = RelationshipFrom('StepModel', 'Next', model=Next)


class StepInst(StepModel):
    status = StringProperty(default=STATUS.NEW, choices=STATUS_LIST)
    nexts = RelationshipTo('StepInst', 'Next', model=Next)
    prevs = RelationshipFrom('StepInst', 'Next', model=Next)


    def submit_for_review(self):
        """change the status to submit for review and save
        """
        self.status = STATUS.READY_FOR_REVIEW
        self.save()

    def check_parents_are_completed(self,node):
        parenstsRelations = node.prevs
        allCompleted = True
        for parent in parenstsRelations:
            parent.__class__ = StepInst
            if parent.status != STATUS.COMPLETED and parent.status != STATUS.SKIPPED:
                allCompleted = False
            #if parent is skip, find its grandparents
            if parent.status == STATUS.SKIPPED:
                if self.check_parents_are_completed(parent) == False:
                    allCompleted = False
        return allCompleted
    def trigger_next(self, node):
        for nextNode in node.nexts:
            nextNode.__class__ = StepInst
            print self.check_parents_are_completed(nextNode)
            if nextNode.status == STATUS.SKIPPED:
                trigger_next(nextNode)
            elif nextNode.status == STATUS.NEW and self.check_parents_are_completed(nextNode) == True:
                nextNode.status = STATUS.IN_PROGRESS
                nextNode.save()

    def complete(self):
        """complete a step.
        this one will be a little bit tricky since it may involves a lot of cases
        """
        self.status = STATUS.COMPLETED
        self.save()
        self.trigger_next(self)

