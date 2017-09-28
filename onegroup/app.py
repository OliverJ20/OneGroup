import logging
import os
import fileinput

from apscheduler.schedulers.background import BackgroundScheduler

#Package imports
try:
    from onegroup.master import run_server as run_master
    from onegroup.slave import run_server as run_slave
    from onegroup.defaults import *
    from onegroup.handler import loadIptables, checkExpiredKeys
    from onegroup.db import Database
except:
    from master import run_server as run_master
    from slave import run_server as run_slave
    from defaults import *
    from handler import loadIptables, checkExpiredKeys
    from db import Database


#Scheduler 
sched = BackgroundScheduler()

filen = database
if os.path.isdir(working_dir):
    filen = working_dir+"/"+database


#
# Config
#
def init_database():
    """
        Initialises the test database if not created already
    
        filen : the location of the database files    
    """
    #Connect to the database
    db = Database(filename = filen)

    if db.retrieve("users") == None:
        #Insert test users
        db.insert("users", {"Name" : "Test client1", "Email" : "client1@test.com", "Password" : sha256_crypt.hash("client1"), "Auth_Type" : "Passphrase", "Account_Type" : "Client", "Keys" : "Test_client1", "Key_Distributed" : 0, "Grp" : -1, "Expiry": ""})
        db.insert("users", {"Name" : "Test client2", "Email" : "client2@test.com", "Password" : sha256_crypt.hash("client2"), "Auth_Type" : "Passphrase", "Account_Type" : "Client", "Keys" : "Test_client2", "Key_Distributed" : 0, "Grp" : -1, "Expiry": ""})
        db.insert("users", {"Name" : "admin", "Email" : "admin@test.com", "Password" : sha256_crypt.hash("admin"), "Auth_Type" : "Passphrase", "Account_Type" : "Admin", "Keys" : "admin", "Key_Distributed" : 0, "Grp" : -1, "Expiry": ""})
        
        #Test group users
        db.insert("users", {"Name" : "Group01_1", "Email" : "one@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_1", "Key_Distributed" : 0, "Grp" : 1, "Expiry": ""})
        db.insert("users", {"Name" : "Group01_2", "Email" : "two@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_2", "Key_Distributed" : 0, "Grp" : 1, "Expiry": ""})
        db.insert("users", {"Name" : "Group01_3", "Email" : "three@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_3", "Key_Distributed" : 0, "Grp" : 1, "Expiry": ""})
        db.insert("users", {"Name" : "Group01_4", "Email" : "four@groupone.com", "Password" : sha256_crypt.hash("111111111111111"), "Auth_Type" : "None", "Account_Type" : "Client", "Keys" : "Group01_4", "Key_Distributed" : 0, "Grp" : 1, "Expiry": ""})

    if db.retrieve("groups") == None:
        db.insert("groups",{"Name" : "Group01", "Internal" : "10.8.1.0/24", "External" : "192.168.3.0/24", "Used_Octets" : "1,2,4,5"})
        db.insert("groups",{"Name" : "Group02", "Internal" : "10.9.1.0/24", "External" : "192.128.3.0/24", "Used_Octets" : "1,2,4,5"})

    
    #Close database
    db.close()


def loadConfig():
    """
        Reads a config file and sets environment variables
    """
    #base config dictonary 
    config = base_config
    
    #Find config file
    confFile = config_file
    if os.path.exists(config_path_main):
        confFile = config_path_main
    elif os.path.exists(config_path_backup): 
        confFile = config_path_backup

    #Read in config
    node_locations = False
    nodes = []
    
    try:
        with fileinput.input(files=confFile) as f:
            for line in f:
                #Ignore new lines and comments
                if line == "" or line =="\n" or line[0] == "#":
                    continue
                #Read in line as an address for a node
                if node_locations:
                    #Check end
                    if line.strip("\n") == "{":
                        node_locations = False
                    else:
                        nodes.append({"Address" : line.strip("\n")})
                else:
                    #split by '=' and store in tuple
                    key, val = line.split("=")
                    
                    #checks for empty values
                    if key == "":
                        logging.error("Error reading config at line %d: No key\n\t%s",f.lineno(),line)
                    elif val == "":
                        logging.error("Error reading config at line %d: No Value\n\t%s",f.lineno(),line)
                    
                    #Check for node_locations and handle
                    if key == "node_locations":
                        #loop till the end of the node_location section
                        node_locations = True
                         
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
        logging.error("Error reading config: %s",e)

    
    #Add nodes to database if multinode support enabled and master node
    if os.getenv(tag+'multinode',base_config['multinode']) == "True" and os.getenv(tag+'node',base_config['node']) == "master":
        db = Database(filename = filen)
        for node in nodes:    
            db.insert("nodes",node)
            
        db.close()
   
    #Loadin iptables  
    loadIptables()

def setKeyExpiry():
    """
        Adds job to the scheduler and starts the scheduler
    """
    #Add key expiry job to run every hour
    sched.add_job(checkExpiredKeys,'cron',minute=0,id='key_expire_job')
    
    #Start scheduler
    sched.start()

def run_server(development=False):
    """
        Initialises and runs the web server
        
        development : flag to run the Flask development server instead of the full Cherrypy server
    """    
    #load config 
    loadConfig()
    
    #Initalise database
    init_database()

    #Setup key expiry 
    setKeyExpiry()
 
    #Determine if this is a multi node system
    if os.getenv(tag+'multinode',base_config['multinode']) == "True" and os.getenv(tag+'node',base_config['node']) == "slave":
        run_slave()    
    else:
        run_master()    


if __name__ == '__main__':
    run_server(True)

