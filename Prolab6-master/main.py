from database_connection.admin import Admin
from database_connection.doctor import Doctor
from database_connection.patient import Patient
from data.doctordata import DoctorData
from data.patientdata import PatientData

def main():
    doktor_data = DoctorData(tc='12345678910',sifre='1234')
    #hasta_data = PatientData(tc='12345678910',sifre='1234')
    admin = Admin()
    admin.open_db_connection()
    admin.create_all("sql/create_queries.sql")
    admin.insert_doctor(doktor_data)
    doktor_data = DoctorData(tc='12345678911',sifre='1234')
    admin.insert_doctor(doktor_data)
    admin.close_db_connection()
    #doktor = Doctor()
    #doktor.open_db()
    #doktor.insert_patient(hasta_data,doktor_data.tc)
    #doktor.close_db_connection()
    #admin.drop_database()
    #admin.create_database()
    
