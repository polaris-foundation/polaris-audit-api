import json
import uuid
from typing import Dict

from assertpy import assert_that, soft_assertions


def generate_audit_event_request() -> Dict:
    return {
        "event_type": "activation",
        "event_data": {
            "patient_uuid": str(uuid.uuid4()),
            "clinician_uuid": str(uuid.uuid4()),
            "reason": "a really important event that you cant miss",
        },
    }


def assert_audit_event_body(
    actual_audit_event: dict, expected_audit_event: dict
) -> None:
    with soft_assertions():
        assert_that(actual_audit_event).contains("event_data").has_event_type(
            expected_audit_event["event_type"]
        ).contains("uuid")

        assert_that(actual_audit_event["event_data"]).has_patient_uuid(
            expected_audit_event["event_data"]["patient_uuid"]
        ).has_clinician_uuid(
            expected_audit_event["event_data"]["clinician_uuid"]
        ).has_reason(
            expected_audit_event["event_data"]["reason"]
        )


def assert_v2_event_is_readable_within_v1_api(event_v1: dict, event_v2: dict) -> None:
    with soft_assertions():
        assert_that(event_v1).contains("uuid").contains("type").has_type(
            event_v2["event_type"]
        ).contains("description")

        description_event_data_string = event_v1["description"]
        assert_that(description_event_data_string).is_instance_of(str)
        description_event_data_dict = json.loads(description_event_data_string)
        for key in event_v2["event_data"].keys():
            assert_that(description_event_data_dict).contains(key)


def generate_audit_event_request_v1() -> Dict:  # TODO: PLAT-615
    return {
        "source": str(uuid.uuid1()),
        "target": str(uuid.uuid1()),
        "description": "a really important event",
        "type": "activation",
    }


def assert_audit_event_body_v1(  # TODO: PLAT-615
    actual_audit_event: dict, expected_audit_event: dict
) -> None:
    with soft_assertions():
        assert_that(actual_audit_event).contains("created").has_created_by(
            expected_audit_event["source"]
        ).has_description(expected_audit_event["description"]).contains(
            "modified"
        ).has_modified_by(
            expected_audit_event["source"]
        ).has_target(
            expected_audit_event["target"]
        ).has_type(
            expected_audit_event["type"]
        ).contains(
            "uuid"
        )
