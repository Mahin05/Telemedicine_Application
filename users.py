from werkzeug.security import check_password_hash

class User():
    def __init__(self,username, email, password,contact,gender,dob, profile_pic):
        self.username = username
        self.email = email
        self.password = password
        self.contact = contact
        self.gender = gender
        self.dob = dob
        self.profile_pic = profile_pic

    @staticmethod
    def is_authenticated():
        return True

    @staticmethod
    def is_active(self):
        return True
    @staticmethod
    def is_anonymous():
        return False
    def get_id(self):
        return self.username

    def check_password(self, password_input):
        return check_password_hash(self.password, password_input)
class Contact():
    def __init__(self,name,email,message):
        self.name = name
        self.email = email
        self.message = message
class Appointment():
    def __init__(self,username,doctors,diesease,contact,datetime,subject):
        self.username= username
        self.doctors = doctors
        self.diesease = diesease
        self.contact = contact
        self.datetime = datetime
        self.subject = subject