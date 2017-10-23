#Imports
import random
import string
import re
import os
import logging
import cherrypy 

from functools import wraps
from flask_mail import Message, Mail
from flask import Flask, render_template, redirect, url_for, request, session, abort, send_file, flash, jsonify
from paste.translogger import TransLogger

try:
    from onegroup.defaults import *
    import onegroup.handler as hl
except:
    from defaults import *
    import handler as hl


app = Flask(__name__)
mail = Mail(app) 

#
# User management
#

@app.route('/getkey/<name>', methods=['GET'])
def getUserKey(name):
    """
        Allows the master node to download a user key from this node  
        
        name : the keyfile name of the key to be downloaded 
        
        GET : Returns the user's keys or 404 if not found
    """
    #Check if keys exist
    if os.path.isdir(keys_dir):
        filename = keys_dir + name + '.ovpn' 
        
        return send_file(filename)
    #Else abort 404    
    else:
        abort(404)


@app.route('/createkey/', methods=['POST'])
def createUserKey():
    """
        Creates a user key pair on the server 

        JSON:
            user : the keyfile name for the user's keys
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    args = [
        "add",
        content["user"],
    ]
    hl.callScript('userman',args)
    return jsonify({"result" : True})

@app.route('/deletekey/', methods=['POST'])
def deleteUserKey():
    """
        Deletes auser key pair from the server 

        JSON:
            user : the keyfile name for the user's keys
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    args = [
        "del",
        content["user"],
    ]
    hl.callScript('userman',args)
    return jsonify({"result" : True})

@app.route('/getconfig/<user>', methods=['GET'])
def getConfig(user):
    """
        Gets a user's openvpn client config 

        user : the keyfile name for the user's keys
        
        GET: Returns the user's client config or None if doesn't exist
    """
    return jsonify({"config" : hl.getUserClientConfig(user)})

#
# Group management
#

@app.route('/addgroup/', methods=['POST'])
def addGroup():
    """
        Adds a group to the system

        JSON:
            internal : internal network address for the group 
        
        POST: Returns True if successful else False
    """
    content = request.get_json() 
    hl.addRouteToConfig(content["internal"])
    return jsonify({"result" : True})

@app.route('/updategroup/', methods=['POST'])
def updateGroup():
    """
        Updates the route for a group on the server

        JSON:
            oldInternal : the old internal network address 
            newInternal : the new internal network address 
        
        POST: Returns True if successful else False
    """
    content = request.get_json() 
    hl.updateRouteInConfig(content["oldInternal"],content["newInternal"])
    return jsonify({"result" : True})

@app.route('/deletegroup/', methods=['POST'])
def deleteGroup():
    """
        Removes a group from the system

        JSON:
            internal : internal network address for the group 
        
        POST: Returns True if successful else False
    """
    content = request.get_json() 
    hl.deleteRouteInConfig(content["internal"])
    return jsonify({"result" : True})

@app.route('/addtogroup/', methods=['POST'])
def addToGroup():
    """
        Adds a user to a group. Will remove them from thier existing group if any

        JSON:
            user : the keyfile name for the user's keys
            internal : internal IP address for the user 
            external : the external ip address/network of the group
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    hl.updateUserClientConfig(content["user"],content["internal"],content["external"])
    return jsonify({"result" : True})

@app.route('/removefromgroup/', methods=['POST'])
def removeFromGroup():
    """
        Removes a user from a group

        JSON:
            user : the keyfile name for the user's keys
        
        POST: Returns True if successful else False
    """
    #Remove the user's client config file
    content = request.get_json()
    args = [
        os.getenv(tag+'openvpn_ccd',base_config['openvpn_ccd'])+"/{}".format(content["user"]),
    ]
    hl.callScript('rm',args)
    return jsonify({"result" : True})

#
# Iptables rule management
#

@app.route('/getrules/', methods=['GET'])
def getIPRules():
    """
        Fetches a json representation of the Iptables rules on the server
 
        GET: json object with the all the iptables rules on the system
    """
    return jsonify({"result" : True, "rules" : hl.getIptablesRules()})

@app.route('/getrule/', methods=['POST'])
def getIPRule():
    """
        Fetches a json representation of a specific iptables rule 
        
        JSON:
            key : the field to search for the rule by
            value : the value to search for the rule by
 
        POST: json object with the iptables rules from the system
    """
    content = request.get_json()
    return jsonify({"result" : True, "rule" : hl.getRule(content["key"], content["value"])})

@app.route('/addrule/', methods=['POST'])
def addRule():
    """
        Adds an iptables rule to the system

        JSON:
            rule : Iptable rule in string format
        
        POST: Returns json object with the ID of the added rule
    """
    content = request.get_json()
    hl.addIPRule(content["rule"])
    rule = hl.getRule("Rule",content["rule"])
    return jsonify({"Rule" : rule["ID"]})

@app.route('/updaterule/', methods=['POST'])
def updateRule():
    """
        Updates an iptables rule on the system

        JSON:
            ID : id of the rule to update
            rule : new iptable rule in string format
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    hl.updateIPRule(content["ID"],content["rule"])
    return jsonify({"result" : True})

@app.route('/deleterule/', methods=['POST'])
def deleteRule():
    """
        Deletes a iptables rule from the system

        JSON:
            ID : id of the rule to update
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    hl.removeIPRule(content["ID"])
    return jsonify({"result" : True})

#
# Log File Methods
#

@app.route('/log/<log>', methods=['GET'])
def logJson(log):
    """
        Fetches a json representation of the vpn logs

        log : the log to fetch
 
        GET: If log is a valid log name, return json formatted log. 
             Else abort 404
    """
    filename = log_dir
    if log == "general":
        filename += "openvpn.log"
    elif log == "status":
        filename += "openvpn-status.log"
    else:
        abort(404)

    return jsonify({"result" : True, "logData" : hl.getLog(filename)})

@app.route("/logdownload/", methods = ['GET'])
def logDownload():
    """
        Downloads a VPN Log file within certian dates

        JSON:
            startdate : datetime for the start of the log section to grab
            enddate: datetime for the end of the log section to grab  
        
        GET: Logfile of entries within the specified date
    """ 
    content = request.get_json()
    startDate = content['startdate']
    endDate = content['enddate']
    logDir = hl.logDownload(startDate,endDate)
    return send_file(logDir)


#
# Server configuration
#

def setConfig(debug):
    """
        Loads the configuration from the config file 
        and applies the config to the server

        debug : flag to turn on the flask debugging flag
    """
    #Set debug flag
    if debug:
        app.config['DEBUG'] = True

    #Apply config
    if os.getenv(tag+'secret',base_config['secret']) == "RANDOM":
        secret = os.urandom(36)
        app.config['SECRET_KEY'] = secret 
    else:
        app.config['SECRET_KEY'] = os.getenv(tag+'secret',base_config['secret']) 


    #Flask-mail config
    #app.config['MAIL_SERVER'] = os.getenv(tag+'mail_server',base_config['mail_server'])
    #app.config['MAIL_PORT'] = int(os.getenv(tag+'mail_port',base_config['mail_port'])) 
    #app.config['MAIL_USE_SSL'] = True
    #app.config['MAIL_USERNAME'] = os.getenv(tag+'email',base_config['email'])    
    #app.config['MAIL_PASSWORD'] = os.getenv(tag+'password',base_config['password']) 
    #mail = Mail(app)


def run_server(development=False):
    """
        Initialises and runs the web server
        
        development : flag to run the Flask development server instead of the full Cherrypy server
    """
    #Set the configuration
    setConfig(development)
     
    #Run development server if in development mode
    if development:
        app.run(use_reloader=False)

        #Delete config
        for key in base_config:
            del os.environ[tag+key]

    else:
        #Enable WSGI access logging with paste
        app_logged = TransLogger(app)

        #Mount app on the root directory
        cherrypy.tree.graft(app_logged,'/')

        #Configure web server
        config = {
            'engine.autoreload_on': True,
            'log.screen': True,
            'server.socket_port': int(os.getenv(tag+'server_port',base_config['server_port'])),
            'server.socket_host': os.getenv(tag+'server_host',base_config['server_host'])        
        }

        #Check if ssl is configured correctly and if so apply it
        ssl_cert = os.getenv(tag+'server_ssl_cert',base_config['server_ssl_cert']) 
        ssl_key = os.getenv(tag+'server_ssl_private',base_config['server_ssl_private']) 
        ssl_chain = os.getenv(tag+'server_ssl_cert_chain',base_config['server_ssl_cert_chain']) 
        
        if ssl_cert != "None" and ssl_key != "None":
            config['server.ssl_module'] = 'builtin'
            config['server.socket_port'] = 443
            config['server.ssl_certificate'] = ssl_cert
            config['server.ssl_private_key'] = ssl_key

            if ssl_chain != "None":
                config['server.ssl_certificate_chain'] = ssl_chain

        #Apply config
        cherrypy.config.update(config) 

        #Start WSGI web server
        cherrypy.engine.start()
        cherrypy.engine.block()


if __name__ == '__main__':
    run_server(True)
