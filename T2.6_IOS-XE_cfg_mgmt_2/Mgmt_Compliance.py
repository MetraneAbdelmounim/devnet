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

        TODO:
        * Create and return a Netmiko ConnectHandler for interacting
          with a Cisco IOS XE device using the attributes of this class.
        """
        # TODO: replace pass with a proper ConnectHandler instance
        pass

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

        # TODO: Use the Netmiko ConnectHandler to get the current list of
        #       local users on the device.
        #       Use the command
        #           show running-config aaa username
        #       to pull the current user list.
        #
        # Example:
        #   local_users_raw = net_connect.send_command("show running-config aaa username")
        local_users_raw = ""

        # Disconnect from the device
        net_connect.disconnect()

        # TODO: Iterate through the list of local users and extract all
        #       usernames that are *not* in self.authorized_users.
        #
        # The function must return a list of unauthorized usernames.
        unauthorized: List[str] = []

        # TODO: populate the `unauthorized` list based on `local_users_raw`
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
        # TODO: connect to the device
        net_connect = self.connect()

        # TODO: Pull the current SNMP community configuration from the device.
        #
        # Use a command that is supported by NTC templates, for example:
        #   show snmp community
        snmp_raw = ""

        # TODO: disconnect from the device
        net_connect.disconnect()

        # TODO: Parse the output using TextFSM / NTC templates via cli_utils.parse_output.
        #
        # Example:
        #   parsed = parse_output(
        #       platform="cisco_ios",
        #       command="show snmp community",
        #       data=snmp_raw,
        #   )
        parsed: List[dict] = []

        # TODO: Build and return a list of SNMP community strings that are
        #       not compliant (i.e., not self.community_string and not in
        #       BUILT_IN_COMMUNITIES).
        unauthorized: List[str] = []

        return unauthorized

    # -------------------------------------------------------------------------
    # Configuration update helpers
    # -------------------------------------------------------------------------
    def update_local_password(self) -> bool:
        """
        Ensure the local admin user exists with the configured password and
        remove any unauthorized local users.

        TODO:
        * Use a ConnectHandler instance to remove unauthorized users
          and (re)configure the local admin user with the supplied password.
        * Return True once the configuration has been pushed.
        """
        # TODO: Implement configuration logic
        return False

    def update_snmp_community(self) -> bool:
        """
        Ensure that only the compliant SNMP community configured in
        self.community_string exists and that it is tied to the correct
        ACL (self.mgmt_list_name).

        Any other SNMP communities (except the built-ins) should be removed.

        TODO:
        * Use a ConnectHandler instance and the results of
          current_unauthorized_communities() to remove non-compliant
          communities and configure the desired one.
        * Return True once the configuration has been pushed.
        """
        # TODO: Implement configuration logic
        return False
