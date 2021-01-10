from datetime import datetime
from os import abort

from bson import ObjectId
from bson.json_util import dumps
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import os
from PIL import Image
from resizeimage import resizeimage
import sqlite3
from flask_table import Table, Col
from bson.json_util import dumps
import json
from flask import redirect, render_template, Flask, url_for, request, session
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_socketio import SocketIO, join_room, leave_room
from flask_pymongo import PyMongo
from pymongo.errors import DuplicateKeyError
from db import get_user, save_user, save_room, add_room_members, get_rooms_for_user, get_room, is_room_admin, \
    get_room_members, is_room_member, update_room, remove_room_members, save_message, get_messages, save_contact, \
    fetch_database, send_appointment, get_appointment

bot = ChatBot('Quick Ask') #create the bot

trainer = ListTrainer(bot)

#bot.train(conv) # teacher train the bot

for knowledeg in os.listdir('base'):
	BotMemory = open('base/'+ knowledeg, 'r').readlines()
	trainer.train(BotMemory)

app = Flask(__name__)
app.config['MONGO_URI'] = "mongodb+srv://test:test@admin.31upf.mongodb.net/<dbname>?retryWrites=true&w=majority"
app.config['UPLOAD_DIR'] = 'static/Uploads'
mongo = PyMongo(app)
app.secret_key = "i know"
socketio = SocketIO(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@app.route('/inbox')
@login_required
def inbox():
    rooms = []
    if current_user.is_authenticated:
        rooms = get_rooms_for_user(current_user.username)
    return render_template("index.html", rooms=rooms)

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template("UserPage.html")
    return render_template("IndexPage.html")
@app.route('/Doctors')
def Doctors():
    return render_template("Doctors.html")
@app.route('/Service')
def Service():
    return render_template("Service.html")

@app.route('/UserPage')
@login_required
def UserPage():
    return render_template("UserPage.html")
@app.route('/login', methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('UserPage'))
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)
        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('UserPage'))
        else:
            message = "Login failed"
    return render_template('login.html', message=message)
@app.route('/registration')
def signin():
    return render_template('signup.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('UserPage'))

    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        contact = request.form.get('contact')
        dob = request.form.get('dob')
        gender = request.form.get("gender")
        file = request.files["profile_pic"]
        file.save(os.path.join(app.config['UPLOAD_DIR'], file.filename))
        try:
            save_user(username, email, password,contact,dob,gender,file.filename)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message = "User already exists!"
    return render_template('signup.html', message=message)

@app.route('/update/<username>', methods=["POST","GET"])
@login_required
def update(username):
    dataa = fetch_database.get_collection('users')
    user = dataa.find_one({'_id':username})
    if request.method == 'POST':
        dataa.update_one({"_id":username},
                         {
                             "$set": {
                                      'email':request.form.get('email'),
                                      "contact": request.form.get('contact'),
                                      "gender": request.form.get('gender'),
                                      "dob": request.form.get('dob'),
                                      }
                         })
        return render_template('view.html',user=user)
    return render_template('Edit_Profile.html', user =user)

@app.route('/delete/<username>', methods=["POST","GET"])
@login_required
def delete(username):
    message = ''
    dataa = fetch_database.get_collection('users')
    # user = dataa.find_one({'_id':username})
    dataa.delete_many({'_id': username})
    message = 'You are no longer a user Please Signup'
    return render_template('login.html', message = message)

#Profile View
@app.route('/user/<username>')
@login_required
def user(username):
    user = mongo.db.users.find({'_id': username})
    return render_template('view.html',user=user)

@app.route('/create-inbox/', methods=['GET', 'POST'])
@login_required
def create_room():
    message = ''
    if request.method == 'POST':
        room_name = request.form.get('room_name')
        usernames = [username.strip() for username in request.form.get('members').split(',')]

        if len(room_name) and len(usernames):
            room_id = save_room(room_name, current_user.username)
            if current_user.username in usernames:
                usernames.remove(current_user.username)
            add_room_members(room_id, room_name, usernames, current_user.username)
            # return redirect(url_for('view_room', room_id=room_id))
        else:
            message = "Failed to create room"
    return render_template('create_room.html', message=message)
@app.route('/appointment')
def appointment():
    return render_template("appointment.html")

@app.route('/sendappointment', methods=['GET', 'POST'])
@login_required
def sendappointment():
    message = ''
    if request.method == "POST":
        try:
            PatientName = request.form["username"]
            DoctorName = request.form["doctors"]
            Disease = request.form["disease"]
            Contact = request.form["contact"]
            Schedule = request.form["datetime"]
            with sqlite3.connect("Appointment.db") as con:
                cur = con.cursor()
                cur.execute("INSERT into Appointment(PatientName, DoctorName, Disease, Contact, Schedule) values (?,?,?,?,?)",(PatientName,DoctorName,Disease,Contact,Schedule))
                con.commit()
                message = "Appointment successfully Added"
                return render_template("appointment.html", message=message)
                con.close()
        except:
            con.rollback()
            message = "Something Went Wrong!!"
@app.route('/AppointmentDetails')
@login_required
def AppointmentDetails():
    con = sqlite3.connect("Appointment.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute("select * from Appointment")
    rows = cur.fetchall()
    return render_template("AppointmentDetails.html", rows=rows, )

@app.route('/rooms/<room_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_room(room_id):
    room = get_room(room_id)
    if room and is_room_admin(room_id, current_user.username):
        existing_room_members = [member['_id']['username'] for member in get_room_members(room_id)]
        room_members_str = ",".join(existing_room_members)
        message = ''
        if request.method == 'POST':
            room_name = request.form.get('room_name')
            room['name'] = room_name
            update_room(room_id, room_name)

            new_members = [username.strip() for username in request.form.get('members').split(',')]
            members_to_add = list(set(new_members) - set(existing_room_members))
            members_to_remove = list(set(existing_room_members) - set(new_members))
            if len(members_to_add):
                add_room_members(room_id, room_name, members_to_add, current_user.username)
            if len(members_to_remove):
                remove_room_members(room_id, members_to_remove)
            message = 'Room edited successfully'
            room_members_str = ",".join(new_members)
        return render_template('edit_room.html', room=room, room_members_str=room_members_str, message=message)
    else:
        return "Room not found", 404

@app.route('/rooms/<room_id>/')
@login_required
def view_room(room_id):
    room = get_room(room_id)
    if room and is_room_member(room_id, current_user.username):
        room_members = get_room_members(room_id)
        messages = get_messages(room_id)
        return render_template('view_room.html', username=current_user.username, room=room, room_members=room_members,
                               messages=messages)
    else:
        return "Room not found", 404

@app.route('/chat')
@login_required
def chat():
    username = request.args.get('username')
    room = request.args.get('room')
    if username and room:
        return render_template('chat.html', username=username, room=room)
    else:
        return redirect(url_for('home'))

@app.route('/rooms/<room_id>/messages/')
@login_required
def get_older_messages(room_id):
    room = get_room(room_id)
    if room and is_room_member(room_id, current_user.username):
        page = int(request.args.get('page', 0))
        messages = get_messages(room_id, page)
        return dumps(messages)
    else:
        return "Room not found", 404

@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}: {}".format(data['username'],
                                                                    data['room'],
                                                                    data['message']))
    data['created_at'] = datetime.now().strftime("%d %b, %H:%M")
    save_message(data['room'], data['message'], data['username'])
    socketio.emit('receive_message', data, room=data['room'])

@socketio.on('join_room')
def handle_join_room_event(data):
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))
    join_room(data['room'])
    socketio.emit('join_room_announcement', data, room=data['room'])

@socketio.on('leave_room')
def handle_leave_room_event(data):
    app.logger.info("{} has left the room {}".format(data['username'], data['room']))
    leave_room(data['room'])
    socketio.emit('leave_room_announcement', data, room=data['room'])

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@login_manager.user_loader
def load_user(username):
    return get_user(username)

@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/contacts',methods=['POST','GET'])
def contacts():
    message = ''
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        message = request.form.get('message')
        save_contact(username, email, message)
        message = "Message Sent!"
        return render_template('contact.html',message=message)
    return render_template('IndexPage.html', message=message)

@app.route('/ChatBot')
def ChatBot():
    return render_template('ChatBot.html')
@app.route('/process',methods=['POST'])
def process():
    user_input=request.form['user_input']
    bot_response=bot.get_response(user_input)
    bot_response=str(bot_response)
    print("Friend: "+bot_response)
    return render_template('ChatBot.html',user_input=user_input,
                           bot_response=bot_response
)


if __name__ == '__main__':
    socketio.run(app, debug=True)