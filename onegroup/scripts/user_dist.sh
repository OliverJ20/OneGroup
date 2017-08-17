#! /bin/bash

# Params
# $1 : Client's name

#Vars
HOME=/usr/local/onegroup/keys

#Get client's dir
CLIENT=$1;

CLIENT_DIR=$OG_openvpn_keys/$CLIENT

#copy ca.crt to the user's dir
cp $OG_openvpn_keys/ca.crt $CLIENT_DIR

#Compress client's key/certs
#cd $CLIENT_DIR
zip -r $HOME/$CLIENT.zip $CLIENT_DIR -j

#exit gracefully
exit 0;
