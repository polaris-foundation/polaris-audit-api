from typing import TypedDict

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask_batteries_included.helpers.apispec import (
    FlaskBatteriesPlugin,
    Identifier,
    initialise_apispec,
    openapi_schema,
)
from marshmallow import EXCLUDE, Schema, fields

dhos_audit_api_spec: APISpec = APISpec(
    version="1.1.0",
    openapi_version="3.0.3",
    title="DHOS Audit API",
    info={
        "description": "The DHOS Audit API is responsible for storing and retrieving audit events."
    },
    plugins=[FlaskPlugin(), MarshmallowPlugin(), FlaskBatteriesPlugin()],
)

initialise_apispec(dhos_audit_api_spec)


@openapi_schema(dhos_audit_api_spec)
class EventSchema(Schema):
    class Meta:
        title = "Event fields common to request and response"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, total=False):
            event_type: str
            event_data: dict

    event_type = fields.String(
        required=True,
        example="Login Success",
        description="The type of the event",
    )
    event_data = fields.Dict(
        required=True,
        example={
            "device_uuid": "4419c048-8094-4fb8-8379-fd122d73e7f7",
            "clinician_uuid": "b277ff62-850b-49a1-be37-4c41da9b5a58",
            "something_really_important": "42",
        },
        description="Arbitrary event JSON data",
        keys=fields.String(),
        values=fields.Raw(),
    )


@openapi_schema(dhos_audit_api_spec)
class EventRequest(EventSchema):
    class Meta:
        title = "Event request v2"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, EventSchema.Meta.Dict, total=False):
            pass


@openapi_schema(dhos_audit_api_spec)
class EventResponse(Identifier, EventSchema):
    class Meta:
        title = "Event response v2"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, EventSchema.Meta.Dict, total=False):
            pass


# TODO: PLAT-615


@openapi_schema(dhos_audit_api_spec)
class EventSchemaV1(Schema):
    class Meta:
        title = "Event fields common to request and response"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, total=False):
            type: str
            description: str
            target: str
            source: str

    type = fields.String(
        required=True,
        example="Login Success",
        description="The type of the event",
    )
    description = fields.String(
        required=True,
        example="Authentication successful for '74780805-0a75-4bc3-99fb-3e3a64986cac'",
        description="The description of the event",
    )
    target = fields.String(
        required=False,
        example="74780805-0a75-4bc3-99fb-3e3a64986cac",
        description="The UUID of the user targeted by the event",
    )
    source = fields.String(
        required=True,
        example="2be8be81-d07a-4dae-8ad7-63cbf5afb8f2",
        description="The UUID of the user who created/modified by the event",
    )


@openapi_schema(dhos_audit_api_spec)
class EventRequestV1(EventSchemaV1):
    class Meta:
        title = "Event request v1"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, EventSchemaV1.Meta.Dict, total=False):
            pass


@openapi_schema(dhos_audit_api_spec)
class EventResponseV1(Identifier, EventSchemaV1):
    class Meta:
        title = "Event response v1"
        unknown = EXCLUDE
        ordered = True

        class Dict(TypedDict, EventSchemaV1.Meta.Dict, total=False):
            pass
