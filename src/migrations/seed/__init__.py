from sqlalchemy import table, column
import sqlalchemy as sa


def get_statuses_table(table_name):
    return table(table_name,
                 column('id', sa.Integer),
                 column('name', sa.String))
