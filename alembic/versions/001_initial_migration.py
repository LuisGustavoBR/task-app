from alembic import op
import sqlalchemy as sa

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id',              sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column('name',            sa.String(100),   nullable=False),
        sa.Column('email',           sa.String(255),   nullable=False),
        sa.Column('hashed_password', sa.String(255),   nullable=False),
        sa.Column('created_at',      sa.DateTime(),    nullable=True),
    )
    op.create_index('ix_users_id',    'users', ['id'],    unique=False)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)

    op.create_table(
        'tasks',
        sa.Column('id',          sa.Integer(),     primary_key=True, autoincrement=True),
        sa.Column('title',       sa.String(200),   nullable=False),
        sa.Column('description', sa.Text(),        nullable=True),
        sa.Column('priority',    sa.String(20),    nullable=True, server_default='medium'),
        sa.Column('status',      sa.String(20),    nullable=True, server_default='pending'),
        sa.Column('due_date',    sa.DateTime(),    nullable=True),
        sa.Column('created_at',  sa.DateTime(),    nullable=True),
        sa.Column('updated_at',  sa.DateTime(),    nullable=True),
        sa.Column('user_id',     sa.Integer(),     sa.ForeignKey('users.id'), nullable=False),
    )
    op.create_index('ix_tasks_id', 'tasks', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_tasks_id', table_name='tasks')
    op.drop_table('tasks')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_id',    table_name='users')
    op.drop_table('users')
