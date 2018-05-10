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

    def trigger(self, role):
        if self.status == STATUS.IN_PROGRESS and role in self.assignees:
            if self.reviewers:
                self.submit_for_review()
            else:
                self.complete()
        elif self.status == STATUS.READY_FOR_REVIEW and role in self.reviewers:
            self.complete()
        else:
            raise CannotComplete()

    def submit_for_review(self):
        """change the status to submit for review and save
        """
        self.status = STATUS.READY_FOR_REVIEW
        self.save()

    def check_parents_are_completed(self, node):
        parensts_relations = node.prevs
        all_completed = True
        for parent in parensts_relations:
            # if parent is skip, find its grandparents
            if parent.status == STATUS.SKIPPED:
                if self.check_parents_are_completed(parent) is False:
                    all_completed = False
            elif parent.status != STATUS.COMPLETED:
                all_completed = False
        return all_completed

    def trigger_next(self, node):
        for next_node in node.nexts:
            if next_node.status == STATUS.SKIPPED or \
                    next_node.status == STATUS.COMPLETED:
                self.trigger_next(next_node)
            elif next_node.status == STATUS.NEW and self.check_parents_are_completed(next_node) is True:
                next_node.status = STATUS.IN_PROGRESS
                next_node.save()

    def complete(self):
        """complete a step.
        this one will be a little bit tricky since it may involves a lot of cases
        """
        self.status = STATUS.COMPLETED
        self.save()
        self.trigger_next(self)
