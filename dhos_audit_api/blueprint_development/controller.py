from typing import Dict, List

from flask_batteries_included.sqldb import db

from dhos_audit_api.models.event import Event


def reset_database() -> None:
    session = db.session
    session.execute("TRUNCATE TABLE event")
    session.commit()
    session.close()


def seed_data(events_data: List[Dict]) -> None:
    for event_details in events_data:
        db.session.add(Event(**event_details))
        db.session.flush()
    db.session.commit()
