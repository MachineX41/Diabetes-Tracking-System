import os
from typing import List
from fastapi.staticfiles import StaticFiles
import uvicorn
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from main import main
from database_connection.doctor import Doctor
from database_connection.patient import Patient
from data.doctordata import DoctorData
from data.patientdata import PatientData
import subprocess
import threading

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


tc = ""

class LoginData(BaseModel):
    role: str
    username: str
    password: str

@app.post("/login")
async def login(data: LoginData):
    global tc
    print(f"Gelen veri: {data}")  

    doktor_data = DoctorData(tc=data.username,sifre=data.password)
    hasta_data = PatientData(tc=data.username,sifre=data.password)

    doktor = Doctor()
    hasta = Patient()
    
    if data.role == "doktor":
        doktor.open_db()
        print(doktor.verify_login(doktor_data))
        if doktor.verify_login(doktor_data):
            tc = doktor_data.tc
            print("Doktor olarak giriş başarılı!")
            doktor.close_db_connection()
            return {"message": "Giriş başarılı!","role" : data.role}
    else:
        hasta.open_db()
        print(hasta.verify_login(hasta_data))
        if hasta.verify_login(hasta_data):
            tc = hasta_data.tc
            print("Hasta olarak giriş başarılı!")
            hasta.close_db_connection()
            return {"message": "Giriş başarılı!","role" : data.role}
    
    raise HTTPException(status_code=401, detail="Kullanıcı adı veya şifre hatalı.")


@app.get("/doktor/hastalar")
async def get_patients():
    global tc
    print("deneme")
    doktor = Doctor()
    doktor.open_db()
    patients = doktor.get_patients(tc)
    doktor.close_db_connection()

    return patients


class FrontPatientData(BaseModel):
    isim : str
    tc : str
    sifre : str
    belirtiler : List[str]
    mail : str | None
    dogumtarihi : str | None
    cinsiyet : str | None
    profilresmi : str | None

@app.post("/doktor/hasta_ekle")
async def add_patient(data : FrontPatientData):
    global tc
    print(data)
    print("Belirtiler:", data.belirtiler)
    print(type(data.belirtiler))
    doktor = Doctor()
    doktor.open_db()
    doktor.insert_patient(data,tc)
    doktor.insert_symptoms(data,tc)
    doktor.close_db_connection()

    print("hasta ve semptompları database eklendi")

    return {"message":"Hasta başarıyla eklendi!"}

class diet_exercise_data_from_doctor(BaseModel):
    hasta_tc : str
    diyet : str
    egzersiz : str

@app.post("/doktor/diyet_egzersiz_ekle")
async def add_diet_exercise(data : diet_exercise_data_from_doctor):
    global tc
    doktor = Doctor()
    doktor.open_db()
    doktor.insert_diet(data,tc)
    doktor.insert_exercise(data,tc)
    doktor.close_db_connection()
    
    return {"message":"Diyet ve egzersiz başarıyla eklendi"}


class BloodSugarData(BaseModel):
    tarih : str
    saat : str
    kan_sekeri : str


@app.post("/hasta/seker_ekle")
async def add_bs(data : BloodSugarData):
    global tc
    hasta = Patient()
    hasta.open_db()
    message = hasta.insert_blood_sugar(data,tc)
    insulin_suggestion_message = hasta.suggest_insulin(tc,data)
    hasta.save_message_to_db(0,tc,data)
    measure_lenght = hasta.get_measurements_lenght(tc) 
    hasta.close_db_connection()
    
    return {
        "message": message ,
        "insulin_suggestion":insulin_suggestion_message,
        "measure_lenght" : measure_lenght
    }
class DoctorBloodSugarData(BaseModel):
    hasta_tc : str
    tarih : str
    saat : str
    kan_sekeri : str

@app.post("/doktor/seker_ekle")
async def add_bs(data : DoctorBloodSugarData):
    doktor = Doctor()
    doktor.open_db()
    message = doktor.insert_blood_sugar(data,data.hasta_tc)
    insulin_suggestion_message = doktor.suggest_insulin(data.hasta_tc,data)
    doktor.save_message_to_db(0,data.hasta_tc,data)
    measure_lenght = doktor.get_measurements_lenght(data.hasta_tc) 
    doktor.close_db_connection()
    
    return {
        "message": message ,
        "insulin_suggestion":insulin_suggestion_message,
        "measure_lenght" : measure_lenght
    }


class diet_exercise_data(BaseModel):
    tarih : str
    saat : str
    diyet : str
    egzersiz : str

@app.post("/hasta/diyet_egzersiz_guncelle")
async def update_diet(data : diet_exercise_data):
    print(data.tarih)
    print(data.saat)
    global tc
    hasta = Patient()
    hasta.open_db()
    hasta.update_diet(data,tc)
    hasta.update_exercise(data,tc)
    hasta.close_db_connection()
    
    return {"message":"Diyet ve egzersiz başarıyla güncellendi"}


class ProfilePhotoData(BaseModel):
    path : str

@app.post("/hasta/foto_guncelle")
async def update_profile_photo(data : ProfilePhotoData ):
    #file_location = os.path.join(IMAGE_DIR, data.path)
    
    global tc 
    hasta = Patient()
    hasta.open_db()
    hasta.update_patient_profile_photo(tc,data.path)
    hasta.close_db_connection()

    return {"message":"Profil fotoğrafı başarıyla database yüklendi"}

@app.get("/hasta/foto_al")
async def update_profile_photo():
    global tc 
    hasta = Patient()
    hasta.open_db()
    path = hasta.get_patient_profile_photo(tc)
    hasta.close_db_connection()

    return {"path":path}

@app.post("/doktor/foto_guncelle")
async def update_profile_photo(data : ProfilePhotoData):
    global tc 
    doktor = Doctor()
    doktor.open_db()
    doktor.update_doctor_profile_photo(tc,data.path)
    doktor.close_db_connection()

    return {"message":"Profil fotoğrafı başarıyla database yüklendi"}

@app.get("/doktor/foto_al")
async def update_profile_photo():
    global tc 
    doktor = Doctor()
    doktor.open_db()
    path = doktor.get_doktor_profile_photo(tc)
    doktor.close_db_connection()
    print(path)
    return {"path":path}

@app.post("/hasta/olcum_bitir")
async def finish_bs():
    global tc
    hasta = Patient()
    hasta.open_db()
    hasta.save_message_to_db(1,tc)
    hasta.save_suggestion_diet_exercise(tc)
    hasta.close_db_connection()
    return {"message":"Mesaj database başarıyla kaydedildi"}

@app.get("/doktor/uyarilar")
async def get_uyarilar():
    global tc
    doktor = Doctor()
    doktor.open_db()
    message1 = doktor.get_messages(tc)
    message2 = doktor.get_suggestion_diet_exercise(tc)
    doktor.close_db_connection()
    messages = []

    messages.append(message1)
    messages.append(message2)
    
    print(messages)

    return messages


@app.get("/hasta/gunluk_veri")
async def get_daily_data_patient():
    global tc
    patient = Patient()
    patient.open_db()
    message1 = patient.get_bs_i_data(tc)
    message2 = patient.get_diet_exercise_data(tc)
    patient.close_db_connection()

    messages = {}

    messages['kan_şekeri'] = message1
    messages['diyet_egzersiz'] = message2

    return messages

# Pydantic model for the request body of /doktor/günlük_veri
class DailyDataRequest(BaseModel):
    hasta_tc: str

@app.post("/doktor/gunluk_veri")
async def get_daily_data(data : DailyDataRequest):
    patient = Patient()
    patient.open_db()
    message1 = patient.get_bs_i_data(data.hasta_tc)
    message2 = patient.get_diet_exercise_data(data.hasta_tc)
    patient.close_db_connection()
    
    messages = {}

    messages['kan_şekeri'] = message1
    messages['diyet_egzersiz'] = message2

    return messages

class veri_tarih(BaseModel):
    tarih : str

@app.post("/hasta/veri_filtrele")
async def filter_insulin(data : veri_tarih):
    global tc
    patient = Patient()
    patient.open_db()
    messages = patient.get_data_by_date(tc,data.tarih)
    patient.close_db_connection()

    return messages

class filtre_verisi(BaseModel):
    kan_sekeri_min : str
    kan_sekeri_max : str
    belirti : str

@app.post("/doktor/veri_filtrele")
async def filter_insulin(data : filtre_verisi):
    global tc
    doktor = Doctor()
    doktor.open_db()
    messages = doktor.get_filtered_patient_data(tc,data)
    doktor.close_db_connection()

    return messages

def start_fastapi():
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=False)

def start_electron():
    subprocess.run(["npm", "start"])  # veya ["npx", "electron", "."]

if __name__ == "__main__":
    main()
    # FastAPI ayrı bir thread'de çalışacak
    fastapi_thread = threading.Thread(target=start_fastapi)
    fastapi_thread.start()

    # Electron'u başlat
    start_electron()