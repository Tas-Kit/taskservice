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

    def next(StepModel):
        self.children.connect(StepModel)

    def submit_for_review(self):
        """change the status to submit for review and save
        """
        self.status = 'rr'
        self.save()
        

    def get_all_outgoing_nodes(self,node):
        definition = dict(node_class=StepInst, direction=OUTGOING, relation_type='Next', model=Next)
        relations_traversal = Traversal(node, StepInst.__label__, definition)
        outgoingRelations = relations_traversal.all()
        return outgoingRelations

    def get_all_incoming_nodes(self,node):
        definition = dict(node_class=StepInst, direction=INCOMING, relation_type='Next', model=Next)
        relations_traversal = Traversal(node, StepInst.__label__, definition)
        outgoingRelations = relations_traversal.all()
        return outgoingRelations

    def check_parents_are_completed(self,node):
        parenstsRelations = self.get_all_incoming_nodes(node)
        allCompleted = True
        for parent in parenstsRelations:
            if parent.status != 'c' and parent.status != 's':
                allCompleted = False
            #if parent is skip, find its grandparents
            if parent.status == 's':
                if self.check_parents_are_completed() == False:
                    allCompleted = False
        return allCompleted


    def complete(self):
        """complete a step.
        this one will be a little bit tricky since it may involves a lot of cases
        """
        self.status = 'c'
        self.save()
        #find next node
        outgoingRelations = self.get_all_outgoing_nodes(self)
        for nextNode in outgoingRelations:
            if self.check_parents_are_completed(nextNode) == True:
                nextNode.status = 'ip'
                nextNode.save()

