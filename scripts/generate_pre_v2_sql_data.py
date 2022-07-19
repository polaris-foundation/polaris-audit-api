import datetime
import random
import uuid
from pathlib import Path

import click

ROW_TEMPLATE = (
    "{uuid}	{created}	{modified}	{modified_by_}	{created_by_}	{event_type}	{event_data}"
)

COPY_CONFIG = """
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;
"""

EVENT_TEMPLATES = (
    (
        "Login Success",
        """{{"description": "Authentication successful for '{target}'", "source": "{source}", "target": "{target}"}}""",
    ),
    (
        "Login Failure",
        """{{"description": "Authentication failed invalid password for '{target}'", "source": "{source}", "target": "{target}"}}""",
    ),
    (
        "GDM Patient diabetes type changed",
        """{{"description": "Patient '{target}' diabetes type changed from {random_int} to {random_int} by clinician '{source}'", "source": "{source}", "target": "{target}"}}""",
    ),
    (
        "SEND entry login success",
        """{{"description": "Successful login using identifier '{random_id}', clinician {target}", "source": "{source}", "target": "{target}"}}""",
    ),
    (
        "SEND entry login failure",
        """{{"description": "Failed login attempt using identifier '{random_id}', clinician {random_id} (clinician contract expired)", "source": "{source}", "target": ""}}""",
    ),
    (
        "Patient information viewed",
        """{{"description": "Patient '{target}' information viewed by clinician '{source}'", "source": "{source}", "target": "{target}"}}""",
    ),
    (
        "score_system_changed",
        """{{"description": "encounter '{random_id}' Score system changed from {random_id} {random_int} to {random_id} {random_int} by {source} at {random_time}", "source": "{source}", "target": "{target}"}}""",
    ),
)


@click.command()
@click.option(
    "-t",
    "--table",
    default="public.event",
    help="Target 'schema.table'",
    type=click.STRING,
)
@click.option(
    "-n",
    "--number",
    default=200000,
    help="Number of records to generate",
    type=click.INT,
)
def generate(table: str, number: int):
    copy_statement = f"COPY {table} (uuid, created, modified, modified_by_, created_by_, event_type, event_data) FROM stdin;"

    rows = []
    for i in range(number):
        target = uuid.uuid4()
        source = uuid.uuid4()
        random_id = uuid.uuid4()
        random_int = random.randint(1, 1000000)
        random_time = (
            datetime.datetime.utcnow()
            - datetime.timedelta(seconds=random.randint(1, 10000000))
        ).isoformat()
        event = random.choice(EVENT_TEMPLATES)
        event_type = event[0]
        event_data = event[1].format(
            target=target,
            source=source,
            random_id=random_id,
            random_int=random_int,
            random_time=random_time,
        )
        row = ROW_TEMPLATE.format(
            uuid=uuid.uuid4(),
            created=random_time,
            modified=random_time,
            modified_by_=source,
            created_by_=source,
            event_type=event_type,
            event_data=event_data,
        )
        rows.append(row)

    fp = Path(__file__).parent.parent / f"{datetime.datetime.utcnow().isoformat()}.sql"
    with fp.open("w+") as f:
        f.write(COPY_CONFIG + "\n")
        f.write(copy_statement + "\n")
        for row in rows:
            f.write(row + "\n")
        f.write("\\.\n")

    print("Done!")


if __name__ == "__main__":
    generate()
