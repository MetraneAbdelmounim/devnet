#!/usr/bin/env python

import os
from dataclasses import dataclass
from typing import Dict, List, Tuple

from lxml import etree
from ncclient import manager

OC_IF_NS = "http://openconfig.net/yang/interfaces"
NSMAP = {"oc-if": OC_IF_NS}


@dataclass
class Router:
    name: str
    host: str


def _bool_env(name: str, default: bool) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in ("1", "true", "yes", "y", "on")


def get_interface_counters(
    router: Router,
    xpath: str,
    port: int,
    username: str,
    password: str,
    timeout: int = 30,
) -> List[Tuple[str, int, int]]:
    """
    Returns list of (ifname, in_octets, out_octets) that are present in the NETCONF reply.
    """

    verify_hostkey = _bool_env("NSE_VERIFY_HOSTKEY", False)

    with manager.connect(
        host=router.host,
        port=port,
        username=username,
        password=password,
        hostkey_verify=verify_hostkey,
        allow_agent=False,
        look_for_keys=False,
        timeout=timeout,
    ) as m:

        # XPath filter. Some servers require prefixes; we use oc-if prefix.
        # ncclient sends: <filter type="xpath" select="..."/>
        reply = m.get(filter=("xpath", xpath))

        xml = etree.fromstring(str(reply).encode("utf-8"))

        # Find interface blocks in OpenConfig namespace
        if_elems = xml.xpath("//oc-if:interfaces/oc-if:interface", namespaces=NSMAP)

        results: List[Tuple[str, int, int]] = []

        for iface in if_elems:
            name = iface.findtext("oc-if:name", namespaces=NSMAP)
            in_oct = iface.findtext(
                "oc-if:state/oc-if:counters/oc-if:in-octets",
                namespaces=NSMAP,
            )
            out_oct = iface.findtext(
                "oc-if:state/oc-if:counters/oc-if:out-octets",
                namespaces=NSMAP,
            )

            if name is None:
                continue

            try:
                in_val = int(in_oct) if in_oct is not None else 0
            except ValueError:
                in_val = 0

            try:
                out_val = int(out_oct) if out_oct is not None else 0
            except ValueError:
                out_val = 0

            results.append((name, in_val, out_val))

        return results
