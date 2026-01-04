from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import re

from netmiko import ConnectHandler


@dataclass
class Mgmt_Compliance:
    """
    Management Compliance class.
    """

    AUTHORIZED_USERS = ["expert", "expert_auto", "admin_auto", "ADMIN_USER"]
    BUILT_IN_COMMUNITIES = ["ILMI"]

    address: str
    port: int
    username: str
    password: str
    community_string: str
    mgmt_acl_name: Optional[str] = "MGMT_ACCESS"
    local_admin_user: Optional[str] = "ADMIN_USER"
    authorized_users: Optional[list[str]] = field(
        default_factory=lambda: Mgmt_Compliance.AUTHORIZED_USERS
    )

    def connect(self) -> ConnectHandler:
        """
        Create and return a ConnectHandler for the device.
        """
        net_connect = ConnectHandler(
            host=self.address,
            port=self.port,
            username=self.username,
            password=self.password,
            device_type="cisco_ios",
        )

        return net_connect

    def current_unauthorized_users(self) -> list[str]:
        """
        Lookup and return the current local users not authorized by policy.
        """
        net_connect = self.connect()

        # Use the command requested by the task text
        local_users = net_connect.send_command("show running-config aaa username")

        net_connect.disconnect()

        # Extract usernames from lines like: "username <name> ..."
        found: list[str] = []
        for line in local_users.splitlines():
            line = line.strip()
            m = re.match(r"^username\s+(\S+)\s+", line)
            if m:
                found.append(m.group(1))

        unauthorized_users = [u for u in found if u not in self.AUTHORIZED_USERS]
        return unauthorized_users

    def current_unauthorized_communities(self) -> list[str]:
        """
        Parse the current SNMP community config and return unauthorized communities.
        """
        net_connect = self.connect()

        cmd = "show running-config | include ^snmp-server community"

        # TextFSM (NTC) parsing when templates are available
        parsed = net_connect.send_command(cmd, use_textfsm=True)
        raw = net_connect.send_command(cmd)

        net_connect.disconnect()

        communities: list[str] = []

        def fallback_parse(text: str) -> list[str]:
            out: list[str] = []
            for ln in text.splitlines():
                ln = ln.strip()
                if not ln.startswith("snmp-server community"):
                    continue
                parts = ln.split()
                if len(parts) >= 3:
                    out.append(parts[2])
            return out

        # Handle all possible return shapes safely
        if isinstance(parsed, list) and parsed:
            if isinstance(parsed[0], dict):
                for entry in parsed:
                    comm = (
                        entry.get("community")
                        or entry.get("snmp_community")
                        or entry.get("community_string")
                    )
                    if comm:
                        communities.append(str(comm))
            elif isinstance(parsed[0], str):
                communities.extend(fallback_parse("\n".join(parsed)))
        elif isinstance(parsed, str) and parsed.strip():
            communities.extend(fallback_parse(parsed))
        else:
            communities.extend(fallback_parse(raw))

        # Normalize unique
        communities = [c.strip() for c in communities if c and c.strip()]
        communities = list(dict.fromkeys(communities))

        unauthorized = [
            c for c in communities
            if c != self.community_string and c not in self.BUILT_IN_COMMUNITIES
        ]
        return unauthorized

    def update_local_password(self, new_password: str) -> None:
        """
        Use ConnectHandler to update the local admin user's password.
        """
        if not self.local_admin_user:
            raise ValueError("local_admin_user is not set")
        if not new_password:
            raise ValueError("new_password is empty")

        net_connect = self.connect()

        # username <user> secret <password>
        net_connect.send_config_set([f"username {self.local_admin_user} secret {new_password}"])

        net_connect.save_config()
        net_connect.disconnect()

    def update_snmp_community(self) -> None:
        """
        Use ConnectHandler to update/add the correct SNMP community string.
        """
        if not self.community_string:
            raise ValueError("community_string is not set")

        net_connect = self.connect()

        cmd = f"snmp-server community {self.community_string} RO"
        if self.mgmt_acl_name:
            cmd = f"{cmd} {self.mgmt_acl_name}"

        net_connect.send_config_set([cmd])

        net_connect.save_config()
        net_connect.disconnect()

    # (Optional helpers used by manage_access_compliance.py)
    def remove_users(self, users: list[str]) -> None:
        if not users:
            return
        net_connect = self.connect()
        net_connect.config_mode()
        for u in users:
            out = net_connect.send_command_timing(f"no username {u}")
            if "confirm" in out.lower():
                net_connect.send_command_timing("\n")
        net_connect.exit_config_mode()
        net_connect.save_config()
        net_connect.disconnect()

    def remove_snmp_communities(self, communities: list[str]) -> None:
        if not communities:
            return
        net_connect = self.connect()
        net_connect.config_mode()
        for c in communities:
            out = net_connect.send_command_timing(f"no snmp-server community {c}")
            if "confirm" in out.lower():
                net_connect.send_command_timing("\n")
        net_connect.exit_config_mode()
        net_connect.save_config()
        net_connect.disconnect()
