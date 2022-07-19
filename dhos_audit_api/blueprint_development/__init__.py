import time
from typing import Dict, List, Optional

from flask import Blueprint, Response, current_app, jsonify, make_response, request
from flask_batteries_included.helpers.security import protected_route
from flask_batteries_included.helpers.security.endpoint_security import key_present

from .controller import reset_database, seed_data

development_blueprint = Blueprint("dhos/dev", __name__)


@development_blueprint.route("/drop_data", methods=["POST"])
@protected_route(key_present("system_id"))
def drop_data_route() -> Response:

    if current_app.config["ALLOW_DROP_DATA"] is not True:
        raise PermissionError("Cannot drop data in this environment")

    start: float = time.time()
    reset_database()
    total_time: float = time.time() - start

    return jsonify({"complete": True, "time_taken": str(total_time) + "s"})


@development_blueprint.route("/seed_data", methods=["POST"])
@protected_route(key_present("system_id"))
def seed_data_route() -> Response:
    events_data: Optional[List[Dict]] = request.get_json()
    if events_data is None:
        raise ValueError("JSON body is required in request")
    seed_data(events_data=events_data)
    return make_response("", 201)
