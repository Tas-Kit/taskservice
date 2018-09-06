from neomodel import StructuredNode, StringProperty, RelationshipTo, db
from relationships import HasTask
from task import TaskInst
from step import StepInst
from taskservice.constants import SUPER_ROLE, ACCEPTANCE, NODE_TYPE, START_END_OFFSET, STATUS
from taskservice.exceptions import NotOwner, NotAdmin, NotAccept, AlreadyHasTheTask, OwnerCannotChangeInvitation, BadRequest
from taskservice.services import NOTIFICATIONS

notifications = NOTIFICATIONS()


class UserNode(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
    tasks = RelationshipTo(TaskInst, 'HasTask', model=HasTask)

    def assert_has_higher_permission(self, task, user):
        self_has_task = self.tasks.relationship(task)
        user_has_task = user.tasks.relationship(task)
        if self_has_task.super_role <= user_has_task.super_role:
            raise BadRequest('You do not have enough permission to delete this user')

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

    def assert_has_task(self, task):
        if not self.tasks.is_connected(task):
            raise BadRequest('User has no such task')

    def assert_not_have_task(self, task):
        if self.tasks.is_connected(task):
            raise AlreadyHasTheTask()

    def assert_not_owner(self, has_task):
        if has_task.super_role == SUPER_ROLE.OWNER:
            raise OwnerCannotChangeInvitation()

    def get_todo_list(self):
        query = """MATCH(
                    (user:UserNode{{uid:'{uid}'}})
                    -[:HasTask{{acceptance:'{accept}'}}]->
                    (task:TaskInst{{status:'{in_progress}'}})
                    -[:HasStep]->(step:StepInst)
                )
                WHERE step.status='{in_progress}' OR step.status='{ready_for_review}'
                RETURN task, step"""
        query = query.format(uid=self.uid,
                             in_progress=STATUS.IN_PROGRESS,
                             ready_for_review=STATUS.READY_FOR_REVIEW,
                             accept=ACCEPTANCE.ACCEPT)
        results, meta = db.cypher_query(query)

        todo_list = [{
            'step': StepInst.inflate(step).get_info(),
            'task': TaskInst.inflate(task).get_info(),
            'has_task': self.tasks.relationship(TaskInst.inflate(task)).get_info()
        } for task, step in results]
        return todo_list

    def download(self, task):
        """
        Donwload a task from Tastore
        """
        task.assert_no_user()
        new_task = self.clone_task(task)
        new_task.set_origin(task)
        return new_task

    def upload(self, task, target_task=None):
        """
        Upload a task to Tastore
        :param task: the task to clone
        :param target_task: the task to upgrade
        """
        self.assert_owner(task)
        task.assert_original()
        if target_task is None:
            new_task = task.clone()
        else:
            target_task.upgrade_graph(task)
            new_task = target_task
        return new_task

    def trigger(self, task, sid=None):
        self.assert_accept(task)
        if sid is None:
            step = task.steps.get(node_type=NODE_TYPE.START)
        else:
            step = task.steps.get(sid=sid)
        has_task = self.tasks.relationship(task)
        step.trigger(role=has_task.role)

    @db.transaction
    def invite(self, task, user, super_role=SUPER_ROLE.STANDARD, role=None):
        self.assert_admin(task)
        self.assert_accept(task)
        task.assert_role(role)
        user.assert_not_have_task(task)
        param = {
            'role': role,
            'super_role': super_role
        }
        user.tasks.connect(task, param)
        notifications.invite([user.uid], inviter_id=self.uid, task_id=task.tid)

    def change_super_role(self, task, user, super_role):
        if super_role is not None:
            has_task = user.tasks.relationship(task)
            self.assert_owner(task)
            has_task.super_role = super_role
            if super_role == SUPER_ROLE.OWNER and self.uid != user.uid:
                user.assert_accept(task)
                self_has_task = self.tasks.relationship(task)
                self_has_task.super_role = SUPER_ROLE.ADMIN
                self_has_task.save()
            has_task.save()

    def change_role(self, task, user, role):
        if role is not None:
            self.assert_admin(task)
            has_task = user.tasks.relationship(task)
            task.assert_role(role)
            has_task.role = role
            has_task.save()

    @db.transaction
    def change_invitation(self, task, user, role=None, super_role=None):
        self.change_super_role(task, user, super_role)
        self.change_role(task, user, role)

    def respond_invitation(self, task, acceptance):
        has_task = self.tasks.relationship(task)
        self.assert_not_owner(has_task)
        has_task.acceptance = acceptance
        has_task.save()

    def revoke_invitation(self, task, user):
        self.assert_has_task(task)
        self.assert_accept(task)
        user.assert_has_task(task)
        self.assert_has_higher_permission(task, user)
        user.tasks.disconnect(task)

    def clone_task(self, task, task_info=None):
        task.assert_original()
        new_task = task.clone(task_info)
        has_task_param = {
            'super_role': SUPER_ROLE.OWNER,
            'acceptance': ACCEPTANCE.ACCEPT
        }
        self.tasks.connect(new_task, has_task_param)
        return new_task

    @db.transaction
    def delete_task(self, task):
        self.assert_owner(task)
        task.delete()

    @db.transaction
    def update_task(self, task, task_info):
        self.assert_admin(task)
        self.assert_accept(task)
        task.update(task_info)

    @db.transaction
    def create_task(self, name, task_info=None):
        """create task for a user

        Args:
            uid (TYPE): Description

        Returns:
            TYPE: Description
        """
        task = TaskInst(name=name).save()
        has_task_param = {
            'super_role': SUPER_ROLE.OWNER,
            'acceptance': ACCEPTANCE.ACCEPT
        }
        self.tasks.connect(task, has_task_param)
        start = StepInst(name='Start', node_type=NODE_TYPE.START, pos_x=-START_END_OFFSET).save()
        end = StepInst(name='End', node_type=NODE_TYPE.END, pos_x=START_END_OFFSET).save()
        task.steps.connect(start)
        task.steps.connect(end)
        task.update(task_info)
        return task
