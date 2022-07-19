from behave import then
from behave.runner import Context
from clients.audit_api_client import get_audit_event, get_audit_event_v1
from helpers.audit_helper import (
    assert_audit_event_body,
    assert_audit_event_body_v1,
    assert_v2_event_is_readable_within_v1_api,
)


@then("the audit event is stored")
def assert_audit_event_is_stored(context: Context) -> None:
    response = get_audit_event(
        event_uuid=context.event_uuid,
        jwt=context.system_jwt,
    )
    assert response.status_code == 200
    assert_audit_event_body(
        actual_audit_event=response.json(),
        expected_audit_event=context.audit_event_data,
    )


@then("the audit event is v1 compatible")
def assert_audit_event_v2_is_compatible_with_v1(
    context: Context,
) -> None:  # TODO: PLAT-615
    response = get_audit_event_v1(event_uuid=context.event_uuid, jwt=context.system_jwt)
    assert response.status_code == 200
    assert_v2_event_is_readable_within_v1_api(
        event_v1=response.json(),
        event_v2=context.audit_event_data,
    )


@then("the audit event v1 is stored")
def assert_audit_event_is_stored_v1(context: Context) -> None:  # TODO: PLAT-615
    response = get_audit_event_v1(
        event_uuid=context.event_uuid,
        jwt=context.system_jwt,
    )
    assert response.status_code == 200
    assert_audit_event_body_v1(
        actual_audit_event=response.json(),
        expected_audit_event=context.audit_event_data,
    )
