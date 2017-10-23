#Imports
import random
import string
import re
import os
import logging
import cherrypy
from datetime import datetime, timedelta

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


def admin_required(f):
    """
        Wraper for endpoints to perform an authentication check specifically for admin only pages
        
        f : endpoint function to be wrapped

        returns f if logged in, else aborts with a 401 error
    """
    @wraps(f)
    def admin_decorator(*args, **kwargs):
        if session.get('logged_in') and session.get('type') == 'Admin':
            return f(*args, **kwargs)
        else:
            abort(401)
    return admin_decorator


#make a new form to take packet type, source, destination and port as parameters
#parameters given could be 3 of something or 17.
#def ipTableForm():
   
 #   packetType = Type:
  #  packetSource = Source:
   # packetDestination = Destination:
   # packetPort = Port:


def client_required(f):
    """
        Wraper for endpoints to perform an authentication check specifically for client only pages
        
        f : endpoint function to be wrapped

        returns f if logged in, else aborts with a 401 error
    """
    @wraps(f)
    def client_decorator(*args, **kwargs):
        if session.get('logged_in') and session.get('type') == 'Client':
            return f(*args, **kwargs)
        else:
            abort(401)
    return client_decorator


def redirect_to_user(username):
    """
        Redirects the to a particular client's page
        
        username : username of the client

        returns redirect to specified client's page
    """
    redirect(url_for('users', username=username))


@app.route('/')
def render():
    """Endpoint placeholder to redirect to the login page"""
    return redirect(url_for('login'))

@app.route('/connectnode/', methods=['POST'])
@admin_required
def connectnode():
    """
        Peforms a request for data from a remote node

        method : GET or POST
        url : url to the node
        data : data to pass to the node

        Returns : json object response from the node
    """
    content = request.get_json()
        
    #Check request method
    if content["method"] == "GET":
        res = hl.nodeGet(content["url"])
    elif content["method"] == "GET":
        res = hl.nodePost(content["url"], content["data"])

    #Error check
    if res:
        if ('result' in res and res['result']) or 'result' not in res:
            try:
                res.pop("result")
            except:
                pass
            
            result = {"result" : True, "data" : res} 
        else:
            result = {"result" : False} 
    else:
        result = {"result" : False} 
                        
    #Return response
    return(jsonify(result)) 



@app.route("/log_download/", methods = ['GET', 'POST'])
def log_download():
    year_month_day = r"\d{4}-\d{1,2}-\d{1,2}";
    
    startDate = request.form['eStart']
    endDate = request.form['eEnd']
    matchStartDate= re.search(year_month_day, startDate);
    matchEndDate= re.search(year_month_day, endDate);
    if(matchStartDate and matchEndDate):
        #If remote node, get log from that node
        if 'nodeSelect' in request.form and request.form['nodeSelect'] != "self":
            url = "{}/logdownload/".format(request.form['nodeSelect'])
            now = datetime.now().strftime("%d%m%Y_%H%M%S")
            logDir = os.getenv(tag+'working_dir',working_dir)+"/openvpn_remote_{}.log".format(now)
            
            print(matchStartDate.group(0), matchEndDate.group(0))
            data = {"startdate" : matchStartDate.group(0), "enddate" : matchEndDate.group(0)}

            if not hl.nodeGetFile(url,logDir, data):
                flash("Error getting log file from remote node")
                return redirect(url_for('show_logs'))


        #Else use local node
        else:
            logDir = hl.logDownload(startDate,endDate)

        return send_file(logDir, as_attachment=True)
    else:
        flash("Please Use Valid Date Format: YYYY-MM-DD")
        return render_template('logs.html')
    


@app.route('/index/', methods=['GET', 'POST'])
@admin_required
def home():
    """
        Main admin dashboard
        
        GET: Surves the dashboard html  
        POST: Attempts to create a new client
            Displays confirmation message if creation is successful
            Flashes notification if user exists
    """
    
    nodes = hl.getAllNodes();
    return render_template('index.html', nodes = nodes)


@app.route('/password/', methods=['GET', 'POST'])
@client_required
def password():
    """
        Password reset page
        
        GET: Surves password reset html
        POST: Changes the user's password, displays confirmation message
    """
    if request.method == 'POST':
        passwordform()
        return redirect(url_for('confirm', confirmed = 'Changed Password'))
    return render_template('password.html')


@app.route('/users/', methods=['GET'])
@admin_required
def retrieve_user_page():
    """
        User management page for admins
        
        GET: Surves the user management html with new admin notifications 
    """
    users = hl.getUsers()
    groups = hl.getAllGroups()
    requests = hl.retrieveRequests()
    nodes = hl.getAllNodes()
    return render_template('users.html', dataR = requests, dataU = users, dataG = groups, nodes = nodes) 


@app.route('/handle_req/<reqid>', methods=['POST'])
@admin_required
def handle_req(reqid):
    """
        Endpoint to handle the approval/denial of requests made to an admin

        user : the user who created the request
        request : type of request to be performed
        
        POST: If approve, perform the request. Else delete the request
    """
    req = hl.retrieveRequest(reqid)
         
    if request.method == 'POST':
        if request.form['reqOption'] == 'Approve':
            hl.acceptRequest(req)
        elif request.form['reqOption'] == 'Decline':
            hl.declineRequest(req)
        
        return redirect('/users')


@app.route('/delete_key/<uid>', methods=['POST'])
@admin_required
def delete_key(uid):
    """
        Endpoint to handle the deletion of a user

        uid : ID of the user to delete
        
        POST: Redirect to the user management page
    """
    if request.method == 'POST':
        hl.deleteUser(uid)
        return redirect('/users')

@app.route('/delete_group/<gid>', methods=['POST'])
@admin_required
def delete_group(gid):
    """
        Endpoint to handle the deletion of a group

        gid : ID of the group to delete
        
        POST: Redirect to the user management page
    """
    if request.method == 'POST':
        hl.deleteGroup(gid)
        return redirect('/users')

@app.route('/logs/', methods=['GET', 'POST'])
@admin_required
def show_logs():
    """
        VPN log display page
        
        GET: Surves the log display html 
    
    """
    nodes=hl.getAllNodes();

    return render_template('logs.html',nodes = nodes)


@app.route('/userkey/<hash>', methods=['GET'])
@client_required
def userkey(hash):
    """
        Surves the user's keys as a downloadable zip file 

        hash : unique name for the downloaded zip file
        
        GET: If the keys have already been download: flash error message and logout
             Else: Offer keys to be downloaded
    """
    user = hl.getUser("Name",session['name'])
    flagCheck = hl.checkDistributeFlag(user["Name"])
    if flagCheck == False:
        return getKeys()
    elif flagCheck == True:
        flash("You have been logged out. Please contact your system administrator")
        return redirect(url_for('logout'))


@app.route('/create_request/<request>/<name>')
@client_required
def create_request(request, name):
    """
        Endpoint to create a new admin notification
 
        GET: Creates a notification and emails the admins detailing the request
    """
    requestId = hl.createRequest(name, request)
    adminEmails = hl.getAdminEmails()
    #Send email to all admin accounts
    msg = """
        Request from {}:
        
        ID: {}

        Request: Key Reset
        
        This message is automatically generated, please do not reply as this account is not monitored.
        
        """.format(name, requestId)
    emailMessage("New Request", adminEmails, msg)
    return redirect(url_for('confirm', confirmed='New Key Request Sent!'))


@app.route('/clients/<username>')
@client_required
def show_user_keys(username):
    """
        Client's personal page
 
        GET: Displays the client page html. Displays download button and generates hash if keys haven't been downloaded for this user
    """
    downloaded = hl.checkDistributeFlag(username)
    #Prevent Replay Attacks by downloading keys
    hash = None
    if not downloaded:
        #generate hash
        hash = randompassword()
    return render_template('user_keys.html', username=username, distributed = downloaded, hash = hash)
    ##method to pull keys from database using username


@app.route('/iptables/<nid>/<ruleid>', methods=['GET','POST'])
@admin_required
def iptable_form(nid, ruleid):
    """
        Form to edit an iptables rule

        nid : the id of the node or -1
        ruleid : the id of the rule to edit

        GET: Display the iptables editor form html
        POST: Handles form data for a new iptables rule
    """ 
    if nid != -1 and (hl.getNode("ID",nid) and hl.getNode("ID",nid)["Address"] != "self"):
        url = hl.getNode("ID",nid)["Address"] 
        res = hl.nodePost(url+"/getrule/",{"key" : "ID", "value" : ruleid}) 
        if "result" in res and res["result"]:
            rule = res["rule"]
    else:
        rule = hl.getRule("ID", ruleid)

    nodes = hl.getAllNodes()
    
    if request.method == 'POST':
        if ruleid == "-2":
            #set policy
            session["Policy"] = request.form["ruleType1"]
            return render_template('iptables_create.html', postback = 1, policy = session["Policy"], nodes = nodes)
        elif ruleid != "-2":
            if ruleid == "-1":           
                ip_string = hl.ipDictToString(getIPForm(session["Policy"]))
                
                #If on a remove node, send rule to node
                if ("node1" in request.form and int(request.form["node1"]) != -1) and hl.getNode("ID",int(request.form["node1"]))["Address"] != "self":
                    url = hl.getNode("ID",int(request.form["node1"]))["Address"] 
                    hl.nodePost(url+"/addrule/",{"rule" : ip_string}) 

                else:    
                    hl.addIPRule(ip_string)
            else :
                ip_string = hl.ipDictToString(getIPForm(rule["Policy"]))
                
                #If on a remove node, send rule to node
                if nid != -1 and (hl.getNode("ID",nid) and hl.getNode("ID",nid)["Address"] != "self"):
                    url = hl.getNode("ID",nid)["Address"] 
                    hl.nodePost(url+"/updaterule/",{"ID" : ruleid, "rule" : ip_string}) 

                else:
                    hl.updateIPRule(ruleid, ip_string)

            return redirect(url_for('show_config'))

        else:
            abort(404)

    if ruleid == "-1":
        return render_template('iptables_create.html', postback = -1, nodes = nodes)

    return render_template('iptables_edit.html', nid = nid, rid = ruleid, rule = rule['Rule'], policy = rule['Policy'], nodes = nodes)


def getIPForm(policy):
    """
        Gets all the form data from an iptables form

        policy : Flag to determine if this is a policy rule or not

        Returns dict of the inputed iptables rule
    """ 
    if int(policy) == 1:
        ip_dict = {
            "Chain" : request.form["Chain"],
            "Action" : request.form["Action"]
        }
    else:
        ip_dict = {
            "Source" : request.form["source"],
            "Source_Port" : request.form["sport"], 
            "Destination" : request.form["destination"],       
            "Destination_Port" : request.form["dport"],
            "Table" : request.form["Table"],
            "Chain" : request.form["Chain"],
            "Input" : request.form["input"],
            "Output" : request.form["output"],
            "Protocol" : request.form["Protocol"],
            "State" : request.form["State"],
            "Action" : request.form["Action"]
        }
    
    return ip_dict


@app.route('/iptabledelete/<nid>/<rid>')
@admin_required
def iptables_delete(nid, rid):
    """
        Deletes a given iptable rule from the database

        rid : the id of the rule to edit

        GET : deletes the given iptable rule
    """
    if nid != -1 and (hl.getNode("ID",nid) and hl.getNode("ID",nid)["Address"] != "self"):
        url = hl.getNode("ID", nid)["Address"] 
        hl.nodePost(url+"/deleterule/",{"ID" : rid}) 
    else:
        hl.removeIPRule(rid)
    
    return redirect(url_for('confirm', confirmed = "IP Table Rule Deleted!"))
    

@app.route('/config/', methods=['GET', 'POST'])
@admin_required
def show_config():
    """
        VPN Server configuration page 
 
        GET: Displays the configuration page html
    """ 

    #Is single or multi node?
    nodes = hl.getAllNodes()
    if nodes:
        if request.method == "POST":
            nodeID = request.form['node1']

        else:
            nodeID = 1

        nodeReq = hl.getNode("ID", nodeID)
        
        if nodeReq["Address"] == "self":
            node = hl.getIptablesRules()
        else:
            res = hl.nodeGet(nodeReq["Address"]+"/getrules/")
            if 'result' in res and res['result']:
                node = res["rules"]         
            else:
                node = None

        if node:
            return render_template('config.html', firewall = node, nodes = nodes, nodeID = hl.getNode("ID", nodeID))
        else:
            flash("Error: cannot retrieve iptable rules from node")
    else:
        return render_template('config.html', firewall = hl.getIptablesRules(), nodes = -1, nodeID = -1)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    """
        User login page 
 
        GET: Displays the login page html
        POST: If credentials are correct: redirect to the appropriate user page
              Else display error
    """
    #Check if the user is already logged in
    if session.get('logged_in'):
        if session['type'] == 'Admin':
            return redirect('/index/')
        else:
            return redirect("/clients/" + session['name'])

    error = None
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['psw']
        if not hl.confirmLogin(email, password):
            error = "Invalid Username or Password"
            flash(error)
        else:
            session['logged_in'] = True
            if hl.confirmUser(email) and hl.confirmClient(email):
                user = hl.getUser("Email",email)
                #If the user used their username instead of thier email
                if not user:
                    user = hl.getUser("Name",email)

                session['type'] = 'Client'
                session['name'] = user['Name']
                return redirect("/clients/" + user['Name'])
            else:
                session['type'] = 'Admin'
                return redirect('/index')
    return render_template('login.html', error=error)


@app.route('/logout/')
@login_required
def logout():
    """
        Endpoint to logout the user
 
        GET: Clears the user's cookies and returns to the login page
    """
    session.clear()
    return redirect(url_for('login'))


@app.route('/confirm/', methods=['GET', 'POST'])
def confirm():
    """
        Confirmation page to display that an action was successful
 
        GET: Displays the confirmation message
        POST: Redirects the user to the appropriate user page
    """
    if request.method == 'POST':
        user_type = session.get('type', None)
        if user_type == 'Admin':
            return redirect('/index')
        elif user_type == 'Client':
            return redirect('/clients/' + session.get('name'))
        else:
            return redirect('/')

    confirmed = request.values['confirmed']
    
    return render_template('confirm.html', confirmed=confirmed)


@app.route('/forgot/', methods=['GET','POST'])
def forgotPassword():
    """
        Password reset request page for users who have forgotten their password
 
        GET: Displays the password reset request html
        POST: If user email is valid, sends a reset link to that address
              Else displays error message
    """
    if request.method == 'POST':
        if emailform():
            email = request.form['email1']

            #Confirm the user exist
            if hl.confirmUser(email):
                user = hl.getUser("Email",email)
                refLink = "http://"+request.headers['Host']+hl.genUrl(user["Name"],"Password")
                #Send email
                msg = """
                    Dear {},

                    You are receiving this email because you have requested your password be reset. 
                    Use the following link to reset your password:

                    {}

                    If you did not request that your password be changed, please reply to this email immediately.

                    Regards,
                    Onegroup Admin Team
                """.format(user["Name"],refLink)

                emailMessage("Password Reset", [user["Email"]], msg)
                return redirect(url_for('confirm', confirmed = 'Password reset email has been sent.'))
            else:
                flash("User doesn't exists")
        else:
            flash("Emails don't match")
        
    return render_template('emailsend.html')


@app.route('/reset/<code>', methods=['GET','POST'])
def passwordCode(code):
    """
        Password reset page for link sent in an email
 
        GET: If the code is valid, display password reset html
             Else abort with a 404
        POST: If the code is valid, confirm passwords are the same and change password
              Else abort with 404 
    """
    #Check if code exists and for the correct purpose. Else abort
    if (hl.checkCode(code,"Password")):
        user = hl.getUserFromCode(code)
    else:
        abort(404)

    if request.method == 'POST':
        #Get new password and handle
        passwordform(user)
        #Mark code as used
        hl.flagCode(code)
        #return
        return redirect(url_for('confirm', confirmed = 'Changed Password'))

    return render_template('password.html')

        
@app.route('/keys/<code>', methods=['GET'])
def keysCode(code):
    """
        Download user's keys from an email link
 
        GET: If the code is valid, download user keys
             Else abort with a 404
    """
    #Check if code exists and for the correct purpose. Else abort
    if (hl.checkCode(code,"Keys")):
        user = hl.getUserFromCode(code)
    else:
        abort(404)
    
    #Mark code as used
    hl.flagCode(code)
    #return
    return getKeys(user["Name"])


@app.route('/log/<log>', methods=['GET'])
@admin_required
def logType(log):
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
    
    return jsonify({"logData" : hl.getLog(filename)})


@app.route('/userform/<form>', methods=['GET', 'POST'])
@admin_required
def filluserform(form):
    """
        Displays the form for editing or creating single users

        form :  "CU" for Create User

                ID: the user ID in database to identify the unique entry
        
        GET : If form is valid value display the correct form
                Else abort 404

        POST : Attempt to add data from form into database, if successful,
                redirect to confirm endpoint or abort 404
    """

##    //ACCOUNT TYPE
##        //IF Client account = Client
##                //Show AUTH TYPE
##                        //IF Passphrase auth = Passphrase
##                                //SHOW NAME, EMAIL, PASS, GROUP, EXPIRY
##                        //IF Email auth = Email
##                                //SHOW NAME, EMAIL, GROUP, EXPIRY
##                        //IF None auth = None
##                                //SHOW NAME, GROUP, EXPIRY
##        //IF ADMIN account = Admin
##                //SHOW NAME, EMAIL, PASS

    groups = hl.getAllGroups()
    nodes = hl.getAllNodes()

    if request.method == 'POST':
        if form == "AC":
            #Store Account Type in session variable 
            if request.form['accountType1'] == "Client":
                session['accountType'] = "Client"
                return render_template("userform_create_user.html", postback = 1, account = "Client", auth = "NULL", groups = groups, nodes = nodes)
            elif request.form['accountType1'] == "Admin":
                session['accountType'] = "Admin"
                session['authType'] = "Passphrase"
                return render_template("userform_create_user.html", postback = 1, account = "Admin", auth = "Passphrase", groups = groups, nodes = nodes)
            else:
                abort(404)
             
        elif form == "AU":
            #Store Auth Type in session variable
            if request.form['authType1'] == "Passphrase":
                session['authType'] = "Passphrase"
                return render_template("userform_create_user.html", postback = 1, account = "Client", auth = "Passphrase", groups = groups, nodes = nodes)
            elif request.form['authType1'] == "Email":
                session['authType'] = "Email"
                return render_template("userform_create_user.html", postback = 1, account = "Client", auth = "Email", groups = groups, nodes = nodes)
            elif request.form['authType1'] == "None":
                session['authType'] = "None"
                return render_template("userform_create_user.html", postback = 1, account = "Client", auth = "None", groups = groups, nodes = nodes)
            else:
                abort(404)

        elif form == "ET":
            user = session['user']
            return render_template("userform_edit_user.html", postback = 1, username=user["Name"], email=user["Email"], authtype=user["Auth_Type"], accounttype=user["Account_Type"], expire=user["Expiry"], grp = user["Grp"], groups = groups, node = user["Node"])
                
        elif form == "DE":
            #MAKE SURE ALL VALUE THAT ARE NOT PART OF REQUEST.FORM DO NOT THROW 400 BAD REQUEST ERROR
            name = request.form['name1']

            auth = session['authType']
            session.pop('authType', None)
            
            account = session['accountType']
            session.pop('accountType', None)
            
            
            if auth == "Passphrase":
                pwd = randompassword() #Default Generation or Not
                email = request.form['email1']
            elif auth == "Email":
                pwd = "" 
                email = request.form['email1']
            else:
                pwd = ""
                email = ""

            if account == "Client":
                group = int(request.form['groupId1'])
                expiry = request.form['expiry1']
                if 'node1' in request.form:
                    node = int(request.form['node1'])
                else:
                    node = -1
            else:
                group = -1
                expiry = ""
                node = -1 
                        
            if createNewUser(name, account, auth, email, pwd, group, expiry, node):
                return redirect(url_for('confirm', confirmed = 'New User Created!'))
            else:
                flash("User already exists")
                    
        elif form == "EU":
            user = {"Name" : request.form['name2'], "Email" : "", "Auth_Type" : session["user"]["Auth_Type"], "Account_Type" : session["user"]["Account_Type"], "Expiry" : request.form['expiry1'], "Grp" : int(request.form['groupId2'])}
            
            if 'email2' in request.form:
                user["Email"] = request.form['email2']             
            
            if 'node2' in request.form:
                user["Node"] = int(request.form['node2'])          

            if hl.updateUser(session["user"]["ID"], user):
                session.pop("user", None)
                return redirect(url_for('confirm', confirmed = 'User Information Successfully Updated'))
            else:
                flash("Cannot Update User Information")
        else: #Must be fake input
            abort(404)

    if form == "CU":
        return render_template("userform_create_user.html", postback = -1, account = "NULL", auth = "NULL", groups = groups, nodes = nodes)
    elif hl.getUser("ID", form) != None:
            user = hl.getUser("ID", form)
            session['user'] = user
            return render_template("userform_edit_user.html", postback = -1, authtype=user["Auth_Type"], accounttype=user["Account_Type"])
            #return render_template("userform_edit_user.html", postback = -1, username=user["Name"], email=user["Email"], authtype=user["Auth_Type"], accounttype=user["Account_Type"], grp = user["Grp"], nde = user["Node"], groups = groups, nodes = nodes)
    else: #Must be fake input
        abort(404)            


@app.route('/groupform/<form>', methods=['GET', 'POST'])
@admin_required
def fillgroupform(form):
    """
        Displays the form for editing or creating groups of users

        form :  "CG" for Create Group
        
                ID: the group ID in database to identify the unique entry
        
        GET : If form is valid value display the correct form
                Else abort 404

        POST : Attempt to add data from form into database, if successful,
                redirect to confirm endpoint or abort 404
    """

    nodes = hl.getAllNodes()
    
    if request.method == 'POST':
        if form == "CG":
            if createNewGroup():
                return redirect(url_for('confirm', confirmed = 'New Group Created!'))
            else:
                abort(404)
        elif hl.getGroup(form) != None:
            group = {"Name" : str(request.form['groupname2']), "Internal" : str(request.form['internal2']), "External" : str(request.form['external2'])} 
            if hl.updateGroup(form, group):
                return redirect(url_for('confirm', confirmed = 'Group Information Successfully Updated'))
            else:
                flash("Cannot Update Group Information")
        else: #Must be fake input
            abort(404)
    
    if form == "CG":
        return render_template("userform_create_group.html", nodes = nodes)
    elif hl.getGroup(form) != None:
        group = hl.getGroup(form)
        return render_template("userform_edit_group.html", groupname=group["Name"], internal=group["Internal"], external=group["External"], node = group["Node"])
    else: #Must be fake input
        abort(404)
        

def emailMessage(subjectTitle, recipientEmail, bodyMessage, attachmentName = None, attachmentFilePath = None):
    """
        Sends an email to specified recipients

        subjectTitle : Email's subject
        recipientEmail : The address(s) to send the email to. Expects list
        bodyMessage: Email's body
        attachmentName : Name of the attached file. None if no attachment
        attachmentFilePath : Full path to the attachment. None if no attachment
    """
    msg = Message(
        subjectTitle,
        sender = os.getenv(tag+'email',base_config['email']) 
    )
    for email in recipientEmail:             
        msg.add_recipient(email)

    msg.body = bodyMessage

    if attachmentName is not None and attachmentFilePath is not None:
        with app.open_resource(attachmentFilePath) as fp:
            msg.attach(attachmentName, "text/plain", fp.read())

    mail.send(msg)


@app.errorhandler(404)
@app.errorhandler(401)
def page_not_found(e):
    """
        Error handler for 404 and 401 errors

        Returns : login template and flashes error message
    """
    flash("Error: Try Something Different This Time")
    return redirect(url_for('login'))


#Function to create user and generate keys into a ZIP folder
def createNewUser(name, account, auth, email, pwd, group, expiry, node):
    """
        Handles input of the new user form. 

        If user creation is successful, emails the user their initial password

        returns : True if user created, else False
    """
    
    #Check if the user creation was succesful
    if hl.createUser(name, account, auth, email = email, passwd = pwd, group = group, expiry = expiry, node = node):
        user = hl.getUser("Email", email)

        if(auth == "Email"):
            subjectTitle = "OneGroup account keys"
            recipientEmail =[email]
            bodyMessage = "here are your keys"
            attachmentName = user['Keys'] + '.ovpn'
            filename = "{}/{}".format(keys_dir,attachmentName)
            attachmentFilePath = filename
            emailMessage(subjectTitle, recipientEmail, bodyMessage,attachmentName, attachmentFilePath)

        elif(auth == "Passphrase"):
            subjectTitle = "OneGroup account details"
            recipientEmail = [email]
            bodyMessage = "Your login details are\n Email :" + str(email) + "\nPassword :" + str(pwd)
            emailMessage(subjectTitle, recipientEmail, bodyMessage)
        return True
    else:
        return False        


def createNewGroup():
    """
        Handles input of the new group form. 

        If user creation is successful returns back to calling function

        returns : True if group created, False otherwise
    """
    if request.method == 'POST':
        groupname = request.form['groupname1']
        internal = request.form['internal1']
        external = request.form['external1']
        userNo = request.form['usersNo1']
        if 'node1' in request.form:
            node = int(request.form['node1'])
        else:
            node = -1

        if int(userNo) == 0:
            if hl.createGroup(groupname, internal, external, node):
                return True
        elif int(userNo) > 0:
            if hl.createGroup(groupname, internal, external, node, genUsers=True, numUsers=int(userNo)):
                return True

        return False

    
def passScript():
    """
        Pass variables obtioned in webform to bashscript
        
        Returns : True if POST request, Else False
    """
    if request.method == 'POST':
        ipRules = "iptables"
        table = request.form['TABLE']
        if not table=="":
            ipRules = ipRules + " -t " + table
            
        chain = request.form['CHAIN']
        if not chain=="":
            ipRules = ipRules + " -A " + chain
            
        packType = request.form['PROT']
        if not packType=="":
            ipRules = ipRules + " -p " + packType
        elif packType=="" and not port=="":
            ipRules = ipRules + " -p tcp"
            
        source = request.form['source']
        if not source=="":
             ipRules = ipRules + " -s " + source
             
        destination = request.form['destination']
        if not destination=="":
            ipRules = ipRules + " -d " + desination
            
        port = request.form['port']
        if not port=="":
            ipRules = ipRules + " -dport " + port
            
        action = request.form['ACTION']
        if not action=="":
            ipRules = ipRules + " -j " + action
            
        callScript('ip_rules.sh',[ipRules])
        return True
    else:
        return False


def passwordform(name = None):
    """
        Handles input for the change password form
        
        name :  Username of the user who's password should be changed. Uses cookie value if None

        if both passwords match, the user's password is changed
    """
    if request.method == 'POST':
        if name == None:
            name = session['name']

        password = request.form['pass1']
        confirmPassword = request.form['passconfirm']
        if password == confirmPassword:
            hl.changePassword(name,confirmPassword)


def randompassword():
    """
        Generates a random password
        
        Returns: string of random length
    """
    characters = string.ascii_uppercase + string.ascii_lowercase + string.digits
    size = random.randint(8, 12)
    return ''.join(random.choice(characters) for x in range(size))


def emailform():
    """
        Handles input for email confirmation forms
        
        Returns: True if emails match
    """
    if request.method == 'POST':
        email = request.form['email1']
        confirmemail = request.form['email2']
        if email == confirmemail:
            #EMAIL CODE HERE
            return True


def getKeys(name = None):
    """
        Returns a zip file of the user's key/cert pair
        
        name : Name of user's keys to fetch. Uses cookie value if None

        Returns : zip file of user's keys if found. Else returns example zip file
    """
    if name == None:
        name = session.get('name')

    keys = hl.getUser("Name",name)["Keys"]
    hl.keyDistributeFlag(name)
    #If on a production server, use actual path
    if os.path.isdir(keys_dir):
        filename = keys_dir + keys + '.ovpn' 

        #if not os.path.exists(filename):
        #    hl.zipUserKeys(keys) 

        return send_file(filename, as_attachment=True)
    #Else use relative dev path
    else:
        return send_file('static\\Test_client1.zip', as_attachment=True)


@app.route('/admin_key/<name>', methods=['GET','POST'])
@admin_required
def adminGetUserKey(name):
    """
        Returns a config file of a specified user's key/cert pair for the Admin to download

        
        Returns : config file of user's keys if found. Else returns example zip file
    """
    keys = hl.getUser("Name",name)["Keys"]
    #If on a production server, use actual path
    if os.path.isdir(keys_dir):
        filename = keys_dir + keys + '.ovpn' 
        #if not os.path.exists(filename):
        #    hl.zipUserKeys(keys) 
        
        return send_file(filename, as_attachment=True)
    #Else use relative dev path
    else:
        return send_file('static\\Test_client1.zip', as_attachment=True)


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
    app.config['MAIL_SERVER'] = os.getenv(tag+'mail_server',base_config['mail_server'])
    app.config['MAIL_PORT'] = int(os.getenv(tag+'mail_port',base_config['mail_port'])) 
    app.config['MAIL_USE_SSL'] = True
    app.config['MAIL_USERNAME'] = os.getenv(tag+'email',base_config['email'])    
    app.config['MAIL_PASSWORD'] = os.getenv(tag+'password',base_config['password']) 
    mail = Mail(app)


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
