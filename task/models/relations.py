from neomodel import StructuredRel, StringProperty, IntegerProperty
from taskservice.constants import SUPER_ROLES, ACCEPTANCES


class HasTask(StructuredRel):
    super_role = IntegerProperty(required=True, choices=SUPER_ROLES)
    role = StringProperty()
    acceptance = StringProperty(default='w', choices=ACCEPTANCES)


class HasStep(StructuredRel):
    pass


class Next(StructuredRel):
    value = StringProperty(required=False)
