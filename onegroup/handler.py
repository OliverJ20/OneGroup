#Imports
from passlib.hash import sha256_crypt
import hashlib
from datetime import datetime, timedelta
import subprocess
import shlex
import os
import logging
import fileinput
import re

#Database and constants
try:
    from onegroup.defaults import *
    from onegroup.db import Database
except:
    from defaults import *
    from db import Database

#Database
filen = database
if os.path.isdir(working_dir):
    filen = working_dir+"/"+database

#
# Config
#
def init_database():
    """Initialises the test database if not created already"""
    #Connect to the database
    db = Database(filename = filen)

    if db.retrieve("users") == None:
        #Insert test users
        db.insert("users", {"Name" : "Test client1", "Email" : "client1@test.com", "Password" : sha256_crypt.hash("client1"), "Auth_Type" : "Passphrase", "Account_Type" : "Client", "Keys" : "Test_client1", "Key_Distributed" : 0, "Grp" : -1, "Expiry": "2018-01-14:1200"})
        db.insert("users", {"Name" : "Test client2", "Email" : "client2@test.com", "Password" : sha256_crypt.hash("client2"), "Auth_Type" : "Passphrase", "Account_Type" : "Client", "Keys" : "Test_client2", "Key_Distributed" : 0, "Grp" : -1, "Expiry": "2018-01-14:1200"})
        db.insert("users", {"Name" : "admin", "Email" : "admin@test.com", "Password" : sha256_crypt.hash("admin"), "Auth_Type" : "Passphrase", "Account_Type" : "Admin", "Keys" : "admin", "Key_Distributed" : 0, "Grp" : -1, "Expiry": "2018-01-14:1200"})
        db.insert("users", {"Name" : "Newadmin", "Email" : "newadmin@test.com", "Password" : sha256_crypt.hash("new"), "Auth_Type" : "Passphrase", "Account_Type" : "Admin", "Keys" : "admin", "Key_Distributed" : 0, "Grp" : -1, "Expiry": "2017-09-14:1700"})
        
        #Test group users
        db.insert("users", {"Name" : "Group01_1", "Email" : "one@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_1", "Key_Distributed" : 0, "Grp" : 1, "Expiry": "2018-01-14:1200"})
        db.insert("users", {"Name" : "Group01_2", "Email" : "two@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_2", "Key_Distributed" : 0, "Grp" : 1, "Expiry": "2018-01-14:1200"})
        db.insert("users", {"Name" : "Group01_3", "Email" : "three@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_3", "Key_Distributed" : 0, "Grp" : 1, "Expiry": "2018-01-14:1200"})
        db.insert("users", {"Name" : "Group01_4", "Email" : "four@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_4", "Key_Distributed" : 0, "Grp" : 1, "Expiry": "2018-01-14:1200"})

    if db.retrieve("groups") == None:
        db.insert("groups",{"Name" : "Group01", "Internal" : "10.8.1.0/24", "External" : "192.168.3.0/24", "Used_Octets" : "1,2,4,5"})
        db.insert("groups",{"Name" : "Group02", "Internal" : "10.9.1.0/24", "External" : "192.128.3.0/24", "Used_Octets" : "1,2,4,5"})

    
    #Close database
    db.close()


def loadConfig():
    """Reads a config file and sets environment variables"""
    #base config dictonary 
    config = base_config
    
    #Find config file
    confFile = config_file
    if os.path.exists(config_path_main):
        confFile = config_path_main
    elif os.path.exists(config_path_backup): 
        confFile = config_path_backup

    #Read in config
    try:
        with fileinput.input(files=confFile) as f:
            for line in f:
                #Ignore new lines and comments
                if line == "" or line =="\n" or line[0] == "#":
                    continue
                else:
                    #split by '=' and store in tuple
                    key, val = line.split("=")
                    
                    #checks for empty values
                    if key == "":
                        logging.error("Error reading config at line %d: No key\n\t%s",f.lineno(),line)
                    elif val == "":
                        logging.error("Error reading config at line %d: No Value\n\t%s",f.lineno(),line)
                    #check if the key is a valid key
                    elif key not in base_config.keys(): 
                        logging.error("Error reading config at line %d: Invalid Key\n\t%s",f.lineno(),line)
                    #else assign value for given key
                    else:
                        config[key] = val.strip("\n")
                    
                    
        #Assign Config to environment variables
        for key in config:
            os.environ[tag+key] = config[key]

    except Exception as e:
        logging.error("Error reading config at line %s",e)

    loadIptables()


def loadIptables():
    """Retrieves the iptables rules from the database (if any) and applys those rules"""
    rules = getIptablesRules()

    #If there are no/not enough rules, use the defaults
    if rules == None or len(rules) < len(iptables):
        rules = iptables
        
        #Add the defaults to the database
        db = Database(filename = filen)
        db.runSQL('DELETE FROM firewall')
        for rule in rules:
            db.insert("firewall",rule)

        db.close()
          
    #Extract rules and add the correct prefix
    ruleStrings = []
    for rule in rules:
        if rule["Policy"]:
            ruleStrings.append("'-P "+rule["Rule"]+"'")
        else: 
            ruleStrings.append("'-A "+rule["Rule"]+"'")

    #Apply rules
    callScript('tabler',ruleStrings)
    
        
#
# User Methods
#
def getUsers():
    """
        Fetchs all users from the database

        Returns : List of all admin requests
    """
    db = Database(filename = filen)
    users = db.retrieve("users")
    db.close()
    return users


def getUser(key, value):
    """
        Gets a user from the database based on a single key/value pair

        key   : The field to indentify the user by
        value : The value to indentify the user by

        Returns : dict the user's database entry

    """
    db = Database(filename = filen)

    user = db.retrieve("users", {key : value})
    
    db.close()
    
    return user


def deleteUser(ID):
    """
        Deletes a user and their keys from the database

        ID  : User's database ID
    """
    db = Database(filename = filen)

    user = getUser("ID",ID)
 
    #delete the users key/cert pair
    args = [
        "del",
        user["Keys"],
    ]
    callScript('userman',args)
     
    db.delete("users", {"ID" : ID})
    db.close()

    return True


def createUser(name, accountType, authType, email = '', passwd = '', group = -1, expiry= ''):

    """
        Creates a user entry in the database and generates key/cert pair

        name        : User's name/username
        accountType : The account type of the user (Client, Admin)
        authType    : The authorisation type of the user (Passphrase, Email, None) (Admin must use Passphrase) 
        email       : User's email (blank if not set. Cannot be set if authType is None)
        passwd      : User's password (blank if not set. Can only be set if authType is Passphrase. Admin must use a password)
        group       : User's group (-1 meaning no group) 

        returns: true if successful, else false
    """
    #Connect to the database
    db = Database(filename = filen)

    #Error checking
    if not validateNewUser(name, accountType, authType, email, passwd, expiry):   
        return False

    #Create user dictonary for database
    password = sha256_crypt.hash(passwd) if passwd != '' else passwd 
    user = {"Name" : name, "Email" : email, "Password": password, "Auth_Type" : authType, "Account_Type" : accountType, "Keys" : createUserFilename(name), "Key_Distributed" : 0, "Grp" : group, "Expiry": expiry}
 
    #create the users key/cert pair
    args = [
        "add",
        user["Keys"],
    ]
    callScript('userman',args)
    #subprocess.call(shlex.split('user_gen.sh {}'.format(user["Keys"])))

    #Add user to the database
    db.insert("users",user)

    #close database connection and exit
    db.close()
    return True
          
def updateUser(ID, username, email, authtype, accounttype, group, expiry):
    """
        Updates the information of a specified user from the users table

        ID : ID field of user as specified in the database
        username : of the user
        email : of the user
        authtype : of the user
        accounttype : of the user
        group : user's group

        Returns True if successful else false
    """
    #Error checking
    if not validateNewUser(name, accountType, authType, email, passwd, expiry):   
        return False
    else:
        oldUser = getUser("ID",ID)

        #Check New username isn't used
        if oldUser["Name"] != username and getUser("Name", username) != None:
            return False
        #Check new email isn't used
        elif oldUser["Email"] != email and getUser("Name", email) != None:
            return False

    #Update user data
    db = Database(filename=filen)
    try:
        db.update("users", {"Name" : username, "Email" : email, "Auth_Type" : authtype, "Account_Type" : accounttype, "Grp" : group, "Expiry": expiry}, ("ID", ID))
    except:
        db.close()
        return False

    db.close()
    return True

def validateNewUser(name, accountType, authType, email, passwd, expiry, existing = True):
    """
        Checks entered form data for invalid data specified below

        name        : User's name/username
        accountType : The account type of the user (Client, Admin)
        authType    : The authorisation type of the user (Passphrase, Email, None) (Admin must use Passphrase) 
        email       : User's email (blank if not set. Cannot be set if authType is None)
        passwd      : User's password (blank if not set. Can only be set if authType is Passphrase. Admin must use a password)
        existing    : Flag to perform checks for existing username and email

        returns: true if valid, else false
    """
    #Invalid account type
    if accountType not in ["Client","Admin"]:
        logging.error("Error validating user %s invalid account type: %s",name,accountType)
        return False
    #Invalid authentication type
    elif authType not in ["Passphrase","Email","None"]:
        logging.error("Error validating user %s invalid authentication type: %s",name,authType)
        return False
    
    #Admin account but not passphrase authentication 
    elif accountType == "Admin" and authType != "Passphrase":
        logging.error("Error validating user %s attempted to make an Admin account without a passphrase",name)
        return False
    
    #Email not set
    elif email == '' and authType != "None": 
        logging.error("Error validating user %s Email not set for authentication type: %s",name,accountType)
        return False
    #Email incorrectly set
    elif email != '' and authType == "None":
        logging.error("Error validating user %s Email set for authentication type None",name,accountType)
        return False
    
    #Password not set
    elif passwd == '' and authType == "Passphrase": 
        logging.error("Error validating user %s Password not set for authentication type Passphrase",name)
        return False
    #Password incorrectly set
    elif passwd != '' and authType != "Passphrase":
        logging.error("Error validating user %s Password set for authentication type: %s",name,accountType)
        return False
    #Expiry incorrectly set
    elif expiry == 'test':
        logging.error("Error validating user %s Expiry set for authentication type: %s",name,expiry)
        return False
    #Name already exists
    if existing:
        if getUser("Name",user["Name"]) != None:
            logging.error("Error validating user %s Name in use",name)
            return False
        #Email already in use
        elif authType != "None" and getUser("Email",user["Email"]) != None: 
            logging.error("Error validating user %s Email in use",name)
            return False
    
    #Form data is correct
    return True


def zipUserKeys(user):
    """
        creates a zip file with the client's key/cert pair

        user : the filename of the client
    """
    #create the users key/cert pair
    args = [
        "dist",
        user,
    ]
    callScript('userman',args)
    #subprocess.call(shlex.split('user_dist.sh {}'.format(user)))


def checkExpiredKeys():
    """
        Checks all the keys in the database to see if they have expired. If so, remove them
    """
    now = datetime.now()
    for user in getUsers():
        #If the user's key doesn't expire, skip
        if user["Expiry"] == "":
            continue

        #If expired, delete the keys
        expire = datetime.strptime(user["Expiry"],"%Y-%m-%d:%H%M")   
        if expire > now:
            #Check setting to determine if the user should be deleted on key expiration 
            if os.getenv(tag+'delete_on_expire',base_config['delete_on_expire']).lower() == "true":
                deleteUser(user["ID"])
            else:
                args = [
                    "del",
                    user["Keys"],
                    ]
                callScript('userman',args)


def createUserFilename(name):
    """
        Creates a filename for the user's key and cert based on specific rules

        name : name of the user

        Returns : the generated filename for the user
    """

    #Filenames must follow the following rules
    # - All spaces must be underscores
    # - Illegal chars: '$','!','.'  
    #

    #illegal chars list
    illegal = ['$','!','.']

    #replace spaces
    userFilen = name.replace(" ","_")

    #replace illegal characters
    for char in illegal:
        userFilen = userFilen.replace(char,"")
    
    return userFilen


def confirmLogin(email, password):
    """
        Confirms if the entered login credentials are correct
    
        email: user's email address
        password: user's associated password
        
        Returns : True if both email is found in the database and associated password matches. 
                  False if either condition fails
    """
    if confirmUser(email):
        user = getUser("Email",email)

        if sha256_crypt.verify(password, user['Password']):
            return True
        
    else:
        return False


def confirmClient(email):
    """
        Confirms if the user account is of the client user type
    
        email : user's email address
        
        Returns : True if client, else false
    """
    user = getUser("Email",email)

    if user['Account_Type'] == "Client":
        return True
    else:
        return False


def confirmUser(email):
    """
        Confirms if the user exists in the database
    
        email : user's email address
        
        Returns : True if exists, else False
    """
    user = getUser("Email",email)

    if user is not None:
        return True
    else:
        return False


#
# Group methods
#
def getAllGroups():
    """
        Retrieves all the groups in the database

        Returns list of groups represented as dictonaries
    """
    db = Database(filename = filen)
    groups = db.retrieve("groups")
    db.close()
    return groups


def getGroup(group):
    """
        Retrieves a group's information and all it's users

        group : Group's database ID

        Returns dict of the group containing users
    """
    db = Database(filename = filen)
    grp = db.retrieve("groups",{"ID" : group})
    
    #Get the users in the group
    grp["Users"] = getUsersInGroup(group) 
     
    db.close()
    return grp


def getUsersInGroup(group):
    """
        Returns a list of all the users in the group

        group : Group's database ID

        Returns list of user dictonaries
    """
    db = Database(filename = filen)
    users = db.retrieve("users",{"Grp":group})
    db.close()

    #Check if empty of single user
    if users == None:
        users = []
    elif isinstance(users,dict):   
        users = [users]

    return users


def createGroup(name, internalNetwork, externalNetwork, **kwargs):
    """
        Adds a database record of a group and creates the firewall rule for the group

        name : New group's name
        internalNetwork : Network address space of the interal network using slash notation (Eg. 10.8.1.0/24)
        ExternalNetwork : Network address space of the External network using slash notation (Eg. 192.168.1.0/24)

        Keyword args:
        genUsers : Boolean to determine if users should be made for the group
        numUsers : Number of users to be generated for the group. Is not checked if genUsers is False
    """
    #Create database entry
    db = Database(filename = filen)
    group = {"Name" : name, "Internal" : internalNetwork, "External" : externalNetwork, "Used_Octets" : ""}

    #Add route to the server config if not already added
    addRouteToConfig(internalNetwork)

    #Setup IPTables rule
    rule = ipDictToString({"Table": "","Chain": "FORWARD","Input": "tun0","Output": "", "Protocol": "","Source" : internalNetwork,"Source_Port": "", "Destination": externalNetwork,"Destination_Port": "","State": "","Action": "ACCEPT"})
    addIPRule(rule)
    group["Rule"] = db.retrieve("firewall",{"Rule":rule})["ID"]

    #Add group to the database
    db.insert("groups",group)

    #If specified, create users for the group
    if kwargs.get("genUsers",False):
        grp = db.retrieve("groups",group)["ID"]
        
        for i in range(kwargs.get("numUsers")):
            #Create new user
            #TODO Polymorph create user to support auto generated users
            username = "{}_{}".format(name,i+1)
            email = "{}@test.com".format(username)
            createUser(username, "AAAAAAAAAAA", email, group = grp)
            
            #Get new user ID and add user to the group
            user = getUser("Name",username)["ID"]
            addUserToGroup(user, grp)
    db.close()
    return True

def updateGroup(ID, group):
    """
        Edits a group's database entry and the appropriate iptables and user settings

        NOTE: ID and Rule fields cannot be changed

        ID : Group's database ID
        group : Dictonary containing the new values for that group
    """
    db = Database(filename = filen)
    oldGroup = getGroup(ID)

    #Checks a new IPTables rule is required 
    if ("Internal" in group and group["Internal"] != oldGroup["Internal"]) or ("External" in group and group["External"] != oldGroup["External"]):
        
        #Update IPTables rule
        rule = ipStringToDict(getRule(oldGroup["Rule"]))
        if "Internal" in group:
            rule["Source"] = group["Internal"]
            
        if "External" in group:
            rule["Destination"] = group["External"]

        updateIPRule(oldGroup["Rule"],ipDictToString(rule))

        #Update server route in server config
        if "Internal" in group and group["Internal"] != oldGroup["Internal"]: 
            updateRouteInConfig(oldGroup["Internal"],group["Internal"])

        #Update all the user's client configs
        for user in getUsersInGroup(ID):
            #Get the current client config for the user
            config = getUserClientConfig(user["Keys"])
            if config != None:
                internal = "{}.{}".format(rule["Source"].split(".0/")[0],config[0].split(".")[-1])
                external = "{}.{}".format(rule["Source"].split(".0/")[0],config[1].split(".")[-1])
                updateUserClientConfig(user["Keys"],internal,external)

    #Removed ID and Rule fields
    del group["ID"]
    del group["Rule"]
    del group["Users"]
 
    #Update Group entry
    db.update("groups",group,("ID",ID))
    db.close()


def deleteGroup(group,deleteUsers = False):
    """
        Deletes a group from the database and users if specified

        group : The group ID of the group to delete
        deleteUsers : Boolean flag to determine if the users of the group should be deleted as well
    """
    db = Database(filename = filen)

    #Delete the IPTables rule
    removeIPRule(getGroup(group)["Rule"])
    
    #Remove route from server config
    deleteRouteInConfig(group["Internal"])

    #Delete group entry
    db.delete("groups",{"ID" : group})
    db.close()

    #Delete user if deleteUsers == True, else just remove them from the group
    for user in getUserInGroup(group):
        if deleteUsers:
            deleteUser(user["ID"])        
        else:
            deleteUserFromGroup(user["ID"])


def addUserToGroup(user, group):
    """
        Adds a user to a group and sets up their client config for that group

        user  : The user's ID of the user to be added to the group
        group : Group ID of the group to add the user to
    """
    #Get the used octets for the group
    grp = getGroup(group)  
    used = grp["Used_Octets"].split()        
    
    #Setup base addresse
    base = grp["Internal"].split("/")[0].split(".0")[0]

    #Determine endpoint pair to use
    if used == "":
        pair = usable_octets[0]
        internal = "{}.{}".format(internal,pair[0])
        external = "{}.{}".format(external,pair[1])
        grp["Used_Octets"] = "{},{}".format(pair[0],pair[1])
    else: 
        for pair in usable_octets:
            strPair = "{},{}".format(pair[0],pair[1])
            if strPair not in used:
                internal = "{}.{}".format(base,pair[0])
                external = "{}.{}".format(base,pair[1])
                grp["Used_Octets"] = "{} {}".format(grp["Used_Octets"],strPair)
                break

    #Setup client config file
    usr = getUser("ID",user)
    updateUserClientConfig(usr["Keys"],internal,external)

    #Update the group's entry to show the used octets
    updateGroup(group,grp)


def getUserClientConfig(user):
    """
        Reads the users client config and returns their internal and external IP addresses

        user : The user's key name

        Returns : String tuple (Internal,External) or None if the user has no config
    """
    ccf = os.getenv(tag+'openvpn_ccd',base_config['openvpn_ccd'])+"{}".format(user)
    with open(ccf,'r') as f:
        config = f.readline().split()
    
    if len(config) != 3:
        return None

    return (config[1],config[2])


def updateUserClientConfig(user, source, destination):
    """ 
        Updates s user's client configuration file. Created file if it doesn't exist

        user : The user's key name
        source : The internal network address for the user
        destination : The external network address for the user
    """
    ccf = os.getenv(tag+'openvpn_ccd',base_config['openvpn_ccd'])+"{}".format(user)
    with open(ccf,'w') as f:
        f.write("ifconfig-push {} {}".format(source,destination))
    

def deleteUserFromGroup(userID):
    """
        Removes a user from a group and resets their client config

        userID : The user's ID of the user to be removed to the group
    """
    #Change user's Group entry in the database
    user = getUser("ID",userID)
    updateUser(userID, user["Name"], user["Email"], user["Auth_Type"], user["Account_Type"], -1) 
    
    #Remove the user's client config filei
    args = [
        os.getenv(tag+'openvpn_ccd',base_config['openvpn_ccd'])+"{}".format(user["Keys"]),
    ]
    callScript('rm',args)


def addRouteToConfig(network):
    """
        Adds a new route to the openvpn server config
        
        network : The network to push the route for
    """
    #Get Formatted network
    formattedNetwork = getFormattedNetwork(network) 

    #Check if the line already exists
    #if so, do nothing, else add it to the config
    line = checkRouteExists(network,formattedNetwork) 
    if line == -1: 
        filename = os.getenv(tag+'openvpn_server_config',base_config['openvpn_server_config']) 
        with open(filename,'r+') as f:
            config = f.readlines()
            #Check if onegroup additions section has been added
            if commentStart+"\n" in config:
                endLine = congfig.index(commentEnd+"\n")
                config.insert(endLine,"{} {}".format("route",formattedNetwork))
            #Else add section
            else:
                config.append("")
                config.append(commentStart)
                config.append("{} {}".format("route",formattedNetwork))
                config.append(commentEnd)

            #Rewrite config file
            f.seek(0)
            for i in config:
                i.strip()
                f.write(i)

        #Restart openvpn to enact changes
        handleOpenvpn("restart")


def updateRouteInConfig(oldNetwork,newNetwork):
    """
        Updates an existing route in the openvpn server config
        
        oldNetwork : The existing network route in the config
        newNetwork : The network route to replace the existing route
    """
    #Find the existing route in the file
    #If the route doesn't exist, add it to the config
    line = checkRouteExists(oldNetwork,getFormattedNetwork(oldNetwork)) 
    if line == -1:
        addRouteToConfig(newNetwork)
    else:
        filename = os.getenv(tag+'openvpn_server_config',base_config['openvpn_server_config']) 
        with open(filename,'r+') as f:
            config = f.readlines()
            #Check if new network already exists for safety
            newNetworkFmt = getFormattedNetwork(newNetwork)
            if checkRouteExists(newNetwork,newNetworkFmt) != -1:
                #Just remove the old network as the new one exists
                config.remove(config[line])
            else:
                config[line] = getFormattedNetwork(newNetwork)
            
            #Rewrite config file
            f.seek(0)
            for i in config:
                i.strip()
                f.write(i)

    #Restart openvpn to enact changes
    handleOpenvpn("restart")


def deleteRouteInConfig(network):
    """
        Deletes a route from the openvpn server config
        
        network : The network to delete the route for
    """
    #Get Formatted network
    formattedNetwork = getFormattedNetwork(network) 

    #Check if the line exists
    #if so, delete it, else do nothing
    line = checkRouteExists(network,formattedNetwork) 
    if line != -1: 
        filename = os.getenv(tag+'openvpn_server_config',base_config['openvpn_server_config']) 
        with open(filename,'r+') as f:
            config = f.readlines()
            config.remove(config[line])

            #Rewrite config file
            f.seek(0)
            for i in config:
                i.strip()
                f.write(i)

        #Restart openvpn to enact changes
        handleOpenvpn("restart")


def checkRouteExists(network,formattedNetwork):
    """
        Checks if a route for a network already exists in the config

        network : the network in slash notation (Eg 10.8.1.0/24)
        formattedNetwork : network but as a string with seperated netmask (Eg 10.8.1.0 255.255.255.0)

        Returns line number if found, else -1
    """
    #Make comparison list
    compare = ["route {}".format(network),"route {}".format(formattedNetwork)]

    #Iterate over file
    filename = os.getenv(tag+'openvpn_server_config',base_config['openvpn_server_config']) 
    with open(filename) as f:
        for num, line in enumerate(f,1):
            if any([x for x in compare if x == line]):
                return num

    #If reached here, the route is not in the file
    return -1


def getFormattedNetwork(network):
    """
        Takes a network address and returns a string in the format of ADDRESS NETMASK

        network : network in slash notation (Eg 10.8.1.0/24)

        Returns string in the format of ADDRESS NETMASK 
    """
    #Split network into address and subnet mask
    address = network.split("/")
    if len(address) == 2:
        maskbit = address[1]
        address = address[0]
    else:
        maskbit = 0
    
    #TODO Support more netmask other than /0 and /24
    if maskbit == 0:
        mask = "0.0.0.0"
    else:
        mask = "255.255.255.0"

    return "{} {}".format(address, mask)


def genUrl(user,purpose):
    """
        Generates a unique URL for password reset and fecthing keys

        user    : The user who owns the url
        purpose : The reason the url is being made 

        Returns : fully formed url
    """
    db = Database(filename = filen)

    #Create row to insert into the database
    row = {"Name" : user, "Purpose" : purpose, "Used" : 0}
    row["Code"] = genCode(user)
    
    db.insert("codes",row)
   
    db.close()
    
    #Create url
    if purpose == "Password":
        url = "/reset/{}".format(row["Code"])
    else:
        url = "/keys/{}".format(row["Code"])

    return url


def genCode(user):
    """
        Generates a unique code to be used with URLS

        user : the user to generate the code for

        Returns : created code
    """
    secret = "{}{}".format(user,datetime.now().strftime("%Y%m%d%H%M%S%f"))
    return hashlib.sha512(secret.encode('UTF-8')).hexdigest()


def checkCode(code,purpose):
    """
        Checks if a code exists and is for the right purpose

        code    : the code to check
        purpose : the intended use for the code

        Returns : True if correct, else False
    """
    db = Database(filename = filen)
    row = db.retrieve("codes",{"Code" : code, "Purpose" : purpose})
    db.close()

    if isinstance(row,dict) and not row["Used"]:
        return True
    else:
        return False


def getUserFromCode(code):
    """
        Get a user from their unique code

        code : unique code

        Returns : username
    """
    db = Database(filename = filen)
    user = db.retrieve("codes",{"Code" : code})
    db.close()

    return user['Name']


def flagCode(code):
    """
        Mark a code as used

        code : unique code
    """
    db = Database(filename = filen)
    code = db.retrieve("codes",{"Code" : code})
    db.update("codes",{"Used" : 1},("Code",str(code)))
    db.close()


def changePassword(name, userinput):
    """
        Changes user password in database
        
        email : user's identifying email
        userinput : user's desired password 
    """
    db = Database(filename = filen)
    user = getUser("Name",name)['ID']
    db.update("users", {"Password": sha256_crypt.hash(userinput)}, ("ID", user))
    db.close()


def retrieveRequests():
    """
        Fetchs all active admin requests from the database

        Returns : List of all admin requests
    """
    db = Database(filename = filen)
    requests =  db.retrieve("notifications")
    db.close()
    return requests


def acceptRequest(reqName):
    """
        Performs the accepted request
    
        reqName : The request to perform

        Returns : True if the request was succesfully performed. Else False
    """
    return True


def declineRequest(reqName):#, reqReq):
    """
        Deletes a request from the database without additional action
    
        reqName : The request to delete

        Returns : True if the request was succesfully deleted. Else False
    """
    db = Database(filename = filen)
    db.delete("notifications",{"Users":reqName})
    #db.delete("notifications", "Request", reqReq)
    db.close()
    return True


# Work in Progress
# def retrieveFlags(name):
#     db = Database(filename = filen)
#     flag =  db.retrieve("users",{})
#     db.close()
#     return flag


def checkDistributeFlag(name):
    """
        Checks key distributed value in database

        name : user's identifying name
        Returns : True if key has not been set to 1, Else False
    """
    flag = getUser("Name", name)['Key_Distributed']
    return flag == 1


def keyDistributeFlag(name):
    """
        Changes key disrutbted value in database

        name : user's identifying name
    """
    db = Database(filename=filen)
    user = getUser("Name", name)['ID']
    db.update("users", {"Key_Distributed": 1}, ("ID", user))
    db.close()


def getLog(filepath):
    """
        Retrieves log file from specified path

        filepath : file path to log file
        Returns : list of strings containing logs contents
    """
    log = []
    try:
        with open(filepath) as f:
            for line in f:
                log.append(line.replace("\n", ""))
    except: 
        return None
    return log
    

def callScript(script, params = []):
    """
        Determine the location of the script and calls it
        
        script : file name of the script to call without path
        params : parameters to pass to the script
    """
    #Determine if the script dir exists, else use local path
    if os.path.exists("scripts/"):
        call = "scripts/"+script
    else:
        call = script

    #loop over parameters if any
    for arg in params:
        call += " {}".format(arg)
   
    #shlex doesn't work with more than 1 arguments
    #if len(params) == 1:
    subprocess.call(call,shell=True)
    #else:
    #    subprocess.call(shlex.split(call),shell=True)


def handleOpenvpn(action):
    """
        Makes a call to the openvpn service

        action : Action to perform on the openvpn server

        valid actions:
            start
            stop
            restart
    """
    #Check if action valid
    if action not in ["start","stop","restart"]:
        logging.error("Invalid action passed to openvpn service")
    
    call = "systemctl {} openvpn".format(action)
    subprocess.call(call,shell=True)


#TODO replace checkdistributedflag with this
def validateKeysDownloaded(username):
    """
        Return the value of Key_Distributed for a specific user in the user's table
    
        username : the name of the user to validate keys are downloaded
        Returns : 1 (TRUE), 0 (FALSE) corresponding to value set in database table
    """
    return getUser("Name", username)["Key_Distributed"]


def createRequest(username, requestType):
    """
        Creates a new admin request 
    
        username : User who made the request
        requestType : Requested action 

        Returns : The id of the new request
    """
    db = Database(filename=filen)
    db.insert("notifications", { "User" : username, "Request" : requestType })
    db.close()
    requestedId = db.retrieve("notifications", { "User" : username, "Request" : requestType })['ID']
    return requestedId
    
    
def getAdminEmails():
    """
        Gets the emails of all the admins
    
        Returns : A list of all the admin's emails in the database
    """
    db = Database(filename=filen)

    emails = retrieve('users', {"Account_Type" : "Admin"})

    #get all emails where account_type is "Admin"

    db.close()
    return [x["Email"] for x in emails]


#
# Iptables commands
#
def getIptablesRules():
    """
        Gets all the iptables rules from the database

        toDict : Flag to convert all the rules to dictonaries

        Returns: List of all iptables in the following dictonary format:
            ID : Row ID
            Rule : The rule in text form
            Policy : 1 if a policy rule, else 0
    """
    db = Database(filename=filen)
    rules = db.retrieve('firewall')
    db.close()
    return rules


def getRule(ruleid):
    """
        Gets the specified iptables rule from the database

        Returns: the given rule
    """
    db = Database(filename=filen)
    rule = db.retrieve('firewall',{"ID" : ruleid})
    rule["Rule"] = ipStringToDict(rule["Rule"])
    db.close()
    return rule


def ipDictToString(ip_dict):
    """
        Pass dictionary obtioned in webform to string
        
        Returns : String of dictionary values
    """
    table =""
    inputFace =""
    outputFace =""
    packType =""
    source =""
    sourceport =""
    destination =""
    port =""
    state =""
    action =""
    
    if len(ip_dict) == 2:
        ipRules = " -A " + ip_dict['CHAIN']
        ipRules = ipRules + " -j " + ip_dict['ACTION']
    else:
        ipRules = ip_dict['Chain']
        
        table = ip_dict['Table']
        if not table=="":
            ipRules = ipRules + " -t " + table
            
        #chain = ip_dict['CHAIN']
        #if not chain=="":
        #    ipRules = ipRules + " -A " + chain

        inputFace = ip_dict['Input']
        if not inputFace=="":
            ipRules = ipRules + " -i " + inputFace

        outputFace = ip_dict['Output']
        if not outputFace=="":
            ipRules = ipRules + " -o " + outputFace
            
        packType = ip_dict['Protocol']
        if not packType=="":
            ipRules = ipRules + " -p " + packType

        elif packType=="" and port=="":
            ipRules = ipRules + " -p tcp"
            
        source = ip_dict['Source']
        if not source=="":
             ipRules = ipRules + " -s " + source

        sourceport = ip_dict['Source_Port']
        if not sourceport=="":
             ipRules = ipRules + " -sport " + sourceport
             
        destination = ip_dict['Destination']
        if not destination=="":
            ipRules = ipRules + " -d " + destination
            
        port = ip_dict['Destination_Port']
        if not port=="":
            ipRules = ipRules + " -dport " + port

        state = ip_dict['State']
        if not state =="":
            ipRules = ipRules + " -m " + state
              
        action = ip_dict['Action']
        if not action=="":
            ipRules = ipRules + " -j " + action
            
    return ipRules


def ipStringToDict(ipString):
    """
        Pass String obtioned in webform to string
        
        Returns : Dictionary of values
    """
    ipSplit = ipString.split()
    
    #If ipSplit is only 2 words, it's a policy rule
    if len(ipSplit) == 2:
        ipDict = {"Chain" : ipSplit[0], "Action" : ipSplit[1]}
    #Else it's a full rule
    else:
        tableData =''
        chainData = ipSplit[0]
        ifaceData =''
        oufaceData =''
        protData =''
        source =''
        sourceport=''
        destination =''
        port =''
        stateData =''
        actionData =''
        for index in range(0, len(ipSplit)):
            if ipSplit[index] == '-t':
                tableData= ipSplit[index+1]
            #elif ipSplit[index] == '-A':
            #    chainData= ipSplit[index+1]
            elif ipSplit[index] == '-i':
                ifaceData= ipSplit[index+1]
            elif ipSplit[index] == '-o':
                oufaceData= ipSplit[index+1]
            elif ipSplit[index] == '-p':
                protData= ipSplit[index+1]
            elif ipSplit[index] == '-s':
                source= ipSplit[index+1]
            elif ipSplit[index] == '--sport':
                sourceport= ipSplit[index+1]
            elif ipSplit[index] == '-d':
                destination= ipSplit[index+1]
            elif ipSplit[index] == '--dport':
                port= ipSplit[index+1]
            elif ipSplit[index] == '-m':
                stateData= ipSplit[index+1]
            elif ipSplit[index] == '-j':
                actionData= ipSplit[index+1]

        ipDict = {'Table': tableData, 'Chain': chainData, 'Input': ifaceData, 'Output': oufaceData, 'Protocol': protData,
                       'Source': source, 'Source_Port': sourceport, 'Destination': destination,'Destination_Port': port, 'State':stateData, 'Action': actionData}
    
    return ipDict


def addIPRule(rule):
    """ 
        Adds a new IPTables rule to the database

        rule : The string representation of the rule
    """
    db = Database(filename=filen)
    db.insert("firewall", {"Rule": rule})
    db.close()

    #Apply new rule
    loadIptables()



def updateIPRules(ID, value):
    """ 
        Updates an IPTables rule entry in the database

        ID : ID of the rule
        value : The new rule string
    """
    db = Database(filename=filen)
    db.update("firewall", {"Rule": value}, ("ID", ID))
    db.close()

    #Apply new rules
    loadIptables()


def removeIPRules(ID):
    """ 
        Removes and IPTables rule from the database and updates the current rules on the system

        ID : ID of the rule
    """
    db = Database(filename=filen)
    db.delete("firewall", {"ID", ID})
    db.close()

    #Apply new rules
    loadIptables()


def logDownload(startDate,endDate):
    """
        Creates a new log file with entries between the start and end dates

        startDate : String starting date for the log
        endDate : String ending date for the log

        Returns : The the filepath to the new logfile 
    """
    print(log_dir)
    logs = getLog(log_dir+"openvpn.log")
    
    #Error check the logfile
    if logs == None:
        return None

    #Create datetime objects
    datefmt = "%Y-%m-%d"
    start = datetime.strptime(startDate,datefmt)        
    end = datetime.strptime(endDate,datefmt)        

    #Loop over the log file and grab entries between the start and end dates
    newLog = []
    started = False
    datematch = re.compile("[A-Za-z]{3} [A-Za-z]{3} [ 0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2} [0-9]{4} ")
    for row in logs:
        print(row)
        match = datematch.match(row)
        if match == None:    
            datestr = ""
        else:
            datestr = str(match.group()[:-1])
        
        print(datestr)
        #Handle no date specified
        if len(datestr) == 0:
            #Date is set to before the starting date to fail the first if condition
            date = start - timedelta(days = 1)
        else:
            date = datetime.strptime(datestr,"%a %b %d %H:%M:%S %Y")
        
        #If date falls between the start and end dates OR no date is specified but is within the two dates
        if (start < date and date < end) or (datestr == "" and started):
            newLog.append(row)
            
            if not started:
                started = False

        #Else check if the end date has been passed
        elif date > end:
            break

    #Write the log to the file
    now = datetime.now().strftime("%d%m%Y_%H%M%S")
    newLogFile = os.getenv(tag+'working_dir',working_dir)+"/openvpn_{}.log".format(now)
    with open(newLogFile,'w') as f:
        for row in newLog:
            f.write(row+"\n")

    #return the new filepath
    return newLogFile






