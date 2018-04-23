from neomodel import StructuredRel, StringProperty, IntegerProperty
from taskservice.constants import SUPER_ROLE, SUPER_ROLES, ACCEPTANCES, ACCEPTANCE


class HasTask(StructuredRel):
    super_role = IntegerProperty(default=SUPER_ROLE.STANDARD, choices=SUPER_ROLES)
    role = StringProperty()
    acceptance = StringProperty(default=ACCEPTANCE.WAITING, choices=ACCEPTANCES)


class HasStep(StructuredRel):
    pass


class Next(StructuredRel):
    value = StringProperty(required=False)
