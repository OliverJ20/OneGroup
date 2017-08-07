#! /bin/bash

# Params
# $1 : Client's name
# $2 : Location of the vpn keys folder (optional)

#Vars
HOME=/usr/local/onegroup/keys

#Get client's dir
CLIENT=$1;
KEYS=/etc/openvpn/keys
if [[ ! -z $2 ]]; then
    KEYS=$2
fi

CLIENT_DIR=$KEYS/$CLIENT

#copy ca.crt to the user's dir
cp $KEYS/ca.crt $CLIENT_DIR

#Compress client's key/certs
#cd $CLIENT_DIR
zip -r $HOME/$CLIENT.zip $CLIENT_DIR -j

#exit gracefully
exit 0;
