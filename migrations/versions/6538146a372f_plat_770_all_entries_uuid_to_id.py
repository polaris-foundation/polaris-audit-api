"""PLAT-770-all-entries-uuid-to-id

Revision ID: 6538146a372f
Revises: 575920a9e769
Create Date: 2021-01-15 17:43:04.115930

"""
import time

from alembic import op

# revision identifiers, used by Alembic.

revision = "6538146a372f"
down_revision = "575920a9e769"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    time_start = time.time()

    query = """
    CREATE OR REPLACE FUNCTION all_entries_change_uuid_to_id(event_data jsonb)
    RETURNS jsonb
    LANGUAGE plpgsql
    AS
    $$
        DECLARE
            resulting_json jsonb;
        BEGIN
            resulting_json := event_data;
        
            IF event_data ? 'clinician_uuid' THEN
                resulting_json := resulting_json - 'clinician_uuid' || jsonb_build_object('clinician_id', event_data -> 'clinician_uuid');
            END IF;
        
            IF event_data ? 'device_uuid' THEN
                resulting_json := resulting_json - 'device_uuid' || jsonb_build_object('device_id', event_data -> 'device_uuid');
            END IF;
        
            IF event_data ? 'patient_uuid' THEN
                resulting_json := resulting_json - 'patient_uuid' || jsonb_build_object('patient_id', event_data -> 'patient_uuid');
            END IF;
        
            IF event_data ? 'encounter_uuid' THEN
                resulting_json := resulting_json - 'encounter_uuid' || jsonb_build_object('encounter_id', event_data -> 'encounter_uuid');
            END IF;
        
            IF event_data ? 'epr_encounter_uuid' THEN
                resulting_json := resulting_json - 'epr_encounter_uuid' || jsonb_build_object('epr_encounter_id', event_data -> 'epr_encounter_uuid');
            END IF;
        
            IF event_data ? 'obs_set_uuid' THEN
                resulting_json := resulting_json - 'obs_set_uuid' || jsonb_build_object('obs_set_id', event_data -> 'obs_set_uuid');
            END IF;
        
            RETURN resulting_json;
        END;
    $$;

    UPDATE event
    SET event_data = all_entries_change_uuid_to_id(event_data);
    """

    conn.execute(query)
    print(f"Done in {time.time() - time_start} seconds!")


def downgrade():
    conn = op.get_bind()
    time_start = time.time()

    query = """
        CREATE OR REPLACE FUNCTION all_entries_change_id_to_uuid(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS
        $$
            DECLARE
                resulting_json jsonb;
            BEGIN
                resulting_json := event_data;

                IF event_data ? 'clinician_id' THEN
                    resulting_json := resulting_json - 'clinician_id' || jsonb_build_object('clinician_uuid', event_data -> 'clinician_id');
                END IF;

                IF event_data ? 'device_id' THEN
                    resulting_json := resulting_json - 'device_id' || jsonb_build_object('device_uuid', event_data -> 'device_id');
                END IF;

                IF event_data ? 'patient_id' THEN
                    resulting_json := resulting_json - 'patient_id' || jsonb_build_object('patient_uuid', event_data -> 'patient_id');
                END IF;

                IF event_data ? 'encounter_id' THEN
                    resulting_json := resulting_json - 'encounter_id' || jsonb_build_object('encounter_uuid', event_data -> 'encounter_id');
                END IF;

                IF event_data ? 'epr_encounter_id' THEN
                    resulting_json := resulting_json - 'epr_encounter_id' || jsonb_build_object('epr_encounter_uuid', event_data -> 'epr_encounter_id');
                END IF;

                IF event_data ? 'obs_set_id' THEN
                    resulting_json := resulting_json - 'obs_set_id' || jsonb_build_object('obs_set_uuid', event_data -> 'obs_set_id');
                END IF;

                RETURN resulting_json;
            END;
        $$;

        UPDATE event
        SET event_data = all_entries_change_id_to_uuid(event_data);
        """

    conn.execute(query)
    print(f"Done in {time.time() - time_start}!")
