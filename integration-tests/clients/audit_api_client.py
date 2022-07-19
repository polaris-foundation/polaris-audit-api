from subprocess import PIPE, STDOUT, Popen
from typing import IO, Dict, List, Optional

import requests
from environs import Env
from requests import Response

base_url = Env().str("DHOS_AUDIT_BASE_URL", "http://dhos-audit-api:5000")


def drop_audit_data(jwt: str) -> Response:
    response = requests.post(
        f"{base_url}/drop_data",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )
    return response


def post_audit_event_bulk(audit_event_data: List[Dict], jwt: str) -> Response:
    response = requests.post(
        f"{base_url}/seed_data",
        headers={"Authorization": f"Bearer {jwt}"},
        json=audit_event_data,
        timeout=15,
    )
    return response


def post_audit_event(audit_event_data: Dict, jwt: str) -> Response:
    response = requests.post(
        f"{base_url}/dhos/v2/event",
        headers={"Authorization": f"Bearer {jwt}"},
        json=audit_event_data,
        timeout=15,
    )
    return response


def get_audit_event(event_uuid: str, jwt: str) -> Response:
    response = requests.get(
        f"{base_url}/dhos/v2/event/{event_uuid}",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )
    return response


def get_audit_events(
    jwt: str, event_type: Optional[str] = None, creator_uuid: Optional[str] = None
) -> Response:
    params = {}

    if event_type:
        params["event_type"] = event_type
    if creator_uuid:
        params["creator_uuid"] = creator_uuid

    response = requests.get(
        f"{base_url}/dhos/v2/event",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=60,
        params=params,
    )
    return response


def post_audit_event_v1(audit_event_data: Dict, jwt: str) -> Response:  # TODO: PLAT-615
    response = requests.post(
        f"{base_url}/dhos/v1/event",
        headers={"Authorization": f"Bearer {jwt}"},
        json=audit_event_data,
        timeout=15,
    )
    return response


def get_audit_event_v1(event_uuid: str, jwt: str) -> Response:  # TODO: PLAT-615
    response = requests.get(
        f"{base_url}/dhos/v1/event/{event_uuid}",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
    )
    return response


def get_audit_events_v1(
    jwt: str, event_type: Optional[str] = None, creator_uuid: Optional[str] = None
) -> Response:  # TODO: PLAT-615
    params = {}

    if event_type:
        params["event_type"] = event_type
    if creator_uuid:
        params["creator_uuid"] = creator_uuid

    response = requests.get(
        f"{base_url}/dhos/v1/event",
        headers={"Authorization": f"Bearer {jwt}"},
        timeout=15,
        params=params,
    )
    return response


def run_on_dhos_audit(cmd: str) -> str:
    ssh_cmd = """sshpass -p app ssh -o StrictHostKeyChecking=no -l app dhos-audit-api"""
    proc = Popen(
        ssh_cmd, shell=True, bufsize=40960, stdin=PIPE, stdout=PIPE, stderr=STDOUT
    )
    stdin: Optional[IO[bytes]] = proc.stdin
    stdout: Optional[IO[bytes]] = proc.stdout
    assert stdin is not None and stdout is not None

    stdin.write(
        (
            "&&".join(
                [
                    "cd /app",
                    "set -o allexport",
                    ". ./local.env",
                    cmd,
                ]
            )
            + "; exit"
        ).encode("utf-8")
    )
    stdin.close()
    proc.wait()
    output = stdout.read().decode("utf-8")
    return output
