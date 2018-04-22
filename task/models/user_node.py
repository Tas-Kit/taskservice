from neomodel import StructuredNode, StringProperty, RelationshipTo, db
from relations import HasTask
from task import TaskInst
from step import StepInst


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
            'super_role': 10,
            'acceptance': 'a'
        }
        self.tasks.connect(task, has_task_param)
        start = StepInst(name='Start', node_type='s').save()
        end = StepInst(name='End', node_type='e').save()
        task.steps.connect(start)
        task.steps.connect(end)
        return task
