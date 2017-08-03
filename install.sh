#! /bin/bash

#GLOBALS
DIR="/etc/openvpn"
CONFIGS="/usr/share/doc/openvpn/examples/sample-config-files"
KEYS="$DIR/keys"
ERSA="$DIR/easy-rsa"

SERVER_ADR="192.168.1.11"
SERVER_PORT=1194

#Install Openvpn and easy-rsa
#print("Installing Openvpn")
sudo apt-get -y install openvpn easy-rsa >> /dev/null;

#Setup CA

#Move easy-rsa files
sudo cp /usr/share/easy-rsa $DIR -r;

#get CA details
echo "Please enter the following organisational details";
echo "COUNTRY CODE: ";
read COUNTRY;
echo "PROVINCE: "
read PROVINCE
echo "CITY: ";
read CITY;
echo "ORGANISATION NAME: ";
read ORG;
echo "EMAIL: ";
read EMAIL;
echo "ORGANISATIONAL UNIT: ";
read OU;

#Change CA config
CAvars=$ERSA/vars
sudo sed -i -e 's,export KEY_COUNTRY="US",export KEY_COUNTRY="'"$COUNTRY"'",g' $CAvars
sudo sed -i -e 's,export KEY_PROVINCE="CA",export KEY_PROVINCE="'"$PROVINCE"'",g' $CAvars
sudo sed -i -e 's,export KEY_CITY="SanFrancisco",export KEY_CITY="'"$CITY"'",g' $CAvars
sudo sed -i -e 's,export KEY_ORG="Fort-Funston",export KEY_ORG="'"$ORG"'",g' $CAvars
sudo sed -i -e 's,export KEY_EMAIL="me@myhost.mydomain",export KEY_EMAIL="'"$EMAIL"'",g' $CAvars
sudo sed -i -e 's,export KEY_OU="MyOrganizationalUnit",export KEY_OU="'"$OU"'",g' $CAvars
sudo sed -i -e 's,export KEY_DIR="$EASY_RSA/keys",export KEY_DIR="/etc/openvpn/keys",g' $CAvars
sudo sed -i -e 's,export KEY_CONFIG=`$EASY_RSA/whichopensslcnf $EASY_RSA`,export KEY_CONFIG=$EASY_RSA/openssl-1.0.0.cnf,g' $CAvars

#Change ownership of the openvpn directory
sudo chown $USER $DIR -R

cd $ERSA

#Create PKI
echo "Setting up CA";
source vars
./clean-all
./pkitool --initca

#Create Certs and Keys

#server
SERVER="server";

echo "Creating Server Key";
./pkitool --server $SERVER

#Test clients
CLIENT1="Test_client1"
CLIENT2="Test_client2"

echo "Creating Testing Clients"
./pkitool $CLIENT1
./pkitool $CLIENT2

#Diffie-Hellman
./build-dh

#Setup config files
CONFIGS=/usr/share/doc/openvpn/examples/sample-config-files
cp $CONFIGS/server.conf.gz $DIR/
gzip -d $DIR/server.conf 
#rm $DIR/server.conf.gz

cp $CONFIGS/client.conf $DIR/client.conf

echo "Creating config files";
SERVER_CERT="$KEYS/$SERVER.crt";
SERVER_KEY="$KEYS/$SERVER.key";
DH=$KEYS"/dh2048.pem";

#server.conf
#CA
sudo sed -i -e 's,ca ca.crt,ca '"$KEYS/ca.crt"',g' $DIR/server.conf
sudo sed -i -e 's,cert server.crt,cert '"$SERVER_CERT"',g' $DIR/server.conf
sudo sed -i -e 's,key server.key,key '"$SERVER_KEY"',g' $DIR/server.conf
sudo sed -i -e 's,dh dh1024.pem,dh '"$DH"',g' $DIR/server.conf

#Logging
sudo sed -i -e 's,;log-append  openvpn.log,log-append  /var/log/openvpn.log,g' $DIR/server.conf

#client.conf
CLIENT1_CONF="$CLIENT1.conf";
CLIENT1_CERT="$CLIENT1.crt";
CLIENT1_KEY="$CLIENT1.key";

CLIENT2_CONF="$CLIENT2.conf";
CLIENT2_CERT="$CLIENT2.crt";
CLIENT2_KEY="$CLIENT2.key";

#Global config
#sudo sed -i -e 's,ca ca.crt,ca '"$CLIENT_CA"',g' $DIR/client.conf
sudo sed -i -e 's,remote my-server-1 1194,remote '"$SERVER_ADR"' '"$SERVER_PORT"',g' $DIR/client.conf

cp $DIR/client.conf $DIR/$CLIENT1_CONF;
cp $DIR/client.conf $DIR/$CLIENT2_CONF;

#client specific
sudo sed -i -e 's,cert client.crt,cert '"$CLIENT1_CERT"',g' $DIR/$CLIENT1_CONF
sudo sed -i -e 's,key client.key,key '"$CLIENT1_KEY"',g' $DIR/$CLIENT1_CONF

sudo sed -i -e 's,cert client.crt,cert '"$CLIENT2_CERT"',g' $DIR/$CLIENT2_CONF
sudo sed -i -e 's,key client.key,key '"$CLIENT2_KEY"',g' $DIR/$CLIENT2_CONF

#Exit
echo "Done!";
exit 0;


