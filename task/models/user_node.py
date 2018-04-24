from neomodel import StructuredNode, StringProperty, RelationshipTo, db
from relationships import HasTask
from task import TaskInst
from step import StepInst
from taskservice.constants import SUPER_ROLE, ACCEPTANCE, NODE_TYPE
from taskservice.exceptions import NotOwner, NotAdmin, NotAccept, AlreadyHasTheTask, OwnerCannotChangeInvitation


class UserNode(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
    tasks = RelationshipTo(TaskInst, 'HasTask', model=HasTask)

    def assert_admin(self, task):
        has_task = self.tasks.relationship(task)
        if has_task.super_role < SUPER_ROLE.ADMIN:
            raise NotAdmin()

    def assert_owner(self, task):
        has_task = self.tasks.relationship(task)
        if has_task.super_role < SUPER_ROLE.OWNER:
            raise NotOwner()

    def assert_accept(self, task):
        has_task = self.tasks.relationship(task)
        if has_task.acceptance != ACCEPTANCE.ACCEPT:
            raise NotAccept()

    def assert_not_have_task(self, task):
        if self.tasks.is_connected(task):
            raise AlreadyHasTheTask()

    def assert_not_owner(self, has_task):
        if has_task.super_role == SUPER_ROLE.OWNER:
            raise OwnerCannotChangeInvitation()

    @db.transaction
    def invite(self, task, user, role=None):
        self.assert_admin(task)
        self.assert_accept(task)
        task.assert_role(role)
        user.assert_not_have_task(task)
        param = {
            'role': role
        }
        user.tasks.connect(task, param)

    @db.transaction
    def change_invitation(self, task, user, role=None, super_role=None):
        self.assert_owner(task)
        task.assert_role(role)
        if super_role == SUPER_ROLE.OWNER:
            user.assert_accept(task)
            self_has_task = self.tasks.relationship(task)
            self_has_task.super_role = SUPER_ROLE.ADMIN
            self_has_task.save()
        has_task = user.tasks.relationship(task)
        has_task.role = role
        if super_role is not None:
            has_task.super_role = super_role
        has_task.save()

    def respond_invitation(self, task, acceptance):
        has_task = self.tasks.relationship(task)
        self.assert_not_owner(has_task)
        has_task.acceptance = acceptance
        has_task.save()

    @db.transaction
    def update_task(self, task, data):
        self.assert_admin(task)
        self.assert_accept(task)
        task.__dict__.update(data)
        return task.save()

    @db.transaction
    def create_task(self, task_name):
        """create task for a user

        Args:
            uid (TYPE): Description

        Returns:
            TYPE: Description
        """
        task = TaskInst(name=task_name).save()
        has_task_param = {
            'super_role': SUPER_ROLE.OWNER,
            'acceptance': ACCEPTANCE.ACCEPT
        }
        self.tasks.connect(task, has_task_param)
        start = StepInst(name='Start', node_type=NODE_TYPE.START).save()
        end = StepInst(name='End', node_type=NODE_TYPE.END).save()
        task.steps.connect(start)
        task.steps.connect(end)
        return task
