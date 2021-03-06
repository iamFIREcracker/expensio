"""Add category table

Revision ID: 33e58258661
Revises: 1ab58533806c
Create Date: 2013-03-10 10:39:33.189815

"""

# revision identifiers, used by Alembic.
revision = '33e58258661'
down_revision = '1ab58533806c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('category',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('user_id', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('foreground', sa.String(), nullable=False),
    sa.Column('background', sa.String(), nullable=False),
    sa.Column('deleted', sa.Boolean(), nullable=False),
    sa.Column('created', sa.DateTime(), nullable=True),
    sa.Column('updated', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('user_id','name', name='user_cname_uc')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('category')
    ### end Alembic commands ###
