#! /bin/bash

#Vars
DIR=/etc/openvpn;
ERSA=$DIR/easy-rsa;
KEYS=$DIR/keys
HOME=/usr/share/onegroup/keys

#Get client's dir
CLIENT=$1;
CLIENT_DIR=$KEYS/$CLIENT

#copy ca.crt to the user's dir
cp $KEYS/ca.crt $CLIENT_DIR

#Compress client's key/certs
zip -r $HOME/$CLIENT.zip $CLIENT_DIR

#exit gracefully
exit 0;
