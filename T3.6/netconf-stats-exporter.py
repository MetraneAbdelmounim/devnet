#!/usr/bin/env python

import os
import time
import yaml
from flask import Flask, Response

from nsexporter import Router, get_interface_counters

app = Flask(__name__)

CONFIG = {}
LAST = {"ts": 0, "data": ""}

CACHE_SECONDS = 15


def load_config():
    global CONFIG
    with open("nse_config.yaml", "r", encoding="utf-8") as f:
        CONFIG = yaml.safe_load(f)


def env_required(name: str) -> str:
    v = os.getenv(name)
    if not v:
        raise RuntimeError(f"Missing required env var: {name}")
    return v


def collect():
    username = env_required("NSE_NETCONF_USERNAME")
    password = env_required("NSE_NETCONF_PASSWORD")
    port = int(CONFIG.get("netconf", {}).get("port", 830))
    timeout = int(CONFIG.get("netconf", {}).get("timeout", 30))

    xpath = CONFIG.get("filter", {}).get("xpath")
    routers = CONFIG.get("routers", [])

    all_rows = []

    for r in routers:
        rows = get_interface_counters(
            router=Router(**r),
            xpath=xpath,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
        )

        # log matched interfaces (helps validate XPath behavior)
        for ifname, in_oct, out_oct in rows:
            all_rows.append((r["name"], ifname, in_oct, out_oct))

    return all_rows


def prom_format(rows):
    # Prometheus text format with metric names matching the task screenshots
    lines = []
    lines.append("# Output / Interface counters")
    lines.append("")

    for router_name, ifname, in_oct, out_oct in rows:
        labels = f'device="{router_name}",instance="{ifname}"'
        lines.append(f'in_octets{{{labels}}} {in_oct}')
        lines.append(f'out_octets{{{labels}}} {out_oct}')

    return "\n".join(lines) + "\n"


# Flask 1.x compatible (Flask 2.x also supports this)
@app.route("/metrics", methods=["GET"])
def metrics():
    now = time.time()
    if now - LAST["ts"] > CACHE_SECONDS:
        LAST["data"] = prom_format(collect())
        LAST["ts"] = now
    return Response(LAST["data"], mimetype="text/plain; version=0.0.4")


def main():
    load_config()
    host = CONFIG.get("prometheus", {}).get("host", "0.0.0.0")
    port = int(CONFIG.get("prometheus", {}).get("port", 8025))
    app.run(host=host, port=port, debug=False)


if __name__ == "__main__":
    main()
