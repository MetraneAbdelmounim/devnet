#! /bin/bash

# Check if NSO has been "setup"
if test -f ./ncs.conf; then
	# Check if NSO is running. If not start it.
	if ! ncs --status; then
		echo "NSO is NOT running"
		ncs
	fi
	# Check if the netsim device is running. If not start it.
	if ! ncs-netsim status access-sw-01; then
		echo "netsim is NOT running"
		ncs-netsim start
	fi
fi
