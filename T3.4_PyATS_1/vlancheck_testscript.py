#!/usr/bin/env python3
import os
import sys
import csv
import logging
from typing import Dict, Any

from pyats import aetest

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def read_sot_csv(csv_path: str) -> Dict[str, Dict[str, Dict[str, str]]]:
    """
    Returns:
      sot[device][vlan_id] = {"name": vlan_name, "status": status}
    """
    sot: Dict[str, Dict[str, Dict[str, str]]] = {}

    # TODO: Read csv_path and populate sot dict

    return sot


def discover_vlans(device) -> Dict[str, str]:
    """
    Returns:
      discovered[vlan_id] = vlan_name
    """
    discovered: Dict[str, str] = {}

    # TODO: Use Genie parsers to discover VLANs on NX-OS
    # Hint: try device.parse("show vlan") and fallback device.parse("show vlan brief")

    return discovered


class common_setup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        # TODO: connect devices (use via='default')
        pass

    @aetest.subsection
    def read_sot(self, testbed):
        # TODO:
        # - read filename from testbed.custom['vlan_sot']
        # - load SoT CSV
        # - store in self.parent.parameters['sot']
        pass

    @aetest.subsection
    def discover_vlans(self, testbed, steps):
        # TODO:
        # - run discover_vlans() for each device
        # - store in self.parent.parameters['discovered']
        pass


class vlan_validation(aetest.Testcase):

    @aetest.test
    def test01_present(self, steps):
        # TODO:
        # For each SoT device:
        #   - if discovered missing/empty => ERRORED
        #   - for each vlan status == "present":
        #       - FAIL if VLAN id missing
        #       - FAIL if VLAN name mismatch
        pass

    @aetest.test
    def test02_absent(self, steps):
        # TODO:
        # For each SoT device:
        #   - if discovered missing/empty => ERRORED
        #   - for each vlan status == "absent":
        #       - FAIL if VLAN id exists
        pass

    @aetest.test
    def test03_extra(self, steps, testbed):
        # TODO:
        # For each testbed device:
        #   - if device not in SoT => ERRORED
        #   - extra = discovered - SoT
        #   - for each extra VLAN => PASSX
        pass


class common_cleanup(aetest.CommonCleanup):

    @aetest.subsection
    def disconnect(self, testbed):
        for dev in testbed.devices.values():
            try:
                dev.disconnect()
            except Exception:
                pass


if __name__ == "__main__":
    # Runner uses: --testbed task_testbed.yaml
    if "--testbed" in sys.argv and "--testbed-file" not in sys.argv:
        i = sys.argv.index("--testbed")
        sys.argv[i] = "--testbed-file"

    aetest.main()
