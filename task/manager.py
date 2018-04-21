from task.models.task import TaskInst
from task.models.user_node import UserNode
from neomodel import db


class TaskManager(object):

    """try to cache all the tasks and steps
    """
