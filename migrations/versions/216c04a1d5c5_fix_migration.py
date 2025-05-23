"""fix migration

Revision ID: 216c04a1d5c5
Revises: 74dcdb0625b6
Create Date: 2025-04-09 21:42:34.755899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '216c04a1d5c5'
down_revision: Union[str, None] = '74dcdb0625b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('file',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('path', sa.String(length=255), nullable=False),
    sa.Column('original_name', sa.String(length=255), nullable=False),
    sa.Column('size', sa.Integer(), nullable=False),
    sa.Column('type', sa.Enum('IMAGE', 'PDF', 'EXCEL', 'PPT', 'WORD', 'HWP', 'OTHER', name='filemodeltype'), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('is_main', sa.Boolean(), nullable=False),
    sa.Column('owner_type', sa.String(length=50), nullable=True),
    sa.Column('owner_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_id'), 'file', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_file_id'), table_name='file')
    op.drop_table('file')
    # ### end Alembic commands ###
