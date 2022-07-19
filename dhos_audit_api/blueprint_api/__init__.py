from typing import Dict, Optional

import flask
from flask import Response
from flask_batteries_included.helpers import schema
from flask_batteries_included.helpers.routes import deprecated_route
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import scopes_present

from dhos_audit_api.blueprint_api import controller
from dhos_audit_api.models.event import Event

api_blueprint = flask.Blueprint("audit", __name__)


@api_blueprint.route("/event/<event_uuid>", methods=["GET"])
@protected_route(scopes_present("read:audit_event"))
def get_event(event_uuid: str) -> Response:
    """---
    get:
      summary: Get event
      description: Get an event by UUID
      tags: [event]
      parameters:
        - name: event_uuid
          in: path
          required: true
          description: The event UUID
          schema:
            type: string
            example: '2126393f-c86b-4bf2-9f68-42bb03a7b68a'
      responses:
        '200':
          description: An event
          content:
            application/json:
              schema: EventResponse
        default:
          description: Error, e.g. 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(controller.get_event(event_uuid))


@api_blueprint.route("/event", methods=["GET"])
@protected_route(scopes_present("read:audit_event"))
def get_events(
    creator: Optional[str] = None,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Response:
    """---
    get:
      summary: Get events by filter
      description: >-
          Get a list of events, filtered by event creator and/or event type
      tags: [event]
      parameters:
        - name: creator
          in: query
          required: false
          description: The UUID of the event creator to filter by
          schema:
            type: string
            example: '2e049188-733d-40f6-8db5-b8ae6f5b2911'
        - name: event_type
          in: query
          required: false
          description: The type of the event to filter by
          schema:
            type: string
            example: 'Login Success'
        - name: start_date
          in: query
          required: false
          description: The start date in YYYY-MM-DD format (inclusive) of the event to filter by
          schema:
            type: string
            example: '2020-06-01'
        - name: end_date
          in: query
          required: false
          description: The end date in YYYY-MM-DD format (inclusive) of the event to filter by
          schema:
            type: string
            example: '2020-06-30'
      responses:
        '200':
          description: A list of events
          content:
            application/json:
              schema:
                type: array
                items: EventResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    schema.get()
    response = controller.get_events(creator, event_type, start_date, end_date)

    return flask.jsonify(response)


@api_blueprint.route("/event", methods=["POST"])
@protected_route(scopes_present("write:audit_event"))
def create_event(event_details: Dict) -> Response:
    """---
    post:
      summary: Create a new event
      description: >-
          Create a new audit event
      tags: [event]
      requestBody:
        description: JSON body containing the event
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EventRequest'
              x-body-name: event_details
      responses:
        '201':
          description: 'New event'
          headers:
            Location:
              description: The location of the created event
              schema:
                type: string
                example: http://localhost/dhos/v1/event/f8d2c136-d2a7-43c4-be9e-3fb882923a58
          content:
            application/json:
              schema: EventResponse
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    schema.post(json_in=event_details, **Event.schema())
    event_uuid: str = controller.create_event(event_details)

    resp: Response = flask.Response(status=201)
    resp.headers["Location"] = f"/dhos/v2/event/{event_uuid}"
    return resp


# TODO: PLAT-615

api_v1_blueprint = flask.Blueprint("audit_v1", __name__)


@deprecated_route(superseded_by="GET /dhos/v2/event/<event_id>")
@api_v1_blueprint.route("/event/<event_id>", methods=["GET"])
@protected_route(scopes_present("read:audit_event"))
def get_event_v1(event_id: str) -> Response:
    """---
    get:
      summary: Get event
      description: Get an event by ID
      tags: [event]
      parameters:
        - name: event_id
          in: path
          required: true
          description: The event ID
          schema:
            type: string
            example: '2126393f-c86b-4bf2-9f68-42bb03a7b68a'
      responses:
        '200':
          description: An event
          content:
            application/json:
              schema: EventResponseV1
        default:
          description: Error, e.g. 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    return flask.jsonify(controller.get_event_v1(event_id))


@deprecated_route(superseded_by="GET /dhos/v2/event")
@api_v1_blueprint.route("/event", methods=["GET"])
@protected_route(scopes_present("read:audit_event"))
def get_events_v1(
    creator: Optional[str] = None,
    type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Response:
    """---
    get:
      summary: Get events by filter
      description: >-
          Get a list of events, filtered by event creator and/or event type
      tags: [event]
      parameters:
        - name: creator
          in: query
          required: false
          description: The UUID of the event creator to filter by
          schema:
            type: string
            example: '2e049188-733d-40f6-8db5-b8ae6f5b2911'
        - name: type
          in: query
          required: false
          description: The type of the event to filter by
          schema:
            type: string
            example: 'Login Success'
        - name: start_date
          in: query
          required: false
          description: The start date in YYYY-MM-DD format (inclusive) of the event to filter by
          schema:
            type: string
            example: '2020-06-01'
        - name: end_date
          in: query
          required: false
          description: The end date in YYYY-MM-DD format (inclusive) of the event to filter by
          schema:
            type: string
            example: '2020-06-30'
      responses:
        '200':
          description: A list of events
          content:
            application/json:
              schema:
                type: array
                items: EventResponseV1
        default:
          description: >-
              Error, e.g. 400 Bad Request, 404 Not Found, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    schema.get()
    response = controller.get_events_v1(creator, type, start_date, end_date)

    return flask.jsonify(response)


@deprecated_route(superseded_by="POST /dhos/v2/event")
@api_v1_blueprint.route("/event", methods=["POST"])
@protected_route(scopes_present("write:audit_event"))
def create_event_v1(event_details: Dict) -> Response:
    """---
    post:
      summary: Create a new event
      description: >-
          Create a new audit event
      tags: [event]
      requestBody:
        description: JSON body containing the event
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/EventRequestV1'
              x-body-name: event_details
      responses:
        '200':
          description: 'New event'
          headers:
            Location:
              description: The location of the created event
              schema:
                type: string
                example: http://localhost/dhos/v1/event/f8d2c136-d2a7-43c4-be9e-3fb882923a58
          content:
            application/json:
              schema: EventResponseV1
        default:
          description: >-
              Error, e.g. 400 Bad Request, 503 Service Unavailable
          content:
            application/json:
              schema: Error
    """
    schema.post(json_in=event_details, **Event.schema_v1())
    _id: str = controller.create_event_v1(event_details)

    resp: Response = flask.make_response()
    resp.headers["Location"] = f"/dhos/v1/event/{_id}"
    return resp
