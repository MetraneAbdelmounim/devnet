#!/usr/bin/env python3

"""
Driver script that uses the Mgmt_Compliance class to:

* Report unauthorized local users and SNMP communities.
* Update the local admin password.
* Enforce a single SNMP community protected by the management ACL.

This file is intended to be "pre-configured" for the lab – you should
NOT need to modify it when completing the task. All logic that students
are expected to change lives in Mgmt_Compliance.py.
"""

import os
import sys

from Mgmt_Compliance import Mgmt_Compliance

# ---------------------------------------------------------------------------
# Environment / defaults
# ---------------------------------------------------------------------------

ROUTER_ADDRESS = os.environ.get("ROUTER_ADDRESS", "192.168.5.118")
ROUTER_PORT = int(os.environ.get("ROUTER_PORT", "22"))

USERNAME = os.environ.get("XE_VAR_USER")
PASSWORD = os.environ.get("XE_VAR_PASS")

# From the lab instructions
COMPLIANT_SNMP_COMMUNITY = "pmm_noc#"
COMPLIANT_ADMIN_PASSWORD = "AlwaysNMotion"


def validate_env() -> bool:
    """
    Make sure all required environment variables are present.
    """
    missing = []
    if not USERNAME:
        missing.append("XE_VAR_USER")
    if not PASSWORD:
        missing.append("XE_VAR_PASS")

    if missing:
        print("ERROR: Missing required environment variables:", ", ".join(missing))
        return False

    return True


def build_mgmt_compliance() -> Mgmt_Compliance:
    """
    Helper to build the Mgmt_Compliance object used for the rest of the script.
    """
    return Mgmt_Compliance(
        address=ROUTER_ADDRESS,
        port=ROUTER_PORT,
        username=USERNAME,
        password=PASSWORD,
        community_string=COMPLIANT_SNMP_COMMUNITY,
    )


def main() -> None:
    if not validate_env():
        sys.exit(1)

    mgmt = build_mgmt_compliance()

    print(f"Checking management configuration on device {ROUTER_ADDRESS}:{ROUTER_PORT}")
    print("-" * 72)

    # -----------------------------------------------------------------------
    # Gather current state
    # -----------------------------------------------------------------------
    unauthorized_users = mgmt.current_unauthorized_users()
    unauthorized_communities = mgmt.current_unauthorized_communities()

    print("Current unauthorized local users:")
    if unauthorized_users:
        for user in unauthorized_users:
            print(f"  - {user}")
    else:
        print("  (none)")

    print("\nCurrent unauthorized SNMP communities:")
    if unauthorized_communities:
        for community in unauthorized_communities:
            print(f"  - {community}")
    else:
        print("  (none)")

    print("\n" + "-" * 72)
    answer = input(
        "Apply compliance changes (update admin password / SNMP)? [y/N]: "
    ).strip().lower()
    if answer not in ("y", "yes"):
        print("No changes applied.")
        return

    # -----------------------------------------------------------------------
    # Enforce compliance
    # -----------------------------------------------------------------------
    print("\nUpdating local admin user password...")
    mgmt.password = COMPLIANT_ADMIN_PASSWORD
    if mgmt.update_local_password():
        print("  ✔ Local user configuration updated.")
    else:
        print("  ✖ Failed to update local user configuration.")

    print("\nUpdating SNMP community configuration...")
    if mgmt.update_snmp_community():
        print("  ✔ SNMP configuration updated.")
    else:
        print("  ✖ Failed to update SNMP configuration.")

    print("\nDone.")


if __name__ == "__main__":
    main()
