from behave import given
from behave.runner import Context
from clients.audit_api_client import drop_audit_data
from helpers.jwt import get_system_token


@given("I have a valid JWT")
def get_system_jwt(context: Context) -> None:
    if not hasattr(context, "system_jwt"):
        context.system_jwt = get_system_token()


@given("the database is empty")
def reset_database(context: Context) -> None:
    drop_audit_data(context.system_jwt)
