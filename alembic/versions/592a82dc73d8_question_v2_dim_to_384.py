"""question v2 dim to 384

Revision ID: 592a82dc73d8
Revises: f1fe6fa2c708
Create Date: 2025-05-29 15:39:13.040059

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import pgvector.sqlalchemy



# revision identifiers, used by Alembic.
revision: str = '592a82dc73d8'
down_revision: Union[str, None] = 'f1fe6fa2c708'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('questions_v2', 'vector',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=768),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=384),
               existing_nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('questions_v2', 'vector',
               existing_type=pgvector.sqlalchemy.vector.VECTOR(dim=384),
               type_=pgvector.sqlalchemy.vector.VECTOR(dim=768),
               existing_nullable=True)
    # ### end Alembic commands ###
