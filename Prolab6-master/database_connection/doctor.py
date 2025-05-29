from .user import User
from encryption.hashing import hash
from encryption.hashing import verify_hash
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class Doctor(User):
    def verify_login(self,data):
        username = data.tc
        password = data.sifre

        cursor = self.conn.cursor()

        cursor.execute("USE diyabet_takip")

        cursor.execute("""
            SELECT sifre FROM doktor WHERE tc_kimlik = %s;      
            """,
            (username,)
        )
        result = cursor.fetchone()
        
        if result:
            stored_password_hash = result[0].encode('utf-8')

            if verify_hash(password,stored_password_hash):
                return True
        else:
            print("Kullanıcı bulunamadı")

        cursor.close()

        return False
        

    def insert_patient(self,data,doktor_tc):
        cursor = self.conn.cursor()

        # veritabanına eriş
        cursor.execute("USE diyabet_takip")

        # Doktorlar tablosuna veri ekle 
        cursor.execute("""
            INSERT INTO hasta (
                tc_kimlik, doktor_tc ,isim, sifre, email, dogum_tarihi, cinsiyet, profil_resmi
            )
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s) 
            """ , (
                data.tc,
                doktor_tc,
                data.isim,
                hash(data.sifre),
                data.mail,
                data.dogumtarihi,
                data.cinsiyet,
                data.profilresmi
            )
        )
        
        print("hasta database eklendi")
        # bağlantıyı kapat
        cursor.close()

        self.send_email(data.mail , data.isim , data.sifre)

    
    def insert_symptoms(self,data,doktor_tc):
        cursor = self.conn.cursor()

        
        cursor.execute("USE diyabet_takip")

        for belirti in data.belirtiler:
            cursor.execute("""
                INSERT INTO hastalık_belirti (
                    doktor_tc, hasta_tc, belirti
                )
                VALUES(%s, %s, %s) 
                """ , (
                    doktor_tc,
                    data.tc,
                    belirti
                )
            )

        # bağlantıyı kapat
        cursor.close()

    def insert_diet(self,data,doktor_tc):
        cursor = self.conn.cursor()

        # veritabanına eriş
        cursor.execute("USE diyabet_takip")

        # Doktorlar tablosuna veri ekle 
        cursor.execute("""
            INSERT INTO diyet (
                doktor_tc, hasta_tc, diyet
            )
            VALUES(%s, %s, %s) 
            """ , (
                doktor_tc,
                data.hasta_tc,
                data.diyet
            )
        )

        # bağlantıyı kapat
        cursor.close()

    def insert_exercise(self,data,doktor_tc):
        cursor = self.conn.cursor()

        # veritabanına eriş
        cursor.execute("USE diyabet_takip")

        # Doktorlar tablosuna veri ekle 
        cursor.execute("""
            INSERT INTO egzersiz (
                doktor_tc, hasta_tc, egzersiz
            )
            VALUES(%s, %s, %s) 
            """ , (
                doktor_tc,
                data.hasta_tc,
                data.egzersiz
            )
        )

        # bağlantıyı kapat
        cursor.close()

    def get_patients(self,doktor_tc):
        cursor = self.conn.cursor()

        cursor.execute("USE diyabet_takip")
        
        cursor.execute("""
            SELECT
                h.tc_kimlik,
                h.isim,
                e.durum AS egzersiz_durumu,
                e.egzersiz AS egzersiz_adı,
                d.durum AS diyet_durumu,
                d.diyet AS diyet_adı,
                GROUP_CONCAT(hb.belirti) AS belirtiler
            FROM hasta h
            LEFT JOIN egzersiz e ON h.tc_kimlik = e.hasta_tc
            LEFT JOIN diyet d ON h.tc_kimlik = d.hasta_tc
            LEFT JOIN hastalık_belirti hb ON h.tc_kimlik = hb.hasta_tc
            WHERE h.doktor_tc = %s 
            GROUP BY h.tc_kimlik, h.isim, e.durum, d.durum
        """,(doktor_tc,))

        result = cursor.fetchall()

        patient_list = []

        for row in result:
            print(type(row[0]))
            patient_dict = {
                "tc": row[0],
                "name": row[1],
                "egzersiz": f"{row[3] or ''} : {row[2] or ''}",
                "diyet": f"{row[5] or ''} : {row[4] or ''}",
                "belirtiler": row[6].split(',') if row[6] else [],
                "kan_sekeri": (self.get_blood_sugar_mean(row[0]))[0]
            }

            patient_list.append(patient_dict)
        print(patient_list)
        return patient_list

        
    def send_email(self,gonderilecek_mail,isim,hasta_sifre):
        gonderen_email = "furkan19051905gs@gmail.com"
        sifre = "btde yztu kyoo zthe "  # Gmail uygulama şifresi!
        alici_email = gonderilecek_mail


        # E-posta içeriği
        mesaj = MIMEMultipart()
        mesaj["From"] = gonderen_email
        mesaj["To"] = alici_email
        mesaj["Subject"] = "Python ile Gönderilen E-Posta"

        # Gövde metni
        govde = f"Merhaba {isim},\nDiyabet Takip uygulaması şifreniz:{hasta_sifre}"
        mesaj.attach(MIMEText(govde, "plain"))

        # SMTP sunucusu üzerinden gönderim
        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(gonderen_email, sifre)
                server.sendmail(gonderen_email, alici_email, mesaj.as_string())
            print("E-posta başarıyla gönderildi.")
        except Exception as e:
            print("E-posta gönderilemedi:", e)


    def get_messages(self,doktor_tc):
        cursor = self.conn.cursor()

        cursor.execute("USE diyabet_takip")

        cursor.execute("""
                        SELECT mesaj , saat , tarih
                        FROM doktora_mesaj
                        WHERE doktor_tc = %s
                       """,(
                           doktor_tc,
                        ))
        
        result = cursor.fetchall()

        cursor.close()

        messages = []

        for message in result:
            message_dict = {}

            message_dict['message'] = message[0]

            message_dict['saat'] = message[1]

            message_dict['tarih'] = message[2]

            messages.append(message_dict)
    
        return messages
    

    def get_suggestion_diet_exercise(self,doktor_tc):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT 
                d.hasta_tc, 
                d.diyet_öneri, 
                e.egzersiz_öneri
            FROM 
                diyet_öneri d
            JOIN 
                egzersiz_öneri e ON d.hasta_tc = e.hasta_tc
            WHERE 
                d.doktor_tc = %s AND e.doktor_tc = %s
        """, (doktor_tc, doktor_tc))

        result = cursor.fetchall()
        
        cursor.close()

        messages = []

        for message in result:
            message_dict = {}

            message_dict['message'] = "Hasta TC : " + message[0] + "\nDiyet Önerisi : " +  message[1] + "\nEgzersiz Önerisi : " + message[2]

            messages.append(message_dict)

        return messages
    
    def get_filtered_patient_data(self,doktor_tc,data):
        cursor = self.conn.cursor()

        cursor.execute("USE diyabet_takip")
        
        cursor.execute("""
                        SELECT tc_kimlik
                        FROM hasta
                        WHERE doktor_tc = %s
                       """,(doktor_tc,))
        
        result = cursor.fetchall()

        print('Tc kimlikler : ',result)

        valid_patient_tc_list = []

        print(result)
        print(result[0])

        for x in result:
            mean_str = (self.get_blood_sugar_mean(x[0]))[0]
            try:
                mean = int(mean_str)
                if int(data.kan_sekeri_min) < mean < int(data.kan_sekeri_max):
                    valid_patient_tc_list.append(x[0])
            except ValueError:
                # 'Geçersiz' gibi dönüştürülemeyen değerler varsa atla
                continue
        
        
        result = []

        print('Tc kimlikler :',valid_patient_tc_list)


        for hasta_tc in valid_patient_tc_list:
            cursor.execute("""
                SELECT
                    h.tc_kimlik,
                    h.isim,
                    e.durum AS egzersiz_durumu,
                    e.egzersiz AS egzersiz_adı,
                    d.durum AS diyet_durumu,
                    d.diyet AS diyet_adı,
                    GROUP_CONCAT(hb.belirti) AS belirtiler
                FROM hasta h
                LEFT JOIN egzersiz e ON h.tc_kimlik = e.hasta_tc
                LEFT JOIN diyet d ON h.tc_kimlik = d.hasta_tc
                LEFT JOIN hastalık_belirti hb ON h.tc_kimlik = hb.hasta_tc
                WHERE h.tc_kimlik = %s
                AND EXISTS (
                    SELECT 1 FROM hastalık_belirti hb2
                    WHERE hb2.hasta_tc = h.tc_kimlik AND hb2.belirti = %s
                )
                GROUP BY h.tc_kimlik, h.isim, e.durum, e.egzersiz, d.durum, d.diyet
            """, (hasta_tc, data.belirti))

            result.append(cursor.fetchall())

        print(result)

        patient_list = []


        for group in result:
            for row in group:  # her row artık gerçek bir kayıt
                patient_dict = {
                    "tc": row[0],
                    "name": row[1],
                    "egzersiz": f"{row[3] or ''} : {row[2] or ''}",
                    "diyet": f"{row[5] or ''} : {row[4] or ''}",
                    "belirtiler": row[6].split(',') if row[6] else [],
                    "kan_sekeri": (self.get_blood_sugar_mean(row[0]))[0]
                }
                patient_list.append(patient_dict)


        print(patient_list)

        return patient_list
    

    def update_doctor_profile_photo(self,doktor_tc,path):
        cursor = self.conn.cursor()

        cursor.execute("""
                       UPDATE doktor 
                       SET profil_resmi = %s
                       WHERE tc_kimlik = %s
                       """,(path,doktor_tc))

        cursor.close()


    def get_doktor_profile_photo(self,doktor_tc):
        cursor = self.conn.cursor()

        cursor.execute("""
                       SELECT profil_resmi
                       FROM doktor
                       WHERE tc_kimlik = %s
                       """,(doktor_tc,))

        result = cursor.fetchone()

        cursor.close()

        return result[0]