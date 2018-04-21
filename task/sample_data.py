from task.models.user_node import UserNode


def main():
    u1 = UserNode.get_or_create({'uid': '123'})[0]
    u1.create_task('my first task')

if __name__ == '__main__':
    main()
