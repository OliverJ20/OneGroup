#Imports
from passlib.hash import sha256_crypt
import hashlib
from datetime import datetime
import subprocess
import shlex
import os
import logging
import fileinput

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
        db.insert("users", {"Name" : "Test client1", "Email" : "client1@test.com", "Password" : sha256_crypt.hash("client1"), "Auth_Type" : "Password", "Account_Type" : "Client", "Keys" : "Test_client1", "Key_Distributed" : 0})
        db.insert("users", {"Name" : "Test client2", "Email" : "client2@test.com", "Password" : sha256_crypt.hash("client2"), "Auth_Type" : "Password", "Account_Type" : "Client", "Keys" : "Test_client2", "Key_Distributed" : 0})
        db.insert("users", {"Name" : "admin", "Email" : "admin@test.com", "Password" : sha256_crypt.hash("admin"), "Auth_Type" : "Password", "Account_Type" : "Admin", "Keys" : "admin", "Key_Distributed" : 0})

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

def loadIptables():
    """Retrieves the iptables rules from the database (if any) and applys those rules"""
    rules = getIptablesRules()

    #If there are no/not enough rules, use the defaults
    if rules == None or len(rules) != len(iptables):
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
def deleteUser(name):
    """
        Deletes a user and their keys from the database

        name  : User's name/username
    """
    db = Database(filename = filen)

    user = getUser("Name",name)
    
    #delete the users key/cert pair
    args = [
        "del",
        user["Keys"],
    ]
    callScript('userman',args)
    
    db.delete("users", user)
    db.close()
    return True

def createUser(name, passwd, email):
    """
        Creates a user entry in the database and generates key/cert pair

        name  : User's name/username
        passwd: User's password 
        email : User's email

        returns: true if successful, else false
    """
    #Connect to the database
    db = Database(filename = filen)

    #Create user dictonary for database
    user = {"Name" : name, "Email" : email, "Password": sha256_crypt.hash(passwd), "Auth_Type" : "Password", "Account_Type" : "Client", "Keys" : createUserFilename(name), "Key_Distributed" : 0}

    #Check if user exists (Check both username and email)
    if getUser("Name",user["Name"]) != None or getUser("Email",user["Email"]) != None:
        logging.error("Error creating user %s user exists",name)
        return False
    
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


def retrieveRequests(table):
    """
        Fetchs all active admin requests from the database

        table : Table to retrieve the requests from

        Returns : List of all admin requests
    """
    db = Database(filename = filen)
    requests =  db.retrieve(table)
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
    rule = retrieve('firewall',{"ID",ruleid})
    db.close()
    return rule


def ipDictToString(ip_dict):
    """
        Pass dictionary obtioned in webform to string
        
        Returns : String of dictionary values
    """
    
    ipRules = "iptables"
        table = ip_dict['Table']
        if not table=="":
            ipRules = ipRules + " -t " + table
            
        chain = ip_dict['Chain']
        if not chain=="":
            ipRules = ipRules + " -A " + chain

        interface = ip_dict['Interface']
        if not interface=="":
            ipRules = ipRules + " -i " + interface
            
        packType = ip_dict['Protocol']
        if not packType=="":
            ipRules = ipRules + " -p " + packType
        elif packType=="" and not port=="":
            ipRules = ipRules + " -p tcp"
            
        source = ip_dict['Source']
        if not source=="":
             ipRules = ipRules + " -s " + source
             
        destination = ip_dict['Destination']
        if not destination=="":
            ipRules = ipRules + " -d " + desination
            
        port = ip_dict['Port']
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
    for string in len(ipSplit):
        if ipString[string] == '-t':
            tableData= ipString[string+1]
        elif ipString[string] == '-A':
            chainData= ipString[string+1]
        elif ipString[string] == '-i':
            ifaceData= ipString[string+1]
        elif ipString[string] == '-p':
            protData= ipString[string+1]
        elif ipString[string] == '-s':
            source= ipString[string+1]
        elif ipString[string] == '-d':
            destination= ipString[string+1]
        elif ipString[string] == '-dport':
            port= ipString[string+1]
        elif ipString[string] == '-m':
            stateData= ipString[string+1]
        elif ipString[string] == '-j':
            actionData= ipString[string+1]

    return  ip_dict = {'Table': tableData, 'Chain': chainData, 'Interface': ifaceData, 'Protocol': protData,
                   'Source': source, 'Destination': destination,'Port': port, 'State':stateData, 'Action': actionData}


def updateIPRules(name, value)
    db = Database(filename=filen)
    user = getUser("Name", name)['ID']
    db.update("firewall", {"Rule": value}, ("ID", user))
    db.close()
                  
