from neomodel import StructuredNode, StringProperty, RelationshipTo, db
from relationships import HasTask
from task import TaskInst
from step import StepInst
from taskservice.constants import SUPER_ROLE, ACCEPTANCE, NODE_TYPE
from taskservice.exceptions import NotAdmin, NotAccept, NoSuchRole, AlreadyHasTheTask


class UserNode(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
    tasks = RelationshipTo(TaskInst, HasTask, model=HasTask)

    def assert_admin(self, task):
        has_task = self.tasks.relationship(task)
        if has_task.super_role < SUPER_ROLE.ADMIN:
            raise NotAdmin()

    def assert_accept(self, task):
        has_task = self.tasks.relationship(task)
        if has_task.acceptance != ACCEPTANCE.ACCEPT:
            raise NotAccept()

    def assert_role(self, task, role):
        if role is not None and role not in task.roles:
            raise NoSuchRole(role)

    def assert_not_connected(self, task, user):
        if user.tasks.is_connected(task):
            raise AlreadyHasTheTask()

    @db.transaction
    def invite(self, tid, uid, role=None):
        task = self.tasks.get(tid=tid)
        self.assert_admin(task)
        self.assert_accept(task)
        self.assert_role(task, role)
        user = UserNode.get_or_create({'uid': uid})[0]
        self.assert_not_connected(task, user)
        param = {
            'role': role
        }
        user.tasks.connect(task, param)

    @db.transaction
    def update_task(self, tid, data):
        task = self.tasks.get(tid=tid)
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
