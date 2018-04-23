from neomodel import StructuredNode, StringProperty, RelationshipTo, db
from relations import HasTask
from task import TaskInst
from step import StepInst
from taskservice.constants import SUPER_ROLE, ACCEPTANCE, NODE_TYPE


class UserNode(StructuredNode):
    uid = StringProperty(unique_index=True, required=True)
    tasks = RelationshipTo(TaskInst, HasTask, model=HasTask)

    @db.transaction
    def update_task(self, tid, data):
        task = self.tasks.get(tid=tid)
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
