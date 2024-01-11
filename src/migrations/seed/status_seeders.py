from alembic import op

from src.infrastructure.entity import TodoStatus
from src.infrastructure.entity.todo_list.todo_list_status import TodoListStatus
from src.infrastructure.entity.user.user_status import UserStatus
from src.migrations.seed import get_statuses_table


def seed_todo_statuses():
    todo_statuses_table = get_statuses_table(TodoStatus.table_name())

    op.bulk_insert(todo_statuses_table,
                   [
                       {'id': 1, 'name': 'Open'},
                       {'id': 2, 'name': 'Closed'},
                       {'id': 3, 'name': 'Expired'},
                       {'id': 4, 'name': 'Deleted'}
                   ],
                   multiinsert=False)


def seed_user_statuses():
    user_statuses_table = get_statuses_table(UserStatus.table_name())

    op.bulk_insert(user_statuses_table,
                   [
                       {'id': 1, 'name': 'Enabled'},
                       {'id': 2, 'name': 'Disabled'}
                   ],
                   multiinsert=False)


def seed_todo_list_statuses():
    todo_list_statuses_table = get_statuses_table(TodoListStatus.table_name())

    op.bulk_insert(todo_list_statuses_table,
                   [
                       {'id': 1, 'name': 'Open'},
                       {'id': 2, 'name': 'Closed'},
                       {'id': 3, 'name': 'Deleted'}
                   ],
                   multiinsert=False)
