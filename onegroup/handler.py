#Imports
from passlib.hash import sha256_crypt
import hashlib
from datetime import datetime
import subprocess
import shlex
import os.path

try:
    from onegroup.db import Database
except:
    from db import Database

#Globals
workingDir = "/usr/local/onegroup"

filen = "OneGroup.db"       #Database
if os.path.isdir(workingDir):
    filen = workingDir+"/OneGroup.db"       #Database

keys = "/etc/openvpn/keys/" #Key/Cert location

def init_database():
    """
        Initialises the test database if not created already
    """
    #Connect to the database
    db = Database(filename = filen)

    if db.retrieve("users") == None:
        #Insert test users
        db.insert("users", {"Name" : "Test client1", "Email" : "client1@test.com", "Password" : sha256_crypt.hash("client1"), "Auth_Type" : "Password", "Account_Type" : "Client", "Keys" : "Test_client1", "Key_Distributed" : 0})
        db.insert("users", {"Name" : "Test client2", "Email" : "client2@test.com", "Password" : sha256_crypt.hash("client2"), "Auth_Type" : "Password", "Account_Type" : "Client", "Keys" : "Test_client2", "Key_Distributed" : 0})
        db.insert("users", {"Name" : "admin", "Email" : "admin@test.com", "Password" : sha256_crypt.hash("admin"), "Auth_Type" : "Password", "Account_Type" : "Admin", "Keys" : "admin", "Key_Distributed" : 0})

    #Close database
    db.close()

#
# User Methods
#

def createUser(name, passwd, email):
    """
        Creates a user entry in the database and generates key/cert pair

        name  : str : User's name/username
        passwd: str : User's password 
        email : str : User's email
    """
    #Connect to the database
    db = Database(filename = filen)

    #Create user dictonary for database
    user = {"Name" : name, "Email" : email, "Password": sha256_crypt.hash(passwd), "Auth_Type" : "Password", "Account_Type" : "Client", "Keys" : createUserFilename(name), "Key_Distributed" : 0}

    #create the users key/cert pair
    subprocess.call(shlex.split('scripts/user_gen.sh {}'.format(user["Keys"])))

    #Add user to the database
    db.insert("users",user)

    #close database connection
    db.close()
          

def zipUserKeys(user):
    """
        creates a zip file with the client's key/cert pair

        user : str : the filename of the client
    """
    #create the users key/cert pair
    subprocess.call(shlex.split('scripts/user_dist.sh {}'.format(user)))



def createUserFilename(name):
    """
        Creates a filename for the user's key and cert based on specific rules

        :param name : str : name of the user

        :returns userFile : str : the generated filename for the user
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

        key   : str : The field to indentify the user by
        value : str : The value to indentify the user by

        returns dict the user's database entry

    """
    db = Database(filename = filen)

    user = db.retrieve("users", {key : value})
    
    db.close()
    
    return user



def confirmLogin(email, password):
    """
    
    
    :param email: user's email address
    :param password: user's associated password
    :return : boolean : True if both email is found in the database and associated password matches. 
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
    
    
    :param email : user's email address
    :return : 
    """

    user = getUser("Email",email)

    if user['Account_Type'] == "Client":
        return True
    else:
        return False


def confirmUser(email):

    user = getUser("Email",email)

    if user is not None:
        return True
    else:
        return False


def genUrl(user,purpose):
    """
        Generates a unique URL for password reset and fecthing keys

        user    : str : The user who owns the url
        purpose : str : The reason the url is being made 

        returns str fully formed url
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

        user : str : the user to generate the code for

        returns str code
    """
    secret = "{}{}".format(user,datetime.now().strftime("%Y%m%d%H%M%S%f"))
    return hashlib.sha512(secret.encode('UTF-8')).hexdigest()

def checkCode(code,purpose):
    """
        Checks if a code exists and is for the right purpose

        code    : str : the code to check
        purpose : str : the intended use for the code

        returns true if correct, else false
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

        code : str : unique code

        returns str user name
    """
    db = Database(filename = filen)
    user = db.retrieve("codes",{"Code" : code})
    db.close()

    return user['Name']


def flagCode(code):
    """
        Mark a code as used

        code : str : unique code
    """
    db = Database(filename = filen)
    code = db.retrieve("codes",{"Code" : code})
    db.update("codes",{"Used" : 1},("Code",str(code)))
    db.close()


def changePassword(name, userinput):
    """
    Changes user password in database
    
    :param email : user's identifying email
    :param userinput : user's desired password
    :return : 
    """
    db = Database(filename = filen)
    user = getUser("Name",name)['ID']
    db.update("users", {"Password": sha256_crypt.hash(userinput)}, ("ID", user))
    db.close() 
