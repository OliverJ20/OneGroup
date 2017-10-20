import logging
import os
import fileinput

from apscheduler.schedulers.background import BackgroundScheduler
from passlib.hash import sha256_crypt

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

    #If no users in the database, add the default admin user
    if db.retrieve("users") == None:
        db.insert("users", {"Name" : "admin", "Email" : "admin@onegroup.com", "Password" : sha256_crypt.hash("admin"), "Auth_Type" : "Passphrase", "Account_Type" : "Admin", "Keys" : "admin", "Key_Distributed" : 1, "Grp" : -1, "Node" : -1, "Expiry": ""})
    
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
                    if line.strip("\n") == "}":
                        node_locations = False
                    else:
                        name, address = line.strip("\n").split()
                        nodes.append({"Name" : name, "Address" : address})
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
                        config[key] = val.strip()
                    
                    
        #Assign Config to environment variables
        for key in config:
            os.environ[tag+key] = config[key]

    except Exception as e:
        logging.error("Error reading config: %s",e)

    #Remove all existing nodes 
    db = Database(filename = filen)
    db.delete("nodes")

    #Add nodes to database if multinode support enabled and master node
    if os.getenv(tag+'multinode',base_config['multinode']) == "True" and os.getenv(tag+'node',base_config['node']) == "master":
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
    sched.add_job(checkExpiredKeys,'cron',second=0, id='key_expire_job')
    
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

