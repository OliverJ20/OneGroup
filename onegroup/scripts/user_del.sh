#! /bin/bash

#Vars
DIR=/etc/openvpn;
ERSA=$DIR/easy-rsa;
KEYS=$DIR/keys

#get client's dir name
CLIENT=$1;
CLIENT_DIR=$KEYS/$CLIENT

#Remove directory
rm $CLIENT_DIR -rf

#Exit gracefully
exit 0;

