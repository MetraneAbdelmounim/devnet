#!/usr/bin/env python

from ats.log.utils import banner
from genie.conf import Genie
from pyats import aetest
import logging

# Get your logger for your script
log = logging.getLogger(__name__)

############################################################
##                  COMMON SETUP SECTION                  ##
############################################################

class device_setup(aetest.CommonSetup):
    """ Common Setup section """

    @aetest.subsection
    def connect(self, testbed, steps):
        genie_testbed = Genie.init(testbed)
        devices = []
        for device in genie_testbed.devices.values():
            with steps.start("Connecting to device '{d}'".format(d=device.name)):
                log.info(banner(
                    "Connecting to device '{d}'".format(d=device.name)))
                try:
                    device.connect()
                except Exception as e:
                    self.failed(
                        "Failed to establish connection to {}".format(device.name)
                    )

                devices.append(device)
        self.devices = devices

    @aetest.subsection
    def gather_interface_details(self, steps):
        interface_dict = {}
        for device in self.devices:
            with steps.start(
                "Gathering interface details on '{d}'".format(d=device.name)
            ):
                interface_info = device.learn('interface').info
                interface_dict.setdefault(device.name, interface_info)

        self.parent.parameters.update(interfaces=interface_dict)

############################################################
##                    TESTCASES SECTION                   ##
############################################################

class error_validation(aetest.Testcase):
    """ This is user Testcases section """

    @aetest.test
    def check_counters(self, steps):
        """ Checking for error counters on all interfaces """
        counter_list = [
            "in_errors",
            "in_crc_errors",
            "out_errors",
        ]

        for device, interfaces in self.parent.parameters['interfaces'].items():
            for interface, details in interfaces.items():
                with steps.start(
                    f"Device {device} Interface {interface}",
                    continue_=True
                ) as interface_step:
                    for counter in counter_list:
                        if details['counters'][counter] != 0:
                            interface_step.failed(
                                f"Counter {counter} error count "
                                f"{details['counters'][counter]}"
                            )


if __name__ == '__main__':
    aetest.main()
