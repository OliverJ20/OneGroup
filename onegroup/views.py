#Cherrypy imports
import cherrypy
from paste.translogger import TransLogger

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


@app.route('/logout')
@login_required
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))


@app.route('/confirm', methods=['GET', 'POST'])
@login_required
def confirm():
    if request.method == 'POST':
        user_type = session.get('type')
        if user_type == 'Admin':
            return redirect('/index')
        elif user_type == 'Client':
            return redirect('/clients/' + session.get('Name'))
        else:
            abort(404)

    confirmed = request.values['confirmed']
    
    return render_template('confirm.html', confirmed=confirmed)

	
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
        ##Creates Zip File
        ##user = hl.getUser("Email",email)
        ##hl.zipUserKeys(user['Keys'])

#
#Cherrypy server base
#
def run_server():
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
