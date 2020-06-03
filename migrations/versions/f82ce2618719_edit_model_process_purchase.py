"""Edit model Process_Purchase

Revision ID: f82ce2618719
Revises: 16825034de23
Create Date: 2020-06-03 18:51:17.701419

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f82ce2618719'
down_revision = '16825034de23'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('process__purchase', sa.Column('attempt', sa.Integer(), nullable=False))
    op.add_column('process__purchase', sa.Column('fd', sa.String(length=10), nullable=False))
    op.add_column('process__purchase', sa.Column('fdate', sa.String(length=16), nullable=False))
    op.add_column('process__purchase', sa.Column('fn', sa.String(length=16), nullable=False))
    op.add_column('process__purchase', sa.Column('fsum', sa.String(length=10), nullable=False))
    op.add_column('process__purchase', sa.Column('max_attempts', sa.Integer(), nullable=False))
    op.alter_column('process__purchase', 'fp',
               existing_type=mysql.VARCHAR(collation='utf8_bin', length=10),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('process__purchase', 'fp',
               existing_type=mysql.VARCHAR(collation='utf8_bin', length=10),
               nullable=True)
    op.drop_column('process__purchase', 'max_attempts')
    op.drop_column('process__purchase', 'fsum')
    op.drop_column('process__purchase', 'fn')
    op.drop_column('process__purchase', 'fdate')
    op.drop_column('process__purchase', 'fd')
    op.drop_column('process__purchase', 'attempt')
    # ### end Alembic commands ###
