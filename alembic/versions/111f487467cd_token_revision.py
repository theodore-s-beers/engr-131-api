"""token revision

Revision ID: 111f487467cd
Revises: cf1d57285cb1
Create Date: 2025-01-05 18:09:14.211580

"""

from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = "111f487467cd"
down_revision: Union[str, None] = "cf1d57285cb1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
