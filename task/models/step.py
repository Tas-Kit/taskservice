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

import utils
from relationships import Next
from taskservice.constants import NODE_TYPE, STATUS, TIME_UNITS, STATUS_LIST, NODE_TYPES
from taskservice.exceptions import CannotComplete
from relationships import HasStep


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
    task = RelationshipFrom('task.models.task.TaskInst', 'HasStep', model=HasStep)


class StepInst(StepModel):
    nexts = RelationshipTo('StepInst', 'Next', model=Next)
    prevs = RelationshipFrom('StepInst', 'Next', model=Next)
    sid = UniqueIdProperty()
    status = StringProperty(default=STATUS.NEW, choices=STATUS_LIST)

    def get_info(self):
        return self.__properties__

    def update(self, data):
        if 'sid' in data:
            del data['sid']
        if 'id' in data:
            del data['id']
        if 'deadline' in data:
            utils.update_datetime(self, 'deadline', data)
        for key in data:
            setattr(self, key, data[key])
        self.save()

    def trigger(self, role=None):
        if self.node_type == NODE_TYPE.START and self.status == STATUS.NEW:
            self.task.get().start()
            self.complete()
        elif self.status == STATUS.IN_PROGRESS and (role in self.assignees or not self.assignees):
            if self.reviewers:
                self.submit_for_review()
            else:
                self.complete()
        elif self.status == STATUS.READY_FOR_REVIEW and (role in self.reviewers or not self.reviewers):
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

    def trigger_next(self):
        for next_node in self.nexts:
            if next_node.status == STATUS.SKIPPED or \
                    next_node.status == STATUS.COMPLETED:
                next_node.trigger_next()
            elif next_node.status == STATUS.NEW and self.check_parents_are_completed(next_node) is True:
                next_node.trigger_self()

    def trigger_self(self):
        if self.node_type == NODE_TYPE.END:
            self.status = STATUS.COMPLETED
            self.task.get().complete()
        else:
            self.status = STATUS.IN_PROGRESS
        self.save()

    def complete(self):
        """complete a step.
        this one will be a little bit tricky since it may involves a lot of cases
        """
        self.status = STATUS.COMPLETED
        self.save()
        self.trigger_next()
