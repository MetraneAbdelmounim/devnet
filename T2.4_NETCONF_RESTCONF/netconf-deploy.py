#!/usr/bin/env python

import os
import logging
import json
import base64
import ssl
from urllib import request, error

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)

def deploy_restconf(device_name: str, payload: str) -> bool:
    """
    Deploy JSON config to device using RESTCONF.

    Sends payload to:
    /restconf/data/Cisco-IOS-XE-native:native
    """
    scheme = os.environ.get("RESTCONF_SCHEME", "https")
    port = os.environ.get("RESTCONF_PORT", "443")

    host = device_name if port == "443" else f"{device_name}:{port}"
    url = f"{scheme}://{host}/restconf/data/Cisco-IOS-XE-native:native"

    user = os.environ["DEVICE_USERNAME"]
    pwd = os.environ["DEVICE_PASSWORD"]
    token = base64.b64encode(f"{user}:{pwd}".encode("utf-8")).decode("ascii")

    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json",
        "Authorization": f"Basic {token}",
    }

    data = payload.encode("utf-8")

    # Lab devices often use self-signed certs
    ctx = ssl._create_unverified_context()

    # Prefer PATCH (partial config). If not supported, fallback to PUT.
    for method in ("PATCH", "PUT"):
        req = request.Request(url, data=data, headers=headers, method=method)
        try:
            with request.urlopen(req, context=ctx, timeout=90) as resp:
                if resp.status in (200, 201, 204):
                    return True
                logging.error(f"RESTCONF {method} failed with status {resp.status}")
                return False
        except error.HTTPError as e:
            if e.code == 405 and method == "PATCH":
                continue
            logging.exception(f"RESTCONF {method} failed: HTTP {e.code}")
            return False
        except error.URLError:
            logging.exception(f"RESTCONF {method} failed to connect")
            return False

    return False


def process_template(template_name: str) -> bool:
    """Process a JSON template and deploy it to the target device."""
    try:
        with open(f"./device-templates/{template_name}") as fd:
            payload = fd.read()
    except OSError:
        logging.exception(f"Failed to open ./device-templates/{template_name}")
        return False

    # Ensure strict JSON (JSONC with // comments will FAIL here)
    try:
        json.loads(payload)
    except json.JSONDecodeError:
        logging.exception(f"Template {template_name} is not valid JSON")
        return False

    # Template should be named RTR_NAME.json and RTR_NAME must be in DNS
    device_name = template_name.rsplit(".", 1)[0]

    logging.info(f"Deploying template to {device_name}...")
    ok = deploy_restconf(device_name, payload)
    if ok:
        logging.info(f"Successfully deployed config to {device_name}")
        return True

    logging.error(f"Failed to deploy template to {device_name}")
    return False


def main() -> None:
    """Deploy configuration snippets using RESTCONF (JSON templates only)."""
    result = True

    with os.scandir("./device-templates") as pd:
        for entry in pd:
            if entry.is_file() and entry.name.endswith(".json"):
                result &= process_template(entry.name)

    if not result:
        exit(1)


if __name__ == "__main__":
    main()
