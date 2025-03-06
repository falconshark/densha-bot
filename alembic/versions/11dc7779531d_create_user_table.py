"""create user table

Revision ID: 11dc7779531d
Revises: 
Create Date: 2025-02-27 17:04:29.286654

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '11dc7779531d'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user',
        sa.Column('chat_id', sa.String(50), nullable=False, primary_key=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_table(
        'user_subscription',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('related_user', sa.String(50), nullable=False),
        sa.Column('target_route', sa.String(50), nullable=False),
        sa.Column('last_message', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    pass

def downgrade() -> None:
    op.drop_table('user')
    pass
