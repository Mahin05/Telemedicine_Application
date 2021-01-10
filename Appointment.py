import sqlite3
connection = sqlite3.connect("Appointment.db")
print("Database opened successfully")
cursor = connection.cursor()
connection.execute("create table Appointment (id INTEGER PRIMARY KEY AUTOINCREMENT, PatientName TEXT , DoctorName TEXT, Disease TEXT, Contact TEXT, Schedule date)")
print("Table created successfully")
connection.close()   
