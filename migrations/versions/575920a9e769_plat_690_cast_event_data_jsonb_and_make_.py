"""PLAT-690 cast event_data -> jsonb and make gin index on it

Revision ID: 575920a9e769
Revises: ee82dc5dbca3
Create Date: 2020-11-24 15:00:55.737758

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "575920a9e769"
down_revision = "ee82dc5dbca3"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        DO $$
        BEGIN
        IF EXISTS(SELECT * FROM information_schema.columns WHERE table_name = 'event' AND column_name = 'event_data' AND data_type = 'json') THEN
        ALTER TABLE event ALTER COLUMN event_data TYPE jsonb USING event_data::jsonb;
        CREATE INDEX ix_event_event_data ON event USING GIN (event_data JSONB_OPS);
        END IF;
        END;
        $$;
        """
    )


def downgrade():
    pass
