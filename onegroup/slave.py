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

def login_required(f):
    """
        Wraper for endpoints to perform an authentication check
        
        f : endpoint function to be wrapped

        returns f if logged in, else aborts with a 401 error
    """
    @wraps(f)
    def login_decorator(*args, **kwargs):
        if not session.get('logged_in'):
            abort(401)
        else:
            return f(*args, **kwargs)
    return login_decorator
    

#
# User Key management
#

@app.route('/getkey/<name>', methods=['GET'])
@login_required
def getUserKey(name):
    """
        Allows the master node to download a user key from this node  
        
        name : the keyfile name of the key to be downloaded 
        
        GET : Returns the user's keys or 404 if not found
    """
    #Check if keys exist
    if os.path.isdir(keys_dir):
        filename = keys_dir + keys + '.ovpn' 
        
        return send_file(filename)
    #Else abort 404    
    else:
        abort(404)


@app.route('/createkey/', methods=['POST'])
@login_required
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

@app.route('/deleteKey/', methods=['POST'])
@login_required
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

#
# Group management
#

@app.route('/addgroup/', methods=['POST'])
@login_required
def addToGroup():
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
@login_required
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

@app.route('/removegroup/', methods=['POST'])
@login_required
def removeGroup():
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
@login_required
def addToGroup():
    """
        Adds a user to a group. Will remove them from thier existing group if any

        JSON:
            user : the keyfile name for the user's keys
            internal : internal IP address for the user 
            external : the external ip address/network of the group
        
        POST: Returns True if successful else False
    """
    updateUserClientConfig(user,internal,external)
    return jsonify({"result" : True})

@app.route('/removefromgroup/', methods=['POST'])
@login_required
def removeFromGroup():
    """
        Removes a user from a group

        JSON:
            user : the keyfile name for the user's keys
        
        POST: Returns True if successful else False
    """
    #Remove the user's client config file
    args = [
        os.getenv(tag+'openvpn_ccd',base_config['openvpn_ccd'])+"/{}".format(content["user"]),
    ]
    callScript('rm',args)
    return jsonify({"result" : True})

#
# Iptables rule management
#

@app.route('/getrules/', methods=['GET'])
@login_required
def getIPRules():
    """
        Fetches a json representation of the Iptables rules on the server
 
        GET: json object with the all the iptables rules on the system
    """
    return jsonify({"result" : True, "rules" : hl.getIptablesRules()})

@app.route('/addrule/', methods=['POST'])
@login_required
def addRule():
    """
        Adds an iptables rule to the system

        JSON:
            rule : Iptable rule in string format
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    hl.addIPRule(content["rule"])
    return jsonify({"result" : True})

@app.route('/modifyrule/', methods=['POST'])
@login_required
def modifyRule():
    """
        Updates an iptables rule on the system

        JSON:
            id : id of the rule to update
            rule : new iptable rule in string format
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    hl.updateIPRules(content["ID"],content["rule"])
    return jsonify({"result" : True})

@app.route('/deleterule/', methods=['POST'])
@login_required
def deleteRule():
    """
        Deletes a iptables rule from the system

        JSON:
            id : id of the rule to update
        
        POST: Returns True if successful else False
    """
    content = request.get_json()
    hl.removeIPRule(content["ID"])
    return jsonify({"result" : True})

#
# Log File Methods
#

@app.route('/log/<log>', methods=['GET'])
@login_required
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
@login_required
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
