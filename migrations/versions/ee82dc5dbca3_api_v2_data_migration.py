"""API v2 data migration
https://sensynehealth.atlassian.net/wiki/spaces/SENS/pages/edit-v2/35455151

Revision ID: ee82dc5dbca3
Revises: 26b5dc41edc6
Create Date: 2020-11-04 15:18:08.051086

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "ee82dc5dbca3"
down_revision = "26b5dc41edc6"
branch_labels = None
depends_on = None


def upgrade_previously_downgraded_data(conn: sa.engine.Connection):
    conn.execute(
        """
        CREATE OR REPLACE FUNCTION json_contains_json(exact_json jsonb, json_key text)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        BEGIN
          RETURN (exact_json ->> json_key)::jsonb;
        EXCEPTION WHEN OTHERS THEN
          RETURN NULL;
        END;
        $$;
        
        UPDATE event SET event_data = (event_data ->> 'description')::jsonb 
        WHERE json_contains_json(event_data, 'description') IS NOT NULL;
        """
    )


def upgrade_dhos_activation_auth_api_data(conn: sa.engine.Connection) -> None:
    query = """
        CREATE OR REPLACE FUNCTION create_json_for_send_entry_login_failure(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE 
            matches text[3];
            resulting_json jsonb;
        BEGIN
            IF event_data ->> 'description' ~ 'Failed login attempt using identifier' THEN
                matches := regexp_matches(event_data ->> 'description', 'Failed login attempt using identifier ''(.+?)''(, clinician (.+?) \(clinician contract expired\))?$', 'g');
                IF matches[3] IS NOT NULL THEN
                    resulting_json := jsonb_build_object('send_entry_identifier', matches[1], 'clinician_uuid', matches[3]);
                ELSE
                    resulting_json := jsonb_build_object('send_entry_identifier', matches[1]);
                END IF;
            ELSIF event_data ->> 'description' ~ 'Attempt made to get a JWT for a device that hasn''t been activated' THEN
                matches := regexp_matches(event_data ->> 'description', 'Attempt made to get a JWT for a device that hasn''t been activated: (.+?)''$', 'g');
                resulting_json := jsonb_build_object('device_uuid', matches[1]);
            ELSIF event_data ->> 'description' ~ 'Failed login attempt using device identifier' THEN
                matches := regexp_matches(event_data ->> 'description', 'Failed login attempt using device identifier ''(.+?)''$');
                resulting_json := jsonb_build_object('device_uuid', matches[1]);
            ELSE
                RETURN event_data;
            END IF;                        
            RETURN resulting_json;
        END;
        $$;
        
        CREATE OR REPLACE FUNCTION create_json_for_send_entry_login_success(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE 
            matches text[2];
        BEGIN
            IF event_data ->> 'description' ~ 'Successful login using device identifier' THEN
                RETURN jsonb_build_object('device_uuid', event_data ->> 'target');
            ELSIF event_data ->> 'description' ~ 'Successful login using identifier' THEN
                matches := regexp_matches(event_data ->> 'description', 'Successful login using identifier ''(.+?)'', clinician (.+?)$');
                RETURN jsonb_build_object('clinician_uuid', event_data ->> 'target', 'send_entry_identifier', matches[1]);
            ELSE
                RETURN event_data;
            END IF;
        END;
        $$;
        
        CREATE OR REPLACE FUNCTION create_json_for_send_entry_device_update(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE 
            matches text[3];
            resulting_json jsonb;
        BEGIN
            matches := regexp_matches(event_data ->> 'description', 'device (.+?) updated by (.+?). updated fields: (.+)$', 'g');
            resulting_json := jsonb_build_object('device_uuid', event_data ->> 'target', 'clinician_uuid', matches[2], 'updated_fields', matches[3]);
            RETURN resulting_json;
        END;
        $$;
        
        CREATE OR REPLACE FUNCTION create_json_for_dhos_activation_auth(event_data jsonb, event_type text)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF event_type = 'SEND entry login failure' THEN
                RETURN create_json_for_send_entry_login_failure(event_data);
            ELSIF event_type = 'SEND entry login success' THEN
                RETURN create_json_for_send_entry_login_success(event_data);
            ELSIF event_type = 'SEND entry device update' THEN
                RETURN create_json_for_send_entry_device_update(event_data);
            ELSE
                RETURN event_data;
            END IF;
        END;
        $$;
        
        UPDATE event 
        SET event_data = create_json_for_dhos_activation_auth(event_data, event_type) 
        WHERE event_type IN ('SEND entry login failure', 'SEND entry login success', 'SEND entry device update') AND event_data ->> 'description' IS NOT NULL AND json_contains_json(event_data, 'description') IS NULL;
        """

    conn.execute(query)


def upgrade_gdm_bg_readings_api_data(conn: sa.engine.Connection) -> None:
    q = """
        UPDATE event SET event_data = jsonb_build_object('patient_uuid', event_data ->> 'source', 'duplicate_reading_uuid', event_data ->> 'target')
        WHERE event_type = 'duplicate_reading' AND event_data ->> 'description' IS NOT NULL AND json_contains_json(event_data, 'description') IS NULL;
        """
    conn.execute(q)


def upgrade_dhos_services_api_data(conn: sa.engine.Connection) -> None:
    q = """
    CREATE OR REPLACE FUNCTION create_json_for_login_failure(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE 
            matches text[2];
        BEGIN
            IF event_data ->> 'description' ~ 'Authentication failed, invalid username' THEN
                matches := regexp_matches(event_data ->> 'description', 'Authentication failed, invalid username ''(.+?)''$');
                RETURN jsonb_build_object('username', matches[1]);
            ELSIF event_data ->> 'description' ~ 'account is disabled' THEN
                RETURN jsonb_build_object('clinician_uuid', event_data ->> 'target');
            ELSIF event_data ->> 'description' ~ 'Login expired, contract_expiry_eod_date' THEN
                matches := regexp_matches(event_data ->> 'description', 'Authentication prevented for ''(.+?)''\. Login expired, contract_expiry_eod_date ''(.+?)''$');
                RETURN jsonb_build_object('clinician_uuid', event_data ->> 'target', 'contract_expiry_eod_date', matches[2]);
            ELSIF event_data ->> 'description' ~ 'Authentication failed invalid password for' THEN
                RETURN jsonb_build_object('clinician_uuid', event_data ->> 'target');
            ELSE 
                RETURN event_data;
            END IF;                        
        END;
        $$;
        
    CREATE OR REPLACE FUNCTION create_json_for_diabetes_type_changed(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE 
            matches text[4];
        BEGIN
            matches := regexp_matches(event_data ->> 'description', 'Patient ''(.+?)'' diabetes type changed from (.+?) to (.+?) by clinician ''(.+?)''$', 'g');
            RETURN jsonb_build_object('patient_uuid', event_data ->> 'target', 'clinician_uuid', event_data ->> 'source', 'old_type', matches[2], 'new_type', matches[3]);
        END;
        $$;
        
    CREATE OR REPLACE FUNCTION create_json_for_dhos_services_api(event_data jsonb, event_type text)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF event_type = 'Login Failure' THEN
                RETURN create_json_for_login_failure(event_data);
            ELSIF event_type = 'GDM Patient diabetes type changed' THEN
                RETURN create_json_for_diabetes_type_changed(event_data);
            ELSIF json_contains_json(event_data, 'description') IS NULL THEN
                IF event_type = 'Login Success' THEN
                    RETURN jsonb_build_object('clinician_uuid', event_data ->> 'target');
                ELSIF event_type = 'login activated' THEN
                    RETURN jsonb_build_object('clinician_uuid', event_data ->> 'target', 'modified_by', event_data ->> 'source');
                ELSIF event_type = 'login deactivated' THEN
                    RETURN jsonb_build_object('clinician_uuid', event_data ->> 'target', 'modified_by', event_data ->> 'source');
                ELSIF event_type IN ('Patient information viewed', 'Patient information archived', 'Patient information updated') THEN
                    RETURN jsonb_build_object('patient_uuid', event_data ->> 'target', 'clinician_uuid', event_data ->> 'source');
                ELSE
                    RETURN event_data;
                END IF;
            ELSE
                RETURN event_data;
            END IF;
        END;
        $$;
        
        UPDATE event SET event_data = create_json_for_dhos_services_api(event_data, event_type) WHERE event_type IN ('Login Failure', 'GDM Patient diabetes type changed', 'Login Success', 'login activated', 'login deactivated', 'Patient information viewed', 'Patient information archived', 'Patient information updated') AND event_data ->> 'description' IS NOT NULL AND json_contains_json(event_data, 'description') IS NULL;
        """
    conn.execute(q)


def upgrade_dhos_encounters_api_data(conn: sa.engine.Connection) -> None:
    q = """
    CREATE OR REPLACE FUNCTION create_json_for_spo2_scale_change_failure(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE 
            matches text[2];
        BEGIN
            matches := regexp_matches(event_data ->> 'description', 'encounter ''(.+?)'' spo2 scale change not permitted for user (.+)$');
            RETURN jsonb_build_object('encounter_uuid', event_data ->> 'target', 'epr_encounter_id', matches[1], 'clinician_uuid', matches[2]);
        END;
        $$;
        
    CREATE OR REPLACE FUNCTION create_json_for_score_system_changed(event_data jsonb)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        DECLARE 
            matches text[2];
        BEGIN
            matches := regexp_matches(event_data ->> 'description', 'encounter ''(.+?)'' Score system changed from (.+?) (.+?) to (.+?) (.+?) by (.+?) at (.+)$');
            RETURN jsonb_build_object('encounter_uuid', event_data ->> 'target', 'epr_encounter_id', matches[1], 'previous_score_system', matches[2], 'previous_spo2_scale', matches[3], 'new_score_system', matches[4], 'new_spo2_scale', matches[5], 'clinician_uuid', matches[6], 'modified', matches[7]);
        END;
        $$;    
        
        CREATE OR REPLACE FUNCTION create_json_for_dhos_encounters_api(event_data jsonb, event_type text)
        RETURNS jsonb
        LANGUAGE plpgsql
        AS $$
        BEGIN
            IF event_type = 'spo2_scale_change_failure' THEN
                RETURN create_json_for_spo2_scale_change_failure(event_data);
            ELSIF event_type = 'score_system_changed' THEN
                RETURN create_json_for_score_system_changed(event_data);
            ELSE 
                RETURN event_data;
            END IF;
        END;
        $$;
        
        UPDATE event SET event_data = create_json_for_dhos_encounters_api(event_data, event_type) WHERE event_type IN ('spo2_scale_change_failure', 'score_system_changed') AND event_data ->> 'description' IS NOT NULL AND json_contains_json(event_data, 'description') IS NULL;
        """

    conn.execute(q)


def upgrade():
    conn = op.get_bind()

    upgrade_previously_downgraded_data(conn)
    upgrade_gdm_bg_readings_api_data(conn)
    upgrade_dhos_activation_auth_api_data(conn)
    upgrade_dhos_services_api_data(conn)
    upgrade_dhos_encounters_api_data(conn)


def downgrade():
    # let's just wrap it into {"description": "{...}"}
    op.execute(
        "UPDATE event SET event_data = jsonb_build_object('description', event_data::text);"
    )
