from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash
from users import User,Contact, Appointment

client = MongoClient("mongodb+srv://test:test@admin.31upf.mongodb.net/<dbname>?retryWrites=true&w=majority")

fetch_database = client.get_database("Datas")
admin_data_collection = fetch_database.get_collection("admins")
user_data_collection = fetch_database.get_collection("users")
rooms_collection = fetch_database.get_collection("rooms")
room_members_collection = fetch_database.get_collection("room_members")
messages_collection = fetch_database.get_collection("messages")
contact_data_collection = fetch_database.get_collection('contacts')
appointments_data_collection = fetch_database.get_collection('appointments')


# def save_doctor(username,email,password, contact,gender,dob,profile_pic):
#     password_hash = generate_password_hash(password)
#     admin_data_collection.insert_one({'_id':username,'email':email,'password':password_hash, 'contact': contact,'gender':gender,'dob':dob,'profile_pic':profile_pic})
def save_user(username,email,password,contact,gender,dob,profile_pic):
    password_hash = generate_password_hash(password)
    user_data_collection.insert_one({'_id':username,'email':email,'password':password_hash, 'contact': contact,'gender':gender,'dob':dob,'profile_pic':profile_pic})

def update_user(username,email,contact,gender,dob):
    user_data_collection.update_many({'_id':username},{'$set' : {'email':email,'contact':contact,'gender':gender,'dob':dob}})


def save_contact(name,email,message):
    contact_data_collection.insert_one({'name':name,'email':email,'message':message})
def send_appointment(username,doctors,diesease,contact,datetime,subject):
    appointments_data_collection.insert_one({'_id':username,'doctors':doctors, 'diesease': diesease,'contact':contact,'datetime':datetime,'subject':subject})
def get_user(username):
    user_data = user_data_collection.find_one({'_id':username})
    return User(user_data['_id'],user_data['email'],user_data['password'],user_data['contact'],user_data['gender'],user_data['dob'],user_data['profile_pic']) if user_data else None
# def get_doctor(username):
#     doctor_data = admin_data_collection.find_one({'_id':username})
#     return User(doctor_data['_id'],doctor_data['email'],doctor_data['password'],doctor_data['contact'],doctor_data['gender'],doctor_data['dob'],doctor_data['profile_pic'])
# save_admin('Mahin','minhaj@gmail.com','test','+880','Male',"2021-01-07",'F:\Telemedicine\static\Uploads\received_236575017256454.jpeg')
def save_room(room_name, created_by):
    room_id = rooms_collection.insert_one(
        {'name': room_name, 'created_by': created_by, 'created_at': datetime.now()}).inserted_id
    add_room_member(room_id, room_name, created_by, created_by, is_room_admin=True)
    return room_id
def update_room(room_id, room_name):
    rooms_collection.update_one({'_id': ObjectId(room_id)}, {'$set': {'name': room_name}})
    room_members_collection.update_many({'_id.room_id': ObjectId(room_id)}, {'$set': {'room_name': room_name}})

def get_room(room_id):
    return rooms_collection.find_one({'_id': ObjectId(room_id)})

def add_room_member(room_id, room_name, username, added_by, is_room_admin=False):
    room_members_collection.insert_one(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
         'added_at': datetime.now(), 'is_room_admin': is_room_admin})

def add_room_members(room_id, room_name, usernames, added_by):
    room_members_collection.insert_many(
        [{'_id': {'room_id': ObjectId(room_id), 'username': username}, 'room_name': room_name, 'added_by': added_by,
          'added_at': datetime.now(), 'is_room_admin': False} for username in usernames])

def remove_room_members(room_id, usernames):
    room_members_collection.delete_many(
        {'_id': {'$in': [{'room_id': ObjectId(room_id), 'username': username} for username in usernames]}})

def get_room_members(room_id):
    return list(room_members_collection.find({'_id.room_id': ObjectId(room_id)}))

def get_rooms_for_user(username):
    return list(room_members_collection.find({'_id.username': username}))

def is_room_member(room_id, username):
    return room_members_collection.count_documents({'_id': {'room_id': ObjectId(room_id), 'username': username}})

def is_room_admin(room_id, username):
    return room_members_collection.count_documents(
        {'_id': {'room_id': ObjectId(room_id), 'username': username}, 'is_room_admin': True})

def save_message(room_id, text, sender):
    messages_collection.insert_one({'room_id': room_id, 'text': text, 'sender': sender, 'created_at': datetime.now()})


MESSAGE_FETCH_LIMIT = 100


def get_messages(room_id, page=0):
    offset = page * MESSAGE_FETCH_LIMIT
    messages = list(
        messages_collection.find({'room_id': room_id}).sort('_id', DESCENDING).limit(MESSAGE_FETCH_LIMIT).skip(offset))
    for message in messages:
        message['created_at'] = message['created_at'].strftime("%d %b, %H:%M")
    return messages[::-1]




# def save_appointment(apn_name,created_by):
#     apn_id = appointments_data_collection.insert_one(
#         {'name':apn_name,'created_by':created_by, 'created_at':datetime.now()}).inserted_id
#     add_appointment(apn_id,apn_name,created_by,created_by)
#
# def add_appointment(apn_id,apn_name,username,ptn_name):
#     apn_data_collection.insert_many([{'_id':{'apn_id':ObjectId(apn_id),'username':username},'apn_name':apn_name,'ptn_name':ptn_name,
#                                       'apn_time':datetime.now()}])
#
# def get_apn(apn_id):
#     return appointments_data_collection.find_one({'_id': ObjectId(apn_id)})
# def is_apn_member(apn_id, username):
#     return apn_data_collection.count_documents({'_id': {'apn_id': ObjectId(apn_id), 'username': username}})