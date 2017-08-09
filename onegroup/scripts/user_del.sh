#! /bin/bash

# Params
# $1 : Client's name
# $2 : Location of the client's folder (optional)

#get client's dir name
CLIENT=$1;
CLIENT_DIR=/etc/openvpn/keys/$CLIENT
if [[ ! -x $2 ]]; then
	CLIENT_DIR=$2/$CLIENT
fi

#Remove directory
rm $CLIENT_DIR -rf

#Exit gracefully
exit 0;

