#! /bin/bash

# Params
# $1 : Client's name

#get client's dir name
CLIENT=$1;

#Remove directory
rm $OG_openvpn_keys/$CLIENT -rf

#Exit gracefully
exit 0;

