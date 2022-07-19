"""API v2

Revision ID: 26b5dc41edc6
Revises: 92d10925019f
Create Date: 2020-10-21 20:24:05.645188

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision = "26b5dc41edc6"
down_revision = "92d10925019f"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("event", sa.Column("event_data", JSONB, nullable=True))
    op.create_index(
        "ix_event_event_data",
        "event",
        ["event_data"],
        unique=False,
        postgresql_using="gin",
    )
    op.alter_column("event", "type", nullable=False, new_column_name="event_type")
    op.create_index(op.f("ix_event_event_type"), "event", ["event_type"], unique=False)

    query = """
    UPDATE event 
    SET event_data = jsonb_build_object(
        'description', event.description, 
        'source', event.created_by_, 
        'target', event.target
    );
    """
    op.execute(query)

    op.alter_column("event", "event_data", existing_type=sa.JSON(), nullable=False)
    op.drop_column("event", "description")
    op.drop_column("event", "target")


def downgrade():
    op.add_column(
        "event", sa.Column("target", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "event",
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.drop_index(op.f("ix_event_event_type"), table_name="event")
    op.alter_column("event", "event_type", nullable=False, new_column_name="type")

    query = """
    UPDATE event 
    SET target = event.event_data ->> 'target', 
        description = event.event_data ->> 'description';
    """
    op.execute(query)

    op.alter_column("event", "description", existing_type=sa.VARCHAR(), nullable=False)
    op.drop_index("ix_event_event_data", table_name="event")
    op.drop_column("event", "event_data")
