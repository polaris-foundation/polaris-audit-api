from typing import Any, Dict

import pytest

from tests.conftest import CommonValues as Vals


class TestApi:
    def test_fails_with_no_json_body(
        self, client: Any, mock_bearer_validation: Any
    ) -> None:
        response = client.post(
            "/dhos/v2/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    write_scenarios = [
        {
            "id": "test_post",
            "payload": {
                "event_type": Vals.LOGIN_SUCCESS,
                "event_data": {
                    "patient_uuid": Vals.SOMEONE_AWESOME,
                    "clinician_uuid": Vals.SOMEONE_EQUALLY_AWESOME,
                    "reason": Vals.LOGIN_SUCCESS_DESCRIPTION,
                },
            },
            "expected_fields": (
                "uuid",
                "created",
                "created_by",
                "modified",
                "modified_by",
                "event_type",
                "event_data",
            ),
            "expected_pairs": {
                "event_type": Vals.LOGIN_SUCCESS,
                "event_data": {
                    "patient_uuid": Vals.SOMEONE_AWESOME,
                    "clinician_uuid": Vals.SOMEONE_EQUALLY_AWESOME,
                    "reason": Vals.LOGIN_SUCCESS_DESCRIPTION,
                },
            },
        }
    ]

    @pytest.mark.parametrize("scenario", write_scenarios, ids=lambda s: s["id"])
    def test_fields_are_populated_correctly(
        self,
        client: Any,
        mock_bearer_validation: Any,
        scenario: Dict,
    ) -> None:
        post_response = client.post(
            "/dhos/v2/event",
            json=scenario["payload"],
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert post_response.status_code == 201

        get_response = client.get(
            post_response.headers["Location"], headers={"Authorization": "Bearer TOKEN"}
        )
        response_json = get_response.json

        assert len(response_json) == len(scenario["expected_fields"])

        for field in scenario["expected_fields"]:
            assert field in response_json

        for key, value in scenario["expected_pairs"].items():
            if isinstance(response_json[key], dict) and isinstance(value, dict):
                for k, v in value.items():
                    assert response_json[key][k] == v
            else:
                assert response_json[key] == value

    def test_fails_with_no_json_body_v1(
        self, client: Any, mock_bearer_validation: Any
    ) -> None:
        response = client.post(
            "/dhos/v1/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    write_scenarios_v1 = (
        {
            "id": "test_post_event_with_target",
            "payload": {
                "source": Vals.SOMEONE_AWESOME,
                "type": Vals.LOGIN_SUCCESS,
                "description": Vals.LOGIN_SUCCESS_DESCRIPTION,
                "target": Vals.SOMEONE_EQUALLY_AWESOME,
            },
            "expected_fields": (
                "uuid",
                "created",
                "created_by",
                "modified",
                "modified_by",
                "type",
                "description",
                "target",
            ),
            "expected_pairs": {
                "created_by": Vals.SOMEONE_AWESOME,
                "modified_by": Vals.SOMEONE_AWESOME,
                "type": Vals.LOGIN_SUCCESS,
                "description": Vals.LOGIN_SUCCESS_DESCRIPTION,
                "target": Vals.SOMEONE_EQUALLY_AWESOME,
            },
        },
        {
            "id": "test_post_event_without_target",
            "payload": {
                "source": Vals.SOMEONE_AWESOME,
                "type": Vals.LOGIN_SUCCESS,
                "description": Vals.LOGIN_SUCCESS_DESCRIPTION,
            },
            "expected_fields": (
                "uuid",
                "created",
                "created_by",
                "modified",
                "modified_by",
                "type",
                "description",
            ),
            "expected_pairs": {
                "created_by": Vals.SOMEONE_AWESOME,
                "modified_by": Vals.SOMEONE_AWESOME,
                "type": Vals.LOGIN_SUCCESS,
                "description": Vals.LOGIN_SUCCESS_DESCRIPTION,
            },
        },
    )

    @pytest.mark.parametrize("scenario", write_scenarios_v1, ids=lambda s: s["id"])
    def test_fields_are_populated_correctly_v1(
        self,
        client: Any,
        mock_bearer_validation: Any,
        scenario: Dict,
    ) -> None:
        post_response = client.post(
            "/dhos/v1/event",
            json=scenario["payload"],
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert post_response.status_code == 200

        get_response = client.get(
            post_response.headers["Location"], headers={"Authorization": "Bearer TOKEN"}
        )
        response_json = get_response.json

        assert len(response_json) == len(scenario["expected_fields"])

        for field in scenario["expected_fields"]:
            assert field in response_json

        for key, value in scenario["expected_pairs"].items():
            assert response_json[key] == value
