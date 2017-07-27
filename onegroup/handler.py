#Imports
from passlib.hash import sha256_crypt
import subprocess
import shlex

try:
    from onegroup.db import Database
except:
    from db import Database

#Globals
filen = "OneGroup.db"       #Database
keys = "/etc/openvpn/keys/" #Key/Cert location

def init_database():
    """
        Initialises the test database if not created already
    """
    #Connect to the database
    db = Database(filename = filen)

    if len(db.retrieveAll("users")) == 0:
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

    user = db.retrieve("users", key, value)
    
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



def changePassword(userinput):
    """
    Changes user password in database
    
    :param userinput : user's desired password
    :return : 
    """
    db = Database(filename = filen)
    db.update("users", "Password", sha256_crypt.hash(userinput))
    db.close()
  
