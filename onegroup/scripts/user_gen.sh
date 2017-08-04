#! /bin/bash

#Create client's filename and dir
CLIENT=$1;
CLIENT_DIR=${!OG_openvpn_keys}/$CLIENT

#Create client key/cert pair
cd ${!OG_openvpn_ersa};
source ./vars
./pkitool $CLIENT;

#Create config variables
CLIENT_CONF="$CLIENT.conf";
CLIENT_CERT="$CLIENT.crt";
CLIENT_KEY="$CLIENT.key";
CLIENT_CSR="$CLIENT.csr";

#Create new config file and change key and cert sections
cp ${!OG_openvpn_client_config} $CLIENT_DIR;

#sudo sed -i -e 's,ca ca.crt,ca '"$CA"',g' $DIR/$CLIENT_CONF;
sudo sed -i -e 's,cert client.crt,cert '"$CLIENT_CERT"',g' $CLIENT_DIR/$CLIENT_CONF;
sudo sed -i -e 's,key client.key,key '"$CLIENT_KEY"',g' $CLIENT_DIR/$CLIENT_CONF;

#create directory and move key/certs into it
mkdir ${!OG_openvpn_keys}/$CLIENT
mv ${!OG_openvpn_keys}/$CLIENT_CERT ${!OG_openvpn_keys}/$CLIENT_KEY ${!OG_openvpn_keys}/$CLIENT_CSR $CLIENT_DIR
 
#Exit gracefully
exit 0;
