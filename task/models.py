# -*- coding: utf-8 -*-
"""Models for Main."""
from __future__ import unicode_literals

# from django.db import models

# Create your models here.
from neomodel import (
    StructuredNode,
    StructuredRel,
    StringProperty,
    FloatProperty,
    DateTimeProperty,
    ArrayProperty,
    BooleanProperty,
    RelationshipTo,
    RelationshipFrom
)
from taskservice.constants import (
    EFFORT_UNITS,
    STATUS_LIST,
    SUPER_ROLES,
    ACCEPTANCES,
    NODE_TYPE
)


class HasTask(StructuredRel):
    super_role = StringProperty(required=True, choices=SUPER_ROLES)
    role = StringProperty()
    acceptance = StringProperty(default='w', choices=ACCEPTANCES)


class HasStep(StructuredRel):
    node_type = StringProperty(default='n', choices=NODE_TYPE)


class HasChild(StructuredRel):
    value = StringProperty(required=False)


class UserNode(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)


class TaskModel(StructuredNode):
    name = StringProperty(required=True)
    description = StringProperty(required=False)
    expected_effort_num = FloatProperty(index=False, default=0)
    expected_effort_unit = StringProperty(default='h', choices=EFFORT_UNITS)
    deadline = DateTimeProperty(required=False)
    roles = ArrayProperty(StringProperty(), default=[])

    steps = RelationshipTo('StepModel', 'HasStep', model=HasStep)


class TaskInst(TaskModel):
    status = StringProperty(default='n', choices=STATUS_LIST)

    users = RelationshipFrom('UserNode', 'HasTask', model=HasTask)


class StepModel(StructuredNode):
    name = StringProperty(required=True)
    description = StringProperty(required=False)
    is_optional = BooleanProperty(default=False)
    expected_effort_num = FloatProperty(index=False, default=0)
    expected_effort_unit = StringProperty(default='h', choices=EFFORT_UNITS)
    deadline = DateTimeProperty(required=False)
    pos_x = FloatProperty(required=False)
    pos_y = FloatProperty(required=False)
    asignees = ArrayProperty(StringProperty(), default=[])
    reviewers = ArrayProperty(StringProperty(), default=[])

    children = RelationshipTo('StepModel', 'HasChild', model=HasChild)
    parents = RelationshipFrom('StepModel', 'HasChild', model=HasChild)


class StepInst(StepModel):
    status = StringProperty(default='n', choices=STATUS_LIST)
