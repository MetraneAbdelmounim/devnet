ncs-netsim create-device ~/nso/packages/neds//cisco-ios-cli-6.69 access-sw-01
ncs-netsim start
ncs-setup \
	--package ~/nso/packages/neds/cisco-ios-cli-6.69 \
	--package ./access-service \
	--dest .
ncs
ncs-netsim ncs-xml-init | ncs_load -l -m
ncs_cli -u admin -C <<HERE
devices sync-from
HERE
