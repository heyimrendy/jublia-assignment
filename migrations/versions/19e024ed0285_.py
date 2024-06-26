"""empty message

Revision ID: 19e024ed0285
Revises: 
Create Date: 2024-03-24 17:51:13.081591

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '19e024ed0285'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_user_email'), ['email'], unique=True)

    op.create_table('email',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('email_subject', sa.String(length=255), nullable=False),
    sa.Column('email_content', sa.Text(), nullable=False),
    sa.Column('timestamp', sa.BigInteger(), nullable=False),
    sa.Column('sent', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('email', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_email_event_id'), ['event_id'], unique=False)

    op.create_table('user_event_association',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_event_association')
    with op.batch_alter_table('email', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_email_event_id'))

    op.drop_table('email')
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_user_email'))

    op.drop_table('user')
    op.drop_table('event')
    # ### end Alembic commands ###
