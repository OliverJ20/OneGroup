#! /bin/bash

# Params
# $1 : Client's name
# $2 : Location of the vpn keys folder (optional)
# $3 : Location of the vpn easy-rsa folder (optional)
# $4 : Location of the client config

#Vars
KEYS=/etc/openvpn/keys
ERSA=/etc/openvpn/easy-rsa
DEF_CONFIG=/etc/openvpn/client.conf

if [[ ! -z $2 ]]; then
    KEYS=$2
fi

if [[ ! -z $3 ]]; then
    ERSA=$3
fi

if [[ ! -z $4 ]]; then
    DEF_CONFIG=$4
fi

#Create client's filename and dir
CLIENT=$1;
CLIENT_DIR=$KEYS/$CLIENT
mkdir $CLIENT_DIR

#Create client key/cert pair
cd $ERSA;
source ./vars
./pkitool $CLIENT;

#Create config variables
CLIENT_CONF="$CLIENT.conf";
CLIENT_CERT="$CLIENT.crt";
CLIENT_KEY="$CLIENT.key";
CLIENT_CSR="$CLIENT.csr";

#Create new config file and change key and cert sections
cp $DEF_CONFIG $CLIENT_DIR/$CLIENT_CONF;

#sudo sed -i -e 's,ca ca.crt,ca '"$CA"',g' $DIR/$CLIENT_CONF;
sudo sed -i -e 's,cert client.crt,cert '"$CLIENT_CERT"',g' $CLIENT_DIR/$CLIENT_CONF;
sudo sed -i -e 's,key client.key,key '"$CLIENT_KEY"',g' $CLIENT_DIR/$CLIENT_CONF;

#create directory and move key/certs into it
mv $KEYS/$CLIENT_CERT $KEYS/$CLIENT_KEY $KEYS/$CLIENT_CSR $CLIENT_DIR
 
#Exit gracefully
exit 0;
