from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

import os

from netmiko import ConnectHandler
from cli_utils import parse_output

# Default values / policy definitions
ADMIN_USER = os.environ.get("XE_VAR_USER", "expert")

# Local users that are allowed to exist on the box by policy
AUTHORIZED_USERS: List[str] = [
    "expert",
    "expert_auto",
    "admin_auto",
    ADMIN_USER,
]

# SNMP communities that are always allowed to exist (platform defaults, etc.)
BUILT_IN_COMMUNITIES: List[str] = ["ILMI"]


@dataclass
class Mgmt_Compliance:
    """
    Helper class used by manage_access_compliance.py to keep local
    user and SNMP configuration in compliance with policy.
    """

    address: str
    port: int
    username: str
    password: str
    community_string: str
    mgmt_list_name: Optional[str] = "MGMT_ACCESS"
    local_admin_user: Optional[str] = ADMIN_USER
    authorized_users: Optional[List[str]] = field(
        default_factory=lambda: AUTHORIZED_USERS.copy()
    )

    # -------------------------------------------------------------------------
    # Device connection helper
    # -------------------------------------------------------------------------
    def connect(self) -> ConnectHandler:
        """
        Create and return a Netmiko ConnectHandler for the device.
        """
        net_connect = ConnectHandler(
            device_type="cisco_ios",
            host=self.address,
            port=self.port,
            username=self.username,
            password=self.password,
        )
        return net_connect

    # -------------------------------------------------------------------------
    # Local user helpers
    # -------------------------------------------------------------------------
    def current_unauthorized_users(self) -> List[str]:
        """
        Look up and return the current local users that are *not* authorized
        by policy.

        A user is considered unauthorized if their username is not present
        in self.authorized_users.
        """
        # Connect to the device
        net_connect = self.connect()

        # Use the Netmiko ConnectHandler to get the current list of local users.
        # The lab text specifies this command:
        #   show running-config aaa username
        local_users_raw = net_connect.send_command("show running-config aaa username")

        # Disconnect from the device
        net_connect.disconnect()

        # Iterate through each line of the output and extract usernames
        unauthorized: List[str] = []
        allowed = self.authorized_users or []

        for line in local_users_raw.splitlines():
            line = line.strip()
            if not line.startswith("username "):
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            user = parts[1]
            if user not in allowed:
                unauthorized.append(user)

        return unauthorized

    # -------------------------------------------------------------------------
    # SNMP helpers
    # -------------------------------------------------------------------------
    def current_unauthorized_communities(self) -> List[str]:
        """
        Parse the current SNMP configuration and return a list of
        community strings that are not allowed by policy.

        SNMP communities are considered unauthorized if they are not:
        - the desired management community (self.community_string), or
        - included in BUILT_IN_COMMUNITIES.
        """
        net_connect = self.connect()

        # Pull the current SNMP community configuration
        # NTC templates include a parser for:
        #   show snmp community
        snmp_raw = net_connect.send_command("show snmp community")

        net_connect.disconnect()

        # Parse the output using TextFSM / NTC templates
        parsed = parse_output(
            platform="cisco_ios",
            command="show snmp community",
            data=snmp_raw,
        )

        unauthorized: List[str] = []

        for entry in parsed:
            community = entry.get("community")
            if not community:
                continue

            # Skip the compliant and built-in communities
            if community == self.community_string:
                continue
            if community in BUILT_IN_COMMUNITIES:
                continue

            unauthorized.append(community)

        return unauthorized

    # -------------------------------------------------------------------------
    # Configuration update helpers
    # -------------------------------------------------------------------------
    def update_local_password(self) -> bool:
        """
        Ensure the local admin user exists with the configured password and
        remove any unauthorized local users.

        Returns True when configuration was pushed successfully.
        """
        # Determine which users should be removed
        unauthorized = self.current_unauthorized_users()

        net_connect = self.connect()

        config_cmds: List[str] = []

        # Remove unauthorized usernames
        for user in unauthorized:
            config_cmds.append(f"no username {user}")

        # (Re)configure the local admin user with the desired password
        if self.local_admin_user:
            config_cmds.append(
                f"username {self.local_admin_user} privilege 15 secret {self.password}"
            )

        if config_cmds:
            net_connect.send_config_set(config_cmds)
            try:
                net_connect.save_config()
            except Exception:
                # Some platforms / auth models may not support save_config via Netmiko
                pass

        net_connect.disconnect()
        return True

    def update_snmp_community(self) -> bool:
        """
        Ensure that only the compliant SNMP community configured in
        self.community_string exists and that it is tied to the correct
        ACL (self.mgmt_list_name).

        Any other SNMP communities (except the built-ins) are removed.
        """
        # Determine unauthorized communities
        unauthorized = self.current_unauthorized_communities()

        net_connect = self.connect()

        config_cmds: List[str] = []

        # Remove each unauthorized community
        for community in unauthorized:
            config_cmds.append(f"no snmp-server community {community}")

        # Configure the compliant community with the required ACL
        config_cmds.append(
            f"snmp-server community {self.community_string} RO {self.mgmt_list_name}"
        )

        net_connect.send_config_set(config_cmds)

        try:
            net_connect.save_config()
        except Exception:
            pass

        net_connect.disconnect()
        return True
