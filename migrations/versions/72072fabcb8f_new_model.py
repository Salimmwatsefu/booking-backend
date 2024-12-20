"""New model

Revision ID: 72072fabcb8f
Revises: 684e0531eea2
Create Date: 2024-11-20 11:34:38.852374

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72072fabcb8f'
down_revision = '684e0531eea2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('name')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('name', sa.VARCHAR(length=100), nullable=False))

    # ### end Alembic commands ###
