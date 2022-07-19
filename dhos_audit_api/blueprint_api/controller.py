from datetime import datetime, timedelta
from typing import Dict, List, Optional

from flask_batteries_included.sqldb import db
from she_logging import logger

from dhos_audit_api.models.event import Event


def get_event(event_uuid: str) -> Dict:
    logger.debug("Getting events with UUID: %s", event_uuid)
    event = Event.query.get_or_404(event_uuid)
    return event.to_dict()


def get_events(
    creator: Optional[str] = None,
    event_type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict]:
    logger.debug(
        "Getting events using filters",
        extra={
            "creator": creator,
            "event_type": event_type,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    query = Event.query

    if creator:
        query = query.filter_by(created_by_=creator)

    if event_type:
        query = query.filter_by(event_type=event_type)

    if start_date:
        from_date: datetime = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Event.modified >= from_date)

    if end_date:
        to_date: datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(Event.modified < to_date)

    objs = query.all()
    return [obj.to_dict() for obj in objs]


def create_event(event: Dict) -> str:
    logger.debug(
        "Creating events",
        extra={"event_type": event["event_type"], "event_data": event["event_data"]},
    )
    obj = Event(
        event_type=event["event_type"],
        event_data=event["event_data"],
    )
    db.session.add(obj)
    db.session.commit()
    return obj.uuid


def get_event_v1(event_uuid: str) -> Dict:  # TODO: PLAT-615
    logger.debug("Getting events V1 with ID: %s", event_uuid)
    event = Event.query.get_or_404(event_uuid)
    return event.to_dict_v1()


def get_events_v1(
    creator: Optional[str] = None,
    type: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> List[Dict]:  # TODO: PLAT-615
    logger.debug(
        "Getting events using filters",
        extra={
            "creator": creator,
            "type": type,
            "start_date": start_date,
            "end_date": end_date,
        },
    )
    query = Event.query

    if creator:
        query = query.filter_by(created_by_=creator)

    if type:
        query = query.filter_by(event_type=type)

    if start_date:
        from_date: datetime = datetime.strptime(start_date, "%Y-%m-%d")
        query = query.filter(Event.modified >= from_date)

    if end_date:
        to_date: datetime = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        query = query.filter(Event.modified < to_date)

    objs = query.all()
    return [obj.to_dict_v1() for obj in objs]


def create_event_v1(event_data: Dict) -> str:  # TODO: PLAT-615
    logger.debug("Creating events V1", extra={"event_data": event_data})
    obj = Event(
        created_by_=event_data["source"],
        modified_by_=event_data["source"],
        event_type=event_data["type"],
        event_data={
            "description": event_data["description"],
            "source": event_data["source"],
            "target": event_data.get("target"),
        },
    )
    db.session.add(obj)
    db.session.commit()
    return obj.uuid
