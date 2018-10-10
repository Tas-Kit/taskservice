from neomodel import (
    StructuredNode,
    StringProperty,
    RelationshipFrom,
)

from relationships import HasComponent

class ComponentModel(StructuredNode):
    app = StringProperty(required=True)
    cmp = StringProperty(required=True)
    oid = StringProperty(required=True)
    step = RelationshipFrom('task.models.task.StepInst', 'HasComponent', model=HasComponent)

    def get_info(self):
        info = self.__properties__
        if 'id' in info:
            del info['id']
        return info
