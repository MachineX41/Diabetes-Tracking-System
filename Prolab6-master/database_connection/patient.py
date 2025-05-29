from .user import User
from encryption.hashing import verify_hash


class Patient(User):
    def __init__(self):
        self.conn = None

    def verify_login(self,data):
        username = data.tc
        password = data.sifre

        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT sifre FROM hasta WHERE tc_kimlik = %s;      
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
    
        
    def update_exercise(self,data,tc):
        cursor = self.conn.cursor()


        cursor.execute("""
                       UPDATE egzersiz
                       SET durum = %s , saat = %s ,tarih = %s
                       WHERE hasta_tc = %s
                      """
                      ,(data.egzersiz,data.saat,data.tarih,tc)
                      )

        cursor.close()



    def update_diet(self,data,tc):
        cursor = self.conn.cursor()


        cursor.execute("""
                       UPDATE diyet
                       SET durum = %s , saat = %s ,tarih = %s
                       WHERE hasta_tc = %s
                      """
                      ,(data.diyet,data.saat,data.tarih,tc)
                      )

        cursor.close()

    
    

    def get_belirtiler(self,hasta_tc):
        cursor = self.conn.cursor()
        

        cursor.execute("""
                SELECT belirti
                FROM hastalık_belirti
                WHERE hasta_tc = %s    
            """,(hasta_tc,)
        )

        result = cursor.fetchall()
        
        cursor.close()

        belirtiler = [item[0] for item in result]

        print('Belirtiler : ',belirtiler)

        return belirtiler
    
    def get_doctor_tc(self,hasta_tc):
        cursor = self.conn.cursor()


        cursor.execute("""
                       SELECT doktor_tc
                       FROM hasta
                       WHERE tc_kimlik = %s
                       """,( hasta_tc,))

        doktor_tc = cursor.fetchone()
        print("doktor_tc: ",doktor_tc)
        cursor.close()

        return doktor_tc[0]

    def save_suggestion_diet_exercise(self,hasta_tc):
        suggestion = {}

        suggestion['Diyet'] = ""
        suggestion['Egzersiz'] = ""

        doktor_tc = self.get_doctor_tc(hasta_tc)

        blood_sugar , _ , _ = self.get_blood_sugar_mean(hasta_tc)

        belirtiler = self.get_belirtiler(hasta_tc)

        if isinstance(blood_sugar, str):
            return 
        
        if blood_sugar < 70:
            if {"Nöropati", "Polifaji", "Yorgunluk"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Dengeli Beslenme"
                suggestion['Egzersiz'] = "Yok"
        elif 110 > blood_sugar >= 70:
            if {"Yorgunluk", "Kilo Kaybı"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Az Şekerli Diyet"
                suggestion['Egzersiz'] = "Yürüyüş"
            elif {"Polifaji", "Polidipsi"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Dengeli Beslenme"
                suggestion['Egzersiz'] = "Yürüyüş"
        elif 180 > blood_sugar >= 110:
            if {"Bulanık Görme", "Nöropati"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Az Şekerli Diyet"
                suggestion['Egzersiz'] = "Klinik Egzersiz"
            elif {"Poliüri", "Polidipsi"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Şekersiz Diyet"
                suggestion['Egzersiz'] = "Klinik Egzersiz"
            elif {"Yorgunluk","Nöropati"," Bulanık Görme"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Az Şekerli Diyet"
                suggestion['Egzersiz'] = "Yürüyüş"
        elif blood_sugar >= 180:
            if {"Yaraların Yavaş İyileşmesi", "Polifaji", "Polidipsi"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Şekersiz Diyet"
                suggestion['Egzersiz'] = "Klinik Egzersiz"
            elif {"Yaraların Yavaş İyileşmesi", "Kilo Kaybı"}.issubset(set(belirtiler)):
                suggestion['Diyet'] = "Şekersiz Diyet"
                suggestion['Egzersiz'] = "Yürüyüş"

        print("Suggestion :",suggestion)
        
        cursor = self.conn.cursor()


        cursor.execute("""
                       INSERT INTO diyet_öneri(
                       doktor_tc , hasta_tc , diyet_öneri 
                       ) VALUES(%s, %s, %s)
                       """,(
                           doktor_tc,
                           hasta_tc,
                           suggestion['Diyet']
                       ))
        
        cursor.execute("""
                       INSERT INTO egzersiz_öneri(
                       doktor_tc , hasta_tc  , egzersiz_öneri
                       ) VALUES(%s, %s, %s)
                       """,(
                           doktor_tc,
                           hasta_tc,
                           suggestion['Egzersiz']
                       ))

        cursor.close()

    
    def get_data_by_date(self,hasta_tc,date):
        cursor = self.conn.cursor()


        cursor.execute("""
                    SELECT DISTINCT 
                        k.tarih, 
                        TIME_FORMAT(k.saat, '%H:%i') AS saat, 
                        saat_to_zaman(k.saat) AS zaman, 
                        k.kan_şekeri, 
                        COALESCE(i.insülin_değeri, 'Yok') AS insülin
                    FROM kan_şekeri_ölçüm k
                    LEFT JOIN insülin i
                        ON k.hasta_tc = i.hasta_tc 
                        AND k.tarih = i.tarih
                        AND k.saat = i.saat
                    WHERE k.hasta_tc = %s 
                    AND k.tarih = %s
                """, (hasta_tc, date))

        

        result = cursor.fetchall()

        cursor.close()

        print(result)

        messages = []

        for x in result:
            message = {}
            
            message['tarih'] = x[0]

            message['saat'] = x[1]

            message['zaman'] = x[2]

            message['kan_şekeri'] = x[3]

            message['insülin'] = x[4]

            messages.append(message)

        print(messages)

        return messages
    
    def get_bs_i_data(self,hasta_tc):
        cursor = self.conn.cursor()


        cursor.execute("""
                    SELECT 
                        k.tarih,
                        TIME_FORMAT(k.saat, '%H:%i') AS saat,
                        saat_to_zaman(k.saat) AS zaman,
                        k.kan_şekeri,
                        COALESCE(i.insülin_değeri, 'Yok') AS insülin
                    FROM kan_şekeri_ölçüm k
                    LEFT JOIN (
                        SELECT DISTINCT hasta_tc, tarih, saat, insülin_değeri
                        FROM insülin
                    ) i 
                    ON k.hasta_tc = i.hasta_tc 
                    AND k.tarih = i.tarih 
                    AND k.saat = i.saat
                    WHERE k.hasta_tc = %s
                    ORDER BY k.tarih, k.saat
                """, (hasta_tc,))

        
        result = cursor.fetchall()
        
        cursor.close()

        messages = []

        for x in result:
            message = {}
            
            message['tarih'] = x[0]

            message['saat'] = x[1]

            message['zaman'] = x[2]

            message['kan_şekeri'] = x[3]

            message['insülin'] = x[4]

            message['ortalama'] , _ , _ = self.get_blood_sugar_mean(hasta_tc)

            messages.append(message)
        
        print(messages)

        return messages
    
    def get_diet_exercise_data(self,hasta_tc):
        cursor = self.conn.cursor()


        cursor.execute("""
                        SELECT d.diyet , d.durum ,e.egzersiz , e.durum
                        FROM diyet d
                        LEFT JOIN egzersiz e
                        ON d.hasta_tc = e.hasta_tc
                        WHERE d.hasta_tc = %s
                       """,(hasta_tc,))
        
        result = cursor.fetchall()
        cursor.close()
        
        messages = []

        for x in result:
            message = {}
            
            message['diyet_adı'] = x[0]

            message['diyet_durum'] = x[1]

            message['egzersiz_adı'] = x[2]

            message['egzersiz_durum'] = x[3]

            messages.append(message)

        return messages
    
    def update_patient_profile_photo(self,hasta_tc,path):
        cursor = self.conn.cursor()

        cursor.execute("""
                       UPDATE hasta 
                       SET profil_resmi = %s
                       WHERE tc_kimlik = %s
                       """,(path,hasta_tc))

        cursor.close()

    def get_patient_profile_photo(self,hasta_tc):
        cursor = self.conn.cursor()

        cursor.execute("""
                       SELECT profil_resmi
                       FROM hasta
                       WHERE tc_kimlik = %s
                       """,(hasta_tc,))

        result = cursor.fetchone()

        cursor.close()

        return result[0]