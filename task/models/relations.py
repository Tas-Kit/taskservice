from neomodel import StructuredRel, StringProperty
from taskservice.constants import SUPER_ROLES, ACCEPTANCES, NODE_TYPE


class HasTask(StructuredRel):
    super_role = StringProperty(required=True, choices=SUPER_ROLES)
    role = StringProperty()
    acceptance = StringProperty(default='w', choices=ACCEPTANCES)


class HasStep(StructuredRel):
    node_type = StringProperty(default='n', choices=NODE_TYPE)


class HasChild(StructuredRel):
    value = StringProperty(required=False)
