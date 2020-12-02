from datetime import datetime
from os import abort
import os
from bson.json_util import dumps
import json
from flask import redirect, render_template, Flask, url_for, request, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from db import get_user, save_user, add_room_members, get_rooms_for_user, get_room, is_room_admin, \
    fetch_database, update_user

app = Flask(__name__)app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://test:test@admin.31upf.mongodb.net/<dbname>?retryWrites=true&w=majority"
app.config['UPLOAD_DIR'] = 'static/Uploads'
mongo = PyMongo(app)
app.secret_key = "i know"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@app.route('/')
@login_required
def home():
    return render_template("home.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)
        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        else:
            message = "Login failed"
    return render_template('login.html', message=message)

@app.route('/registration')
def signin():
    return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        contact = request.form.get('contact')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        file = request.files["profile_pic"]
        file.save(os.path.join(app.config['UPLOAD_DIR'], file.filename))
        try:
            save_user(username, email, password,contact,gender,dob,file.filename)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "User already exists!"
    return render_template('signup.html', message=message)



@app.route('/update/<username>', methods=["POST","GET"])
def update(username):
    dataa = fetch_database.get_collection('users')
    user = get_user(username)
    if request.method == 'POST':
        dataa.update_one({"_id":username},
                         {
                             "$set": {"id":request.form.get('username'),
                                      "email": request.form.get('email'),
                                      "contact": request.form.get('contact'),
                                      "gender": request.form.get('gender'),
                                      "dob": request.form.get('dob'),
                                      }
                         })
        return redirect(url_for('home'))
    return render_template('Edit_Profile.html', user =user)

#Profile View
@app.route('/user/<username>')
@login_required
def user(username):
    user = mongo.db.users.find({'_id': username})
    return render_template('view.html',user=user)

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(username):
    return get_user(username)

if __name__ == '__main__":
       app.run(debug=True)
