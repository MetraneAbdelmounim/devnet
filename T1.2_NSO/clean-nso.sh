# Stop NSO and netsim
ncs --stop
ncs-netsim stop

# Delete NSO and netsim directories
rm -Rf netsim \
	logs \
	ncs-cdb \
	ncs.conf \
	README.ncs \
	README.netsim \
	scripts \
	state \
	storedstate \
	packages \
	target
