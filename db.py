from datetime import datetime
from bson import ObjectId
from pymongo import MongoClient, DESCENDING
from werkzeug.security import generate_password_hash
from users import User,Contact

client = MongoClient("mongodb+srv://test:test@admin.31upf.mongodb.net/<dbname>?retryWrites=true&w=majority")

fetch_database = client.get_database("Datas")
user_data_collection = fetch_database.get_collection("users")

def save_user(username,email,password,contact,gender,dob,profile_pic):
    password_hash = generate_password_hash(password)
    user_data_collection.insert_one({'username':username,'email':email,'password':password_hash, 'contact': contact,'gender':gender,'dob':dob,'profile_pic':profile_pic})

def get_user(username):
    user_data = user_data_collection.find_one({'_id':username})
    # admin_data = admin_data_collection.find_one({'_id':username})
    return User(user_data['_id'],user_data['email'],user_data['password'],user_data['contact'],user_data['gender'],user_data['dob'],user_data['profile_pic']) if user_data else None
