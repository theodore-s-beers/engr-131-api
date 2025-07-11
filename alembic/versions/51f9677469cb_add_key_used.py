"""add key used

Revision ID: 51f9677469cb
Revises: 6496ecaa42bb
Create Date: 2025-02-09 10:08:19.846005

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "51f9677469cb"
down_revision: Union[str, None] = "6496ecaa42bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "assignment_submissions", sa.Column("key_used", sa.String(), nullable=True)
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("assignment_submissions", "key_used")
    # ### end Alembic commands ###
