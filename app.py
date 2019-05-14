import os
import sys
import requests
import time

from flask import Flask, session, render_template, request, redirect, url_for, jsonify, make_response
from flask_session import Session
from flask_socketio import SocketIO, emit
from flask_hashing import Hashing as Hashing
from flask_login import LoginManager, current_user, login_user, logout_user, login_required, UserMixin
from database import db_session


# Setting APP
app = Flask(__name__)

# Configure app to use in filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["HASHING_METHOD"] = "sha256"
app.config["SECRET_KEY"] = "lkkajdghdadkglajkgah" # a secret key for login

# Init some fungtion needed in app
Session(app)
socketio = SocketIO(app, manage_session=False)
hash = Hashing(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'index' # the login view of your application
login_manager.login_message = 'Silahkan login utuk dapat mengakses halaman.'
login_manager.login_message_category = "warning"

# Prepare Global Variable
data_response = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}

class User(UserMixin):
  def __init__(self,id):
    self.id = id

# Set Main Route
@app.route("/")
@app.route("/index")
def index():  
    return render_template("login.html")

# Route to catch response
@app.route("/answer")
@login_required
def answer():
    session['time'] = {'m':0, 's':10}
    # Display Main Page
    return render_template("answer.html", data_response=session['data_response'], username=session['user_name'], number=session['number'], session_code=session['session_code'])

# Route for login API
@app.route('/login', methods=["POST"])
def login():
    # Cek if user request via POST
    if request.method == 'POST':
        # clear user data in session
        session.clear()

        # Cek if user request via POST
        user = request.form['username']
        code = request.form['session_code']

        # Save login data into sessions
        login_user(User(1))
        session['logged_in'] = True
        session['user_id'] = 1
        session['user_name'] = user
        session['session_code'] = code
        session['number'] = 1
        session['data_response'] = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}

        # Welcome user and redirected to book page
        sys.stdout.flush()
        return redirect(url_for('answer'))

# ROute for logout API
@app.route('/logout', methods=["POST", "GET"])
@login_required
def logout():
    # remove the username from the session if it's there
    logout_user()
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.clear()
    return redirect(url_for('index'))

@app.route('/reset', methods=["POST", "GET"])
@login_required
def reset():
    # remove the username from the session if it's there
    logout_user()
    session.pop('logged_in', None)
    session.pop('user_id', None)
    session.pop('user_name', None)
    session.clear()
    data_response = {"A": 0, "B": 0, "C": 0, "D": 0, "E": 0}
    return redirect(url_for('index'))
#=============================================
# SocketIO Route
#=============================================
# SocketIO to catch response
@socketio.on("submit response")
@login_required
def response(data):
    session['logged_in'] = True
    session['user_id'] = 1

    # Catch selection data that emitted from client
    selection = data["selection"]

    # Increase counter of selection
    session['data_response'][selection] += 1
    data_response[selection] += 1

    # Emits data_response to display to client
    emit("response totals", data_response, broadcast=True)

# Route to next
@socketio.on("next response")
@login_required
def next():
    # Increase counter of number
    session['number'] += 1
    print(session['number'])
    # Emits data_response to display to client
    emit("response number", session['number'])

# Route to next
@socketio.on("back response")
@login_required
def back():
    # Increase counter of number
    if session['number'] > 1:
        session['number'] -= 1
    print(session['number'])
    # Emits data_response to display to client
    emit("response number", session['number'])

@socketio.on("timer")
def countdown():
    while True:
        time.sleep(1)
        if(session['time']['m'] > 0 and session['time']['s'] == 0):
            session['time']['s'] = 60
            session['time']['m'] -= 1
        session['time']['s'] -= 1
        if(session['time']['s'] > 9):
            emit("time", {'time_out': False,
                          'time': f"0{session['time']['m']}:{session['time']['s']}"})
        else:
            emit("time", {'time_out': False,
                          'time': f"0{session['time']['m']}:0{session['time']['s']}"})
        if(session['time']['m'] == 0 and session['time']['s'] == 0):
            break
    emit("time", {'time_out': True,
                          'time': f"00:00"})

#=============================================
# LOGIN SETTUP 
#=============================================
# Route to manage user
@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Route to rejected user handler
@login_manager.unauthorized_handler
def unauthorized():
    # Redirect to home
    response = make_response(redirect(url_for('index'), code=302))
    response.headers['url'] = 'parachutes are cool'
    return response

# Route to after logout
@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
	# Runing SocketIO
	socketio.run(app)
