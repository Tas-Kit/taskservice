from task.models.user_node import UserNode


def create():
    u1 = UserNode.get_or_create({'uid': '1'})[0]
    for i in range(4):
        u1.create_task('my {0} task'.format(str(i + 1)))
