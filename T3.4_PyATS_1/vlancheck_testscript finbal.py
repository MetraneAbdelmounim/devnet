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
    sot: Dict[str, Dict[str, Dict[str, str]]] = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            device = (row.get("device") or "").strip()
            vlan_id = (row.get("vlan id") or "").strip()
            vlan_name = (row.get("vlan name") or "").strip()
            status = (row.get("status") or "").strip().lower()

            if not device or not vlan_id:
                continue

            sot.setdefault(device, {})
            sot[device][str(vlan_id)] = {"name": vlan_name, "status": status}

    return sot


def _extract_vlans(parsed: Dict[str, Any]) -> Dict[str, str]:
    out: Dict[str, str] = {}
    vlans = parsed.get("vlans") or {}
    for vid, data in vlans.items():
        name = ""
        if isinstance(data, dict):
            name = str(data.get("name", "")).strip()
        out[str(vid)] = name
    return out


def discover_vlans(device) -> Dict[str, str]:
    # NX-OS commonly supports these
    for cmd in ("show vlan", "show vlan brief"):
        try:
            parsed: Dict[str, Any] = device.parse(cmd)
            vlans = _extract_vlans(parsed)
            if vlans:
                return vlans
        except Exception:
            continue
    return {}


class common_setup(aetest.CommonSetup):

    @aetest.subsection
    def connect(self, testbed):
        for dev in testbed.devices.values():
            dev.connect(via="default", log_stdout=False)

    @aetest.subsection
    def read_sot(self, testbed):
        sot_file = None
        try:
            sot_file = testbed.custom.get("vlan_sot")
        except Exception:
            sot_file = None

        if not sot_file:
            self.errored("Missing required testbed custom variable: vlan_sot")

        sot_path = sot_file if os.path.isabs(sot_file) else os.path.join(os.getcwd(), sot_file)
        self.parent.parameters["sot"] = read_sot_csv(sot_path)

    @aetest.subsection
    def discover_vlans(self, testbed, steps):
        discovered_all: Dict[str, Dict[str, str]] = {}
        for dev in testbed.devices.values():
            with steps.start(f"Learning VLANs on '{dev.name}'", continue_=True):
                discovered_all[dev.name] = discover_vlans(dev)
        self.parent.parameters["discovered"] = discovered_all


class vlan_validation(aetest.Testcase):

    @aetest.test
    def test01_present(self, steps):
        sot: Dict[str, Dict[str, Dict[str, str]]] = self.parent.parameters["sot"]
        discovered: Dict[str, Dict[str, str]] = self.parent.parameters["discovered"]

        for device_name, sot_vlans in sot.items():
            with steps.start(f"Verifying required VLANs on {device_name}", continue_=True) as dev_step:
                dev_vlans = discovered.get(device_name)
                if not dev_vlans:
                    dev_step.errored(f"No VLAN data discovered for device '{device_name}' present in SoT")
                    continue

                for vlan_id, meta in sot_vlans.items():
                    if meta.get("status", "").lower() != "present":
                        continue

                    expected_name = (meta.get("name") or "").strip()

                    with dev_step.start(f"Checking for required VLAN {vlan_id}[{expected_name}]", continue_=True) as vlan_step:
                        if vlan_id not in dev_vlans:
                            vlan_step.failed(f"VLAN {vlan_id} is missing on {device_name}")
                            continue

                        actual_name = (dev_vlans.get(vlan_id) or "").strip()
                        if actual_name != expected_name:
                            vlan_step.failed(
                                f"VLAN {vlan_id} name mismatch on {device_name}: "
                                f"expected '{expected_name}', got '{actual_name}'"
                            )

    @aetest.test
    def test02_absent(self, steps):
        sot: Dict[str, Dict[str, Dict[str, str]]] = self.parent.parameters["sot"]
        discovered: Dict[str, Dict[str, str]] = self.parent.parameters["discovered"]

        for device_name, sot_vlans in sot.items():
            with steps.start(f"Verifying absent VLANs on {device_name}", continue_=True) as dev_step:
                dev_vlans = discovered.get(device_name)
                if not dev_vlans:
                    dev_step.errored(f"No VLAN data discovered for device '{device_name}' present in SoT")
                    continue

                for vlan_id, meta in sot_vlans.items():
                    if meta.get("status", "").lower() != "absent":
                        continue

                    expected_name = (meta.get("name") or "").strip()
                    with dev_step.start(f"Checking for absent VLAN {vlan_id}[{expected_name}]", continue_=True) as vlan_step:
                        if vlan_id in dev_vlans:
                            vlan_step.failed(f"VLAN {vlan_id} exists on {device_name} but SoT says 'absent'")

    @aetest.test
    def test03_extra(self, steps, testbed):
        sot: Dict[str, Dict[str, Dict[str, str]]] = self.parent.parameters["sot"]
        discovered: Dict[str, Dict[str, str]] = self.parent.parameters["discovered"]

        for dev in testbed.devices.values():
            device_name = dev.name
            with steps.start(f"Checking extra VLANs on {device_name}", continue_=True) as dev_step:
                if device_name not in sot:
                    dev_step.errored(f"No SoT data found for testbed device '{device_name}'")
                    continue

                dev_vlans = discovered.get(device_name) or {}
                sot_vlan_ids = set(sot[device_name].keys())
                extra_vlan_ids = sorted(set(dev_vlans.keys()) - sot_vlan_ids)

                if not extra_vlan_ids:
                    continue

                for vlan_id in extra_vlan_ids:
                    vlan_name = dev_vlans.get(vlan_id, "")
                    with dev_step.start(f"Extra VLAN {vlan_id}[{vlan_name}]", continue_=True) as s:
                        s.passx(f"VLAN {vlan_id} exists on {device_name} but is not in SoT")


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
