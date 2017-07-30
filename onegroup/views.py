#Cherrypy imports
import cherrypy
from paste.translogger import TransLogger
from flask_mail import Message, Mail

from flask import Flask, render_template, redirect, url_for, request, session, abort, send_file, flash
from functools import wraps
try:
    import onegroup.handler as hl
except:
    import handler as hl


app = Flask(__name__)
app.config.from_object(__name__)

# Load default config and override config from an environment variable
app.config.update(dict(
    SECRET_KEY='development_key',
))

app.config.update(
    DEBUG = True,
    MAIL_SERVER='smtp.gmail.com',
	MAIL_PORT=465,
	MAIL_USE_SSL=True,
	MAIL_USERNAME = 'capstoneonegroup@gmail.com',
	MAIL_PASSWORD = 'MaristCollege!'
)
mail = Mail(app)

#Message mail structure
# msg = Message (
#     "can be some text",  <--- subject title
#     sender = "capstoneonegroup@gmail.com",
#     recipients= ['some email here'])
#     msg.body = "some text here" <--- the body of the email here
#     mail.send(msg)
# )

def login_required(f):
    @wraps(f)
    def login_decorator(*args, **kwargs):
        if not session.get('logged_in'):
            abort(401)
            ##return redirect(url_for('login'))
        else:
            return f(*args, **kwargs)
    return login_decorator


def admin_required(f):
    @wraps(f)
    def admin_decorator(*args, **kwargs):
        if session.get('logged_in') and session.get('type') == 'Admin':
            return f(*args, **kwargs)
        else:
            abort(401)
    return admin_decorator


def client_required(f):
    @wraps(f)
    def client_decorator(*args, **kwargs):
        if session.get('logged_in') and session.get('type') == 'Client':
            return f(*args, **kwargs)
        else:
            abort(401)
    return client_decorator


def redirect_to_user(username):
    redirect(url_for('users', username=username))


@app.route('/')
def render():
    return redirect(url_for('login'))

@app.route('/index', methods=['GET', 'POST'])
@admin_required
def home():
    if request.method == 'POST':
        userforms()
        return redirect(url_for('confirm', confirmed = 'Added Client'))
    return render_template('index.html')


@app.route('/password', methods=['GET', 'POST'])
@client_required
def password():
    if request.method == 'POST':
        passwordform()
        return redirect(url_for('confirm', confirmed = 'Changed Password'))
    return render_template('password.html')

@app.route('/users')
@admin_required
def retrieve_user_page():
    ##redirect(url_for('users'))
    flash("Run")
    return render_template('users.html')


@app.route('/logs')
@admin_required
def show_logs():
    flash("Rabbit")
    return render_template('logs.html')


@app.route('/userkey')
def userkey():
    return send_file('static\\' + session.get('name') + '.zip')
    #Possible Zip File Path
    #return send_file('usr\\local\\onegroup\\keys\\' + session.get('name') + '.txt')
	
@app.route('/clients/<username>')
@client_required
def show_user_keys(username):
    return render_template('user_keys.html', username=username)
    ##method to pull keys from database using username


@app.route('/config')
@admin_required
def show_config():
    flash("Run")
    flash("Forget the Sun")
    return render_template('config.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
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
    session.clear()
    print(session)
    return redirect(url_for('login'))


@app.route('/confirm', methods=['GET', 'POST'])
def confirm():
    if request.method == 'POST':
        user_type = session.get('type', None)
        print(user_type)
        if user_type == 'Admin':
            return redirect('/index')
        elif user_type == 'Client':
            return redirect('/clients/' + session.get('Name'))
        else:
            return redirect('/')

    confirmed = request.values['confirmed']
    
    return render_template('confirm.html', confirmed=confirmed)

@app.route('/forgot', methods=['GET','POST'])
def forgotPassword():
    if request.method == 'POST':
        email = request.form['email']
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

            emailMessage("Password Reset", user["Email"], msg)
            return redirect(url_for('confirm', confirmed = 'Password reset email has been sent.'))
        else:
            flash("User doesn't exists")

    return render_template('.html')

@app.route('/reset/<code>', methods=['GET','POST'])
def passwordCode(code):
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
    #Check if code exists and for the correct purpose. Else abort
    if (hl.checkCode(code,"Keys")):
        user = hl.getUserFromCode(code)
    else:
        abort(404)
    
    #Mark code as used
    hl.flagCode(code)
    #return
    return send_file('/usr/local/onegroup/keys/' + user + '.zip')

def emailMessage(subjectTitle, recipientEmail, bodyMessage):
    msg = Message(
        subjectTitle,
        sender = "capstoneonegroup@gmail.com",
        recipients= [recipientEmail])
    msg.body = bodyMessage ##"Your login details are\n Email :" + str(clientemail) + "\nPassword :" + str(clientpassword)
    mail.send(msg)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html'), 404
	

#Function to create user and generate keys into a ZIP folder
def userforms():
    if request.method == 'POST':
        name = request.form['name1']
        password = request.form['pass1']
        email = request.form['email1']
        hl.createUser(name,password,email)
        subjectTitle = "OneGroup account details"
        recipientEmail = email
        bodyMessage = "Your login details are\n Email :" + str(email) + "\nPassword :" + str(password)
        emailMessage(subjectTitle, recipientEmail, bodyMessage)
        ##user = hl.getUser("Email",email)
        ##hl.zipUserKeys(user['Keys'])

def passwordform(name = None):
    if request.method == 'POST':
        if name == None:
            name = session['name']

        password = request.form['pass1']
        confirmPassword = request.form['passconfirm']
        if password == confirmPassword:
            hl.changePassword(name,confirmPassword)

#
#Cherrypy server base
#
def run_server():
    #Initalise database
    hl.init_database()
    
    #Enable WSGI access logging with paste
    app_logged = TransLogger(app)

    #Mount app on the root directory
    cherrypy.tree.graft(app_logged,'/')

    #Configure web server
    cherrypy.config.update({
	'engine.autoreload_on': True,
	'log.screen': True,
	'server.socket_port': 80,
	'server.socket_host': '0.0.0.0'
    })

    #Start WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == '__main__':
    #Initalise database
    hl.init_database()
     
    #For debugging
    app.run()

    #Cherrypy server
    #run_server()
