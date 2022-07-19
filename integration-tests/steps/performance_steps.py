import random
import time
import uuid
from typing import Dict, List

from behave import given, step, then, when
from behave.runner import Context
from clients import audit_api_client


@given("{number_rows:d} rows with {event_data_keys} keys")
def seed_db(
    context: Context,
    number_rows: int,
    event_data_keys: str,
) -> None:
    chunk = []
    for i in range(number_rows):
        randomly_chosen_keys: List[str] = list(event_data_keys.split(","))
        random.shuffle(randomly_chosen_keys)
        randomly_chosen_keys = randomly_chosen_keys[
            : random.randint(1, len(randomly_chosen_keys) - 1)
        ]
        event = {
            "event_type": "Performance Test Event",
            "event_data": {key: str(uuid.uuid4()) for key in randomly_chosen_keys},
        }
        chunk.append(event)

        if len(chunk) == 500 or i == number_rows - 1:
            response = audit_api_client.post_audit_event_bulk(
                audit_event_data=chunk, jwt=context.system_jwt
            )
            assert response.status_code == 201
            chunk.clear()


@when("timing this step")
def timing_step(context: Context) -> None:
    context.start_time = time.time()


@step("database is upgraded to revision {revision_to}")
def upgrade_db(context: Context, revision_to: str) -> None:
    output = audit_api_client.run_on_dhos_audit(f"flask db upgrade {revision_to}")
    assert "Done" in output, f"Upgrade failed: {output}"
    assert "exception" not in output.lower(), f"Exception occurred: {output}"


@step("database is downgraded to revision {revision_to}")
def downgrade_db(context: Context, revision_to: str) -> None:
    output = audit_api_client.run_on_dhos_audit(f"flask db downgrade {revision_to}")
    assert "Done" in output, f"Downgrade failed: {output}"
    assert "exception" not in output.lower(), f"Exception occurred: {output}"


@then("it takes less than {seconds} seconds to complete")
def takes_less_than(context: Context, seconds: str) -> None:
    limit = float(seconds)
    end_time = time.time()
    diff = end_time - context.start_time
    assert (
        diff < limit
    ), f"Max time for the test exceeded {limit} seconds - it took {diff} seconds"


@step("all entries keys have changed from {old_keys} to {new_keys}")
def keys_have_changed(context: Context, old_keys: str, new_keys: str) -> None:
    new_keys_list: List[str] = new_keys.split(",")
    old_keys_list: List[str] = old_keys.split(",")

    response = audit_api_client.get_audit_events(jwt=context.system_jwt)
    assert response.status_code == 200
    events: List[Dict] = response.json()
    for event in events:
        for key in event["event_data"].keys():
            assert key not in old_keys_list, event["event_data"]
            assert key in new_keys_list, event["event_data"]
