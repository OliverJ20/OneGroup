#! /bin/bash

#Vars
DIR=/etc/openvpn;
ERSA=$DIR/easy-rsa;
KEYS=$DIR/keys
#CA="CA.key";

#Create client's filename
CLIENT=$1;

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
cp $DIR/client.conf $DIR/$CLIENT_CONF;

#sudo sed -i -e 's,ca ca.crt,ca '"$CA"',g' $DIR/$CLIENT_CONF;
sudo sed -i -e 's,cert client.crt,cert '"$CLIENT_CERT"',g' $DIR/$CLIENT_CONF;
sudo sed -i -e 's,key client.key,key '"$CLIENT_KEY"',g' $DIR/$CLIENT_CONF;

#create directory and move key/certs into it
mkdir $KEYS/$CLIENT
mv $DIR/$CLIENT_CONF $KEYS/$CLIENT_CERT $KEYS/$CLIENT_KEY $KEYS/$CLIENT_CSR $KEYS/$CLIENT
 
#Exit gracefully
exit 0;
