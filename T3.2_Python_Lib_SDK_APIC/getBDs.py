#!/usr/bin/env python3
import requests
import json
import urllib3
import logging
import os
from typing import Any, cast, Optional

urllib3.disable_warnings()  # type: ignore


class ACIModule(object):
    """ACIModule class."""

    def __init__(self, hostname: str, username: str, password: str) -> None:
        """Init ACIModule class."""
        self.username = username
        self.hostname = hostname
        self.password = password
        self.timeout = 30
        self.authenticated = False

        self.base_url = "https://" + str(hostname) + "/api/"

        if not self.authenticated:
            if not self.login():
                raise Exception("Unable to login")

    def login(self) -> bool:
        """Login to ACI APIC Controller."""
        base_url = "https://" + str(self.hostname) + "/api/"
        auth_bit = "aaaLogin.json"
        auth_url = base_url + auth_bit

        auth_data = {
            "aaaUser": {"attributes": {"name": self.username, "pwd": self.password}}
        }

        self.s = requests.session()
        resp = self.s.post(auth_url, verify=False, data=json.dumps(auth_data))

        # Optional: basic sanity check (APIC usually returns 200 on success)
        if resp.status_code != 200:
            logging.error("Login failed: %s %s", resp.status_code, resp.text)
            return False

        self.authenticated = True
        return True

    def handle_req(
        self,
        reqType: str,
        url: str,
        data: Optional[dict[Any, Any]] = None,
        pagesize: int = 100,
    ) -> list[dict[str, Any]]:
        """Perform request towards APIC controller."""
        logging.debug("handle_req init")
        req_url = self.base_url + url

        if data is None:
            data = {}

        if reqType == "get":
            logging.debug("handle_req get %s", req_url)
            session_response = self.s.get(req_url, verify=False)
            if session_response.status_code == 200:
                result = session_response.json()
                result_typed = cast(list[dict[str, Any]], result.get("imdata", []))
                return result_typed
            raise Exception(f"Unhandled status_code: {session_response.status_code}")

        if reqType == "post":
            logging.debug("handle_req post %s", req_url)
            session_response = self.s.post(
                req_url, verify=False, data=json.dumps(data)
            )
            if session_response.status_code == 200:
                result = session_response.json()
                result_typed = cast(list[dict[str, Any]], result.get("imdata", []))
                return result_typed

            # keep your original debug prints
            print(session_response.status_code)
            try:
                print(session_response.json())
            except Exception:
                print(session_response.text)
            raise Exception(f"Unhandled status_code: {session_response.status_code}")

        raise Exception("Unhandled handle_req scenario")

    # ==========================
    # TODO VERSION (practice)
    def get_BD(self, subnet_address: Optional[str] = None) -> list[dict[str, str]]:
        """
        Get all BDs or filter BDs by subnet (fvSubnet).

        TODO requirements:
        If subnet_address is provided:
        - Return ONLY the BDs (fvBD) that have a child fvSubnet with ip == subnet_address
        - Use ACI filtering methods (query-target + target-subtree-class + query-target-filter)
        - Return output in aci_list_cleanup format (already implemented)
        If subnet_address is NOT provided:
        - Return all BDs (same behavior as before)
        """
        logging.debug("get_BD init")

        if subnet_address:
            logging.debug("get_BD init Subnet case")

            # 1) Get all Bridge Domains (BDs)
            bds = self.handle_req("get", "class/fvBD.json")
            bds = self.aci_list_cleanup(bds)

            bds_return: list[dict[str, str]] = []

            for bd in bds:
                # TODO 1: get the BD DN (bd["dn"])
                # TODO 2: build bd_obj_address = f"node/mo/{dn}.json"
                # TODO 3: build subnet_querystring that:
                #   - query-target=children
                #   - target-subtree-class=fvSubnet
                #   - query-target-filter=eq(fvSubnet.ip,"<subnet address>")
                # TODO 4: call handle_req("get", f"{bd_obj_address}?{subnet_querystring}")
                # TODO 5: cleanup with aci_list_cleanup
                # TODO 6: if any returned fvSubnet has ip == subnet_address:
                #   - append the BD once to bds_return
                #   - break (do not duplicate BD)
                pass  # remove after implementing TODOs

            # TODO 7: return bds_return after checking all BDs
            return bds_return

        # Non-subnet case: return all BDs
        logging.debug("get_BD init Non subnet case")
        BD = self.handle_req("get", "class/fvBD.json")
        bd_cleaned = self.aci_list_cleanup(BD)
        return bd_cleaned

    def aci_list_cleanup(self, data: list[dict[str, Any]]) -> list[dict[str, str]]:
        """Reformat returned data from APIC controller."""
        # ACI outputs in a format [mo]['attributes'][data]
        # sanitizing this output data to simple list

        return_data: list[dict[str, str]] = []
        for entry in data:
            for key in entry:
                attrs = entry[key].get("attributes", {})
                if isinstance(attrs, dict):
                    # Cast values to str-ish dict for your original return typing
                    return_data.append(cast(dict[str, str], attrs))
        return return_data


if __name__ == "__main__":

    if "ACI_VAR_LOG_LEVEL" in os.environ:
        if os.environ["ACI_VAR_LOG_LEVEL"] == "info":
            logging.basicConfig(level=logging.INFO)
        elif os.environ["ACI_VAR_LOG_LEVEL"] == "debug":
            logging.basicConfig(level=logging.DEBUG)
        elif os.environ["ACI_VAR_LOG_LEVEL"] == "error":
            logging.basicConfig(level=logging.ERROR)
        else:
            logging.basicConfig(level=logging.INFO)
    else:
        logging.basicConfig(level=logging.INFO)

    logging.info("getBDs.py initialized")

    hostname = "192.168.181.22"
    username = os.environ["ACI_VAR_USER"]
    password = os.environ["ACI_VAR_PASS"]

    # Optional subnet address filter:
    # - prefer ENV so it works nicely with .envrc
    # - allow CLI arg for quick tests
    subnet_address = os.environ.get("ACI_VAR_SUBNET")
    if len(os.sys.argv) > 1:
        subnet_address = os.sys.argv[1]

    ACI = ACIModule(hostname, username, password)

    bds = ACI.get_BD(subnet_address=subnet_address)

    print("Total Count: " + str(len(bds)) + " objects.")
    # Optional: print results
    # print(json.dumps(bds, indent=2))
