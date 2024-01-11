"""Initial migration

Revision ID: 0e5f833651fd
Revises: 
Create Date: 2023-01-17 09:35:01.433626+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0e5f833651fd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('todo_status',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=30), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('todo',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('created_date', sa.DateTime(), nullable=False),
    sa.Column('modified_date', sa.DateTime(), nullable=True),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('valid_until', sa.DateTime(), nullable=False),
    sa.Column('user_id', sa.String(length=36), nullable=False),
    sa.Column('status_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['status_id'], ['todo_status.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_todo_valid_until'), ['valid_until'], unique=False)

    from src.migrations.seed.status_seeders import seed_todo_statuses
    seed_todo_statuses()

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('todo', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_todo_valid_until'))

    op.drop_table('todo')
    op.drop_table('todo_status')
    # ### end Alembic commands ###