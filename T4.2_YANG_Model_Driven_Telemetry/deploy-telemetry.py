#!/usr/bin/env python

from scrapli.driver.core import IOSXEDriver, NXOSDriver
import logging

CERT_FILE = "telegraf-cert.pem"

DEVICE_USERNAME = "expert"
DEVICE_PASSWORD = "1234QWer!"

RTR_DEVICE = {
    "host": "rtr-edge-01.ppm.example.com",
    "auth_username": DEVICE_USERNAME,
    "auth_password": DEVICE_PASSWORD,
    "auth_strict_key": False,
}

SPINE_DEVICE = {
    "host": "sw-spine-01.ppm.example.com",
    "auth_username": DEVICE_USERNAME,
    "auth_password": DEVICE_PASSWORD,
    "auth_strict_key": False,
}

RTR_CONFIG = "rtr-edge-01-config.txt"
SPINE_CONFIG = "sw-spine-01-config.txt"


def deploy_rtr_config() -> bool:
    """Deploy router config.

    Returns:
        result (bool): True if config was deployed successfully. False otherwise.
    """
    with IOSXEDriver(**RTR_DEVICE) as conn:
        responses = conn.send_configs_from_file(RTR_CONFIG)
        for response in responses:
            try:
                response.raise_for_status()
            except Exception as e:
                logging.exception(
                    f"ERROR: Failed to deploy config to {RTR_DEVICE['host']}: {e}"
                )
                return False

    return True


def deploy_cert() -> bool:
    """Deploy the TLS certificate for NXOS.

    Returns:
        result (bool): True if cert was deployed successfully.  False otherwise.
    """
    with open(CERT_FILE) as fd:
        cert_contents = fd.read()

    cert_contents = cert_contents.replace("\n", "\\n")

    with NXOSDriver(**SPINE_DEVICE) as conn:
        conn.acquire_priv("tclsh")
        try:
            conn.channel.send_input(f"set fd [open /bootflash/{CERT_FILE} w]")
            conn.channel.send_input(f'puts $fd "{cert_contents}"')
            conn.channel.send_input("close $fd")
        except Exception as e:
            logging.exception(
                f"ERROR: Failed to deploy certificate to {SPINE_DEVICE['host']}: {e}"
            )
            return False

    return True


def deploy_spine_config() -> bool:
    """Deploy configuration to spine switch.

    Results:
        result (bool): Returns True if the config was deployed successfully.  False otherwise.
    """
    with NXOSDriver(**SPINE_DEVICE) as conn:
        responses = conn.send_configs_from_file(SPINE_CONFIG, eager=True)
        for response in responses:
            try:
                response.raise_for_status()
            except Exception as e:
                logging.exception(
                    f"ERROR: Failed to deploy config to {SPINE_DEVICE['host']}: {e}"
                )
                return False

    return True


def main() -> None:
    """Initial entry point."""

    deploy_rtr_config()

    result = deploy_cert()
    if not result:
        exit(1)

    deploy_spine_config()


if __name__ == "__main__":
    main()
