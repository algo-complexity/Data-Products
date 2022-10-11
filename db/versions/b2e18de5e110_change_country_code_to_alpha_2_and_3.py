"""change country code to alpha 2 and 3

Revision ID: b2e18de5e110
Revises: 1ebd80d973b9
Create Date: 2022-10-11 10:58:28.432526

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b2e18de5e110"
down_revision = "1ebd80d973b9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("country", sa.Column("alpha2", sa.String(length=2), nullable=False))
    op.add_column("country", sa.Column("alpha3", sa.String(length=3), nullable=False))
    op.drop_column("country", "code")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "country",
        sa.Column("code", sa.VARCHAR(length=3), autoincrement=False, nullable=False),
    )
    op.drop_column("country", "alpha3")
    op.drop_column("country", "alpha2")
    # ### end Alembic commands ###