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
from taskservice.constants import STATUS, TIME_UNITS, STATUS_LIST, NODE_TYPE
from step import StepInst
from django.contrib.auth.models import User
from taskservice.exceptions import NoSuchRole
from dictdiffer import diff


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

    def clone_graph(self):
        """clone all the step model data and relations

        Returns:
            TYPE: Description
        """
        data = task.get_graph()
        edge_list = data['edges']
        node_dict = data['nodes']
        task_copy = TaskModel(name=self.name + '_copy')
        sid_map = {}
        for key, value in node_dict.iteritems():
            oldSid = value['sid']
            del value['id']
            del value['sid']
            value.status = STATUS.NEW
            value.name = value.name + '_copy'
            node = StepInst(**value)
            task_copy.steps.connect(node)
            sid_map[oldSid] = node.sid
        form_edge(edge_list, sid_map)
        return task_copy

    def form_edge(self, edge_list, sid_map):
        for edge in edge_list:
            incomingNode = self.steps.get_or_none(sid=edge["from"])
            outgoingNode = self.steps.get_or_none(sid=edge["to"])
            if incomingNode is None:
                incomingNode = self.steps.get(sid=sid_map[edge["from"]])
            if outgoingNode is None:
                outgoingNode = self.steps.get(sid=sid_map[edge["to"]])
            incomingNode.nexts.connect(outgoingNode)

    def get_graph(self):
        steps = self.steps
        user_map = {
            user_node.uid: user_node
            for user_node in self.users
        }
        users = {
            str(task_user.id): {
                'basic': {
                    'username': task_user.username,
                    'first_name': task_user.first_name,
                    'last_name': task_user.last_name
                },
                'has_task': self.users.relationship(user_map[str(task_user.id)]).__properties__
            }
            for task_user in User.objects.filter(pk__in=user_map.keys())
        }

        edges = [
            {
                'from': step.sid,
                'to': edge.sid,
                'value': step.nexts.relationship(StepInst(id=edge.id)).value
            }
            for step in steps
            for edge in step.nexts
        ]
        nodes = {
            step.sid: step.__properties__
            for step in steps
        }
        data = {
            'nodes': nodes,
            'edges': edges,
            'users': users
        }
        return data

    def save_graph(self, data):
        """save all the step data

        Args:
            data (TYPE): Description

        Returns:
            TYPE: Description
        """
        edgesList = data["edges"]
        nodeDict = data["nodes"]

        oldData = self.get_graph()
        diffListNodes = list(diff(oldData["nodes"], data["nodes"]))
        sidMap = {}
        # ('change', u'1.pos_x', (None, 5.0))
        for item in diffListNodes:
            changeType = item[0]
            nodeVariable = item[1]
            if changeType == 'change':
                nodeSID, variable = nodeVariable.split(".")
                if variable != "id":
                    continue
                node = self.steps.get_or_none(sid=nodeSID)
                nodeDict[nodeSID]["id"] = node.id
                nodeDict[nodeSID]["sid"] = node.sid
                node = StepInst(**nodeDict[nodeSID]).save()
            elif changeType == 'add':
                nodeDataList = item[2]
                for nodeDataItem in nodeDataList:
                    sid = nodeDataItem[0]
                    nodeData = nodeDataItem[1]
                    del nodeData["id"]
                    del nodeData["sid"]
                    node = StepInst(**nodeData).save()
                    sidMap[sid] = node.sid
                    self.steps.connect(node)
            elif changeType == 'remove':
                nodeDataList = item[2]
                for nodeDataItem in nodeDataList:
                    sid = nodeDataItem[0]
                    node = self.steps.get(sid=sid)
                    if node.node_type == NODE_TYPE.START or node.node_type == NODE_TYPE.END:
                        continue
                    node.delete()
        for node in self.steps:
            node.nexts.disconnect_all()

        for edge in edgesList:
            incomingNode = self.steps.get_or_none(sid=edge["from"])
            outgoingNode = self.steps.get_or_none(sid=edge["to"])
            if incomingNode is None:
                incomingNode = self.steps.get(sid=sidMap[edge["from"]])
            if outgoingNode is None:
                outgoingNode = self.steps.get(sid=sidMap[edge["to"]])
            incomingNode.nexts.connect(outgoingNode)


class TaskInst(TaskModel):

    """Summary

    Attributes:
        status (TYPE): Description
        users (TYPE): Description
    """

    tid = UniqueIdProperty()
    status = StringProperty(default=STATUS.NEW, choices=STATUS_LIST)
    users = RelationshipFrom(
        'task.models.user_node.UserNode', 'HasTask', model=HasTask)
