"""introduce timezone into datetime of slot

Revision ID: df05f76b5225
Revises: ce19395ed912
Create Date: 2025-08-23 11:01:10.843894

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df05f76b5225'
down_revision: Union[str, Sequence[str], None] = 'ce19395ed912'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: make Slot.datetime timezone-aware."""
    with op.batch_alter_table("slots", schema=None) as batch_op:
        batch_op.alter_column(
            "datetime",
            existing_type=sa.DateTime(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=False,
        )


def downgrade() -> None:
    """Downgrade schema: revert Slot.datetime to naive DateTime."""
    with op.batch_alter_table("slots", schema=None) as batch_op:
        batch_op.alter_column(
            "datetime",
            existing_type=sa.DateTime(timezone=True),
            type_=sa.DateTime(),
            existing_nullable=False,
        )