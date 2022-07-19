import json
from typing import Dict

from flask_batteries_included.sqldb import ModelIdentifier, db
from sqlalchemy.dialects.postgresql import JSONB


class Event(ModelIdentifier, db.Model):
    event_type = db.Column(db.String, nullable=False, unique=False, index=True)
    event_data = db.Column(JSONB, nullable=False, unique=False)

    event_data_index = db.Index(
        "ix_event_event_data", event_data, postgresql_using="gin"
    )

    @staticmethod
    def schema() -> Dict:
        return {
            "required": {"event_type": str, "event_data": dict},
            "updatable": {},
        }

    def to_dict(self) -> Dict:
        return {
            **self.pack_identifier(),
            "event_type": self.event_type,
            "event_data": self.event_data,
        }

    @staticmethod
    def schema_v1() -> Dict:  # TODO: PLAT-615
        return {
            "required": {"type": str, "description": str, "source": str},
            "optional": {"target": str},
            "updatable": {},
        }

    def to_dict_v1(self) -> Dict:  # TODO: PLAT-615
        description = self.event_data.get("description", json.dumps(self.event_data))

        resp = {
            **self.pack_identifier(),
            "type": self.event_type,
            "description": description,
        }

        target = self.event_data.get("target")
        if target is not None:
            resp["target"] = target

        return resp
