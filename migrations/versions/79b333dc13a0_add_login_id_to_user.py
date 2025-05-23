"""add login_id to user

Revision ID: 79b333dc13a0
Revises: 8a17390c2642
Create Date: 2025-04-08 13:03:28.988841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '79b333dc13a0'
down_revision: Union[str, None] = '8a17390c2642'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('login_id', sa.String(length=50), nullable=True))
    op.add_column('user', sa.Column('phone', sa.String(length=20), nullable=True))
    op.create_unique_constraint(None, 'user', ['login_id'])
    op.create_unique_constraint(None, 'user', ['phone'])
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_constraint(None, 'user', type_='unique')
    op.drop_column('user', 'phone')
    op.drop_column('user', 'login_id')
    # ### end Alembic commands ###
