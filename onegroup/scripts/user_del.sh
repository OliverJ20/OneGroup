#! /bin/bash

#get client's dir name
CLIENT=$1;
CLIENT_DIR=${!OG_openvpn_keys}/$CLIENT

#Remove directory
rm $CLIENT_DIR -rf

#Exit gracefully
exit 0;

