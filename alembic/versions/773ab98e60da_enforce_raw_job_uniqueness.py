"""enforce raw job uniqueness

Revision ID: 773ab98e60da
Revises: 0f4e8bced38a
Create Date: 2026-09-16 23:27:34.292871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '773ab98e60da'
down_revision: Union[str, Sequence[str], None] = '0f4e8bced38a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DELETE FROM raw_job_postings a
        USING raw_job_postings b
        WHERE a.id > b.id
          AND a.source = b.source
          AND a.source_job_id = b.source_job_id
        """
    )

    op.create_unique_constraint(
        "uq_raw_job_source_job_id",
        "raw_job_postings",
        ["source", "source_job_id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "uq_raw_job_source_job_id",
        "raw_job_postings",
        type_="unique",
    )