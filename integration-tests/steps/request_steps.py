from behave import when
from behave.runner import Context
from clients.audit_api_client import post_audit_event, post_audit_event_v1
from helpers.audit_helper import (
    generate_audit_event_request,
    generate_audit_event_request_v1,
)


@when("an audit event is received")
def request_create_audit_event(context: Context) -> None:
    context.audit_event_data = generate_audit_event_request()
    context.post_audit_event_response = post_audit_event(
        audit_event_data=context.audit_event_data,
        jwt=context.system_jwt,
    )
    assert context.post_audit_event_response.status_code == 201
    context.event_uuid = context.post_audit_event_response.headers["Location"].split(
        "/"
    )[-1]


@when("an audit event v1 is received")
def request_create_audit_event_v1(context: Context) -> None:  # TODO: PLAT-615
    context.audit_event_data = generate_audit_event_request_v1()
    context.post_audit_event_response = post_audit_event_v1(
        audit_event_data=context.audit_event_data,
        jwt=context.system_jwt,
    )
    assert context.post_audit_event_response.status_code == 200
    context.event_uuid = context.post_audit_event_response.headers["Location"].split(
        "/"
    )[-1]
