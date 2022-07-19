from pathlib import Path

import connexion
from connexion import FlaskApp
from flask import Flask
from flask_batteries_included import augment_app as fbi_augment_app
from flask_batteries_included.config import is_not_production_environment
from flask_batteries_included.sqldb import db, init_db

from dhos_audit_api import config
from dhos_audit_api.blueprint_api import api_blueprint, api_v1_blueprint
from dhos_audit_api.blueprint_development import development_blueprint
from dhos_audit_api.helpers.cli import add_cli_command


def create_app(
    testing: bool = False, use_pgsql: bool = True, use_sqlite: bool = False
) -> Flask:
    openapi_dir: Path = Path(__file__).parent / "openapi"
    connexion_app: FlaskApp = connexion.App(
        __name__,
        specification_dir=openapi_dir,
        options={"swagger_ui": is_not_production_environment()},
    )
    connexion_app.add_api("openapi.yaml", strict_validation=True)

    # Create a Flask app.
    app: Flask = fbi_augment_app(
        app=connexion_app.app,
        use_auth0=True,
        use_pgsql=use_pgsql,
        testing=testing,
        use_sqlite=use_sqlite,
    )
    config.apply_config(app)

    # Register the API blueprint.
    app.register_blueprint(api_v1_blueprint, url_prefix="/dhos/v1")  # TODO: PLAT-615
    app.register_blueprint(api_blueprint, url_prefix="/dhos/v2")
    app.logger.info("Registered API blueprint")

    # Configure the SQL database.
    init_db(app=app, testing=testing)

    # Development blueprint registration
    if is_not_production_environment():
        app.register_blueprint(development_blueprint)
        app.logger.info("Registered development blueprint")

    if testing:
        with app.app_context():
            db.create_all()

    add_cli_command(app)

    # Done!
    app.logger.info("App ready to serve requests")

    return app
