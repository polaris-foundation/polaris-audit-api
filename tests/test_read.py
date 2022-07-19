from datetime import datetime, timedelta
from typing import Any, Dict, Generator, List

import pytest
from flask_batteries_included.sqldb import db

from dhos_audit_api.models.event import Event
from tests.conftest import CommonValues as Vals


class TestRead:
    @pytest.fixture
    def test_events(self) -> Generator[List[Event], None, None]:

        day_before_yesterday: datetime = datetime.now(tz=None) + timedelta(days=-2)
        test_objects: List[Dict] = [
            {
                "uuid": Vals.UUID_1,
                "created_by_": Vals.SOMEONE_AWESOME,
                "modified_by_": Vals.SOMEONE_AWESOME,
                "event_type": Vals.LOGIN_SUCCESS,
                "event_data": {
                    "description": Vals.LOGIN_SUCCESS_DESCRIPTION,
                    "source": Vals.SOMEONE_AWESOME,
                },
            },
            {
                "uuid": Vals.UUID_2,
                "created_by_": Vals.SOMEONE_AWESOME,
                "modified_by_": Vals.SOMEONE_AWESOME,
                "event_type": Vals.LOGIN_FAILURE,
                "event_data": {
                    "description": Vals.LOGIN_FAILURE_DESCRIPTION,
                    "source": Vals.SOMEONE_AWESOME,
                    "target": Vals.SOMEONE_EQUALLY_AWESOME,
                },
            },
            {
                "uuid": Vals.UUID_3,
                "created_by_": Vals.SOMEONE_ELSE,
                "modified_by_": Vals.SOMEONE_ELSE,
                "event_type": Vals.LOGIN_SUCCESS,
                "event_data": {
                    "description": Vals.LOGIN_SUCCESS_DESCRIPTION,
                    "source": Vals.SOMEONE_ELSE,
                },
                "created": day_before_yesterday,
                "modified": day_before_yesterday,
            },
        ]
        models: List[Event] = [Event(**to) for to in test_objects]
        db.session.add_all(models)
        db.session.commit()

        yield models

        for m in models:
            db.session.delete(m)
        db.session.commit()

    def test_request_with_jwt(self, client: Any, mock_bearer_validation: Any) -> None:
        client.get(
            "/dhos/v2/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert mock_bearer_validation.called_once_with("TOKEN")

    def test_fails_with_json_body(
        self, client: Any, mock_bearer_validation: Any
    ) -> None:
        response = client.get(
            "/dhos/v2/event",
            json={"something": 123},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_returns_empty_list(self, client: Any, mock_bearer_validation: Any) -> None:
        response = client.get(
            "/dhos/v2/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

    def test_returns_populated_list(
        self,
        client: Any,
        test_events: List[Event],
        mock_bearer_validation: Any,
    ) -> None:
        response = client.get(
            "/dhos/v2/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == len(test_events)

    def test_filter_by_creator(
        self,
        client: Any,
        test_events: List[Event],
        mock_bearer_validation: Any,
    ) -> None:
        response = client.get(
            f"/dhos/v2/event?creator={Vals.SOMEONE_AWESOME}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        for obj in response.json:
            assert obj["uuid"] in [Vals.UUID_1, Vals.UUID_2]
            assert obj["created_by"] == Vals.SOMEONE_AWESOME
            assert obj["modified_by"] == Vals.SOMEONE_AWESOME

        response = client.get(
            f"/dhos/v2/event?creator={Vals.SOMEONE_ELSE}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_3
        assert obj["created_by"] == Vals.SOMEONE_ELSE
        assert obj["modified_by"] == Vals.SOMEONE_ELSE

    def test_filter_by_type(
        self,
        client: Any,
        test_events: List[Event],
        mock_bearer_validation: Any,
    ) -> None:
        response = client.get(
            f"/dhos/v2/event?event_type={Vals.LOGIN_SUCCESS}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        for obj in response.json:
            assert obj["uuid"] in [Vals.UUID_1, Vals.UUID_3]
            assert obj["event_type"] == Vals.LOGIN_SUCCESS
            assert obj["event_data"]["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

        response = client.get(
            f"/dhos/v2/event?event_type={Vals.LOGIN_FAILURE}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_2
        assert obj["event_type"] == Vals.LOGIN_FAILURE
        assert obj["event_data"]["description"] == Vals.LOGIN_FAILURE_DESCRIPTION
        assert obj["event_data"]["target"] == Vals.SOMEONE_EQUALLY_AWESOME

    def test_filter_by_creator_and_type(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:
        response = client.get(
            f"/dhos/v2/event?creator={Vals.SOMEONE_AWESOME}&event_type={Vals.LOGIN_SUCCESS}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_1
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["event_type"] == Vals.LOGIN_SUCCESS
        assert obj["event_data"]["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

    def test_filter_by_type_and_start_date_(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:

        today = datetime.today().strftime("%Y-%m-%d")
        response = client.get(
            f"/dhos/v2/event?event_type={Vals.LOGIN_SUCCESS}&start_date={today}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_1
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["event_type"] == Vals.LOGIN_SUCCESS
        assert obj["event_data"]["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

    def test_filter_by_type_and_end_date(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:

        yesterday = (datetime.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        response = client.get(
            f"/dhos/v2/event?event_type={Vals.LOGIN_SUCCESS}&end_date={yesterday}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_3
        assert obj["created_by"] == Vals.SOMEONE_ELSE
        assert obj["modified_by"] == Vals.SOMEONE_ELSE
        assert obj["event_type"] == Vals.LOGIN_SUCCESS
        assert obj["event_data"]["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

    def test_filter_by_start_and_end_date(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:

        yesterday = (datetime.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        today = datetime.today().strftime("%Y-%m-%d")
        response = client.get(
            f"/dhos/v2/event?start_date={yesterday}&end_date={today}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_1
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["event_type"] == Vals.LOGIN_SUCCESS
        assert obj["event_data"]["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

        obj = response.json[1]
        assert obj["uuid"] == Vals.UUID_2
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["event_type"] == Vals.LOGIN_FAILURE
        assert obj["event_data"]["description"] == Vals.LOGIN_FAILURE_DESCRIPTION

    def test_get_non_existent(self, client: Any, mock_bearer_validation: Any) -> None:
        response = client.get(
            "/dhos/v1/event/qwerty123",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 404

    def test_request_with_jwt_v1(
        self, client: Any, mock_bearer_validation: Any
    ) -> None:  # TODO: PLAT-615
        client.get(
            "/dhos/v1/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert mock_bearer_validation.called_once_with("TOKEN")

    def test_fails_with_json_body_v1(
        self, client: Any, mock_bearer_validation: Any
    ) -> None:  # TODO: PLAT-615
        response = client.get(
            "/dhos/v1/event",
            json={"something": 123},
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 400

    def test_returns_empty_list_v1(
        self, client: Any, mock_bearer_validation: Any
    ) -> None:  # TODO: PLAT-615
        response = client.get(
            "/dhos/v1/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == 0

    def test_returns_populated_list_v1(
        self,
        client: Any,
        test_events: List[Event],
        mock_bearer_validation: Any,
    ) -> None:  # TODO: PLAT-615
        response = client.get(
            "/dhos/v1/event",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert response.status_code == 200
        assert isinstance(response.json, list)
        assert len(response.json) == len(test_events)

    def test_filter_by_creator_v1(
        self,
        client: Any,
        test_events: List[Event],
        mock_bearer_validation: Any,
    ) -> None:  # TODO: PLAT-615
        response = client.get(
            f"/dhos/v1/event?creator={Vals.SOMEONE_AWESOME}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        for obj in response.json:
            assert obj["uuid"] in [Vals.UUID_1, Vals.UUID_2]
            assert obj["created_by"] == Vals.SOMEONE_AWESOME
            assert obj["modified_by"] == Vals.SOMEONE_AWESOME

        response = client.get(
            f"/dhos/v1/event?creator={Vals.SOMEONE_ELSE}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_3
        assert obj["created_by"] == Vals.SOMEONE_ELSE
        assert obj["modified_by"] == Vals.SOMEONE_ELSE

    def test_filter_by_type_v1(
        self,
        client: Any,
        test_events: List[Event],
        mock_bearer_validation: Any,
    ) -> None:  # TODO: PLAT-615
        response = client.get(
            f"/dhos/v1/event?type={Vals.LOGIN_SUCCESS}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        for obj in response.json:
            assert obj["uuid"] in [Vals.UUID_1, Vals.UUID_3]
            assert obj["type"] == Vals.LOGIN_SUCCESS
            assert obj["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

        response = client.get(
            f"/dhos/v1/event?type={Vals.LOGIN_FAILURE}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_2
        assert obj["type"] == Vals.LOGIN_FAILURE
        assert obj["description"] == Vals.LOGIN_FAILURE_DESCRIPTION
        assert obj["target"] == Vals.SOMEONE_EQUALLY_AWESOME

    def test_filter_by_creator_and_type_v1(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:  # TODO: PLAT-615
        response = client.get(
            f"/dhos/v1/event?creator={Vals.SOMEONE_AWESOME}&type={Vals.LOGIN_SUCCESS}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_1
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["type"] == Vals.LOGIN_SUCCESS
        assert obj["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

    def test_filter_by_type_and_start_date_v1(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:  # TODO: PLAT-615

        today = datetime.today().strftime("%Y-%m-%d")
        response = client.get(
            f"/dhos/v1/event?type={Vals.LOGIN_SUCCESS}&start_date={today}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_1
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["type"] == Vals.LOGIN_SUCCESS
        assert obj["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

    def test_filter_by_type_and_end_date_v1(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:  # TODO: PLAT-615

        yesterday = (datetime.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        response = client.get(
            f"/dhos/v1/event?type={Vals.LOGIN_SUCCESS}&end_date={yesterday}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 1
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_3
        assert obj["created_by"] == Vals.SOMEONE_ELSE
        assert obj["modified_by"] == Vals.SOMEONE_ELSE
        assert obj["type"] == Vals.LOGIN_SUCCESS
        assert obj["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

    def test_filter_by_start_and_end_date_v1(
        self, client: Any, test_events: List[Event], mock_bearer_validation: Any
    ) -> None:  # TODO: PLAT-615

        yesterday = (datetime.today() + timedelta(days=-1)).strftime("%Y-%m-%d")
        today = datetime.today().strftime("%Y-%m-%d")
        response = client.get(
            f"/dhos/v1/event?start_date={yesterday}&end_date={today}",
            headers={"Authorization": "Bearer TOKEN"},
        )
        assert isinstance(response.json, list)
        assert len(response.json) == 2
        obj = response.json[0]
        assert obj["uuid"] == Vals.UUID_1
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["type"] == Vals.LOGIN_SUCCESS
        assert obj["description"] == Vals.LOGIN_SUCCESS_DESCRIPTION

        obj = response.json[1]
        assert obj["uuid"] == Vals.UUID_2
        assert obj["created_by"] == Vals.SOMEONE_AWESOME
        assert obj["modified_by"] == Vals.SOMEONE_AWESOME
        assert obj["type"] == Vals.LOGIN_FAILURE
        assert obj["description"] == Vals.LOGIN_FAILURE_DESCRIPTION
