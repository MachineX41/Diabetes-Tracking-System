from abc import ABC 
import mysql.connector
from datetime import datetime 

class User(ABC):
    def __init__(self):
        self.conn = None

    def open_db_connection(self):
        # MySQL'e bağlanma
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "Ab123456!",
            autocommit=True
        )

        self.conn = conn
    
    def open_db(self):
        # MySQL'e bağlanma
        conn = mysql.connector.connect(
            host = "localhost",
            user = "root",
            password = "Ab123456!",
            database = "diyabet_takip",
            charset='utf8mb4',
            autocommit=True
        )

        cursor = conn.cursor()
        cursor.execute("SET NAMES utf8mb4 COLLATE utf8mb4_turkish_ci")
        cursor.close()

        self.conn = conn

    def close_db_connection(self):
        self.conn.close() 

    def find_time(self, hour):
        message = "Kan şekeri verisi başarıyla eklendi!"

        if 7 <= hour < 8:
            return "Sabah" ,message
        elif 12 <= hour < 13:
            return "Öğle" , message
        elif 15 <= hour < 16:
            return "İkindi" , message
        elif 18 <= hour < 19:
            return "Akşam" , message
        elif 22 <= hour < 23:
            return "Gece" , message
        else:
            message = "Veri kaydedildi ancak ortalama hesabına dahil edilmeyecektir lütfen istenen aralıkta girin!"
            return "Geçersiz" , message
    
    def insert_blood_sugar(self,data,tc):
        cursor = self.conn.cursor()
        tarih = datetime.strptime(data.tarih, "%Y-%m-%d").date()
        saat = datetime.strptime(data.saat, "%H:%M").time()
        
        time_of_day , message = self.find_time(saat.hour)

        print(type(data.kan_sekeri))

        # Kan şekeri tablosuna veri ekle 
        cursor.execute("""
            INSERT INTO kan_şekeri_ölçüm (
                hasta_tc, kan_şekeri  , saat , tarih
            )
            VALUES(%s, %s, %s , %s) 
            """ , (
                tc,
                int(data.kan_sekeri),
                saat,
                tarih
            )
        ) 

        print("Kan şekeri ölçüm bilgileri database girildi")

        cursor.close()

        return message
    
    def get_measurements_lenght(self,hasta_tc):
        cursor = self.conn.cursor()
        
        cursor.execute("""
                    SELECT saat, tarih
                    FROM kan_şekeri_ölçüm
                    WHERE hasta_tc = %s
                    AND saat_to_zaman(saat) <> 'Geçersiz'
                    AND tarih = (
                        SELECT MAX(tarih)
                        FROM kan_şekeri_ölçüm
                        WHERE hasta_tc = %s
                            AND saat_to_zaman(saat) <> 'Geçersiz'
                    )
                    ORDER BY saat DESC
                """, (hasta_tc, hasta_tc))
        
    
        result = cursor.fetchall()

        print("Ölçüm şeyi:",result)

        print(len(result))

        return len(result)

    def get_blood_sugar_mean(self,hasta_tc):
        cursor = self.conn.cursor()
        

        cursor.execute("""
            SELECT DATE(tarih) , saat_to_zaman(saat) AS zaman
            FROM kan_şekeri_ölçüm
            WHERE hasta_tc = %s AND saat_to_zaman(saat) <> 'Geçersiz'
            ORDER BY eklenme_zamanı DESC
            LIMIT 1
        """, (hasta_tc,))
        last_date_result = cursor.fetchone()

        blood_sugar_list = []

        if last_date_result:
            latest_date = last_date_result[0]  # bu '2025-05-24' gibi bir tarih olur

            cursor.execute("""
                SELECT saat_to_zaman(saat) AS zaman, kan_şekeri
                FROM kan_şekeri_ölçüm
                WHERE hasta_tc = %s
                AND DATE(tarih) = %s
                AND saat_to_zaman(saat) <> 'Geçersiz'
                ORDER BY saat ASC
            """, (hasta_tc, latest_date))

            blood_sugar_list = cursor.fetchall()

        if len(blood_sugar_list) == 0:
            return ("Geçersiz", None, None)
        

        print(blood_sugar_list)

        blood_sugar_dict = {}

        for x in blood_sugar_list:
            blood_sugar_dict[x[0]] = x[1]

        print(blood_sugar_dict)

        return self.calculate_blood_sugar_mean(blood_sugar_dict,hasta_tc)

    
    def calculate_blood_sugar_mean(self,blood_sugar_dict,hasta_tc):
        cursor = self.conn.cursor()


        cursor.execute("""
                       SELECT saat_to_zaman(saat) AS zaman , saat ,tarih
                       FROM kan_şekeri_ölçüm
                       WHERE hasta_tc = %s and saat_to_zaman(saat) <> 'Geçersiz'
                       ORDER BY eklenme_zamanı DESC
                       LIMIT 1
                       """,(hasta_tc,))            
        
        result = cursor.fetchall()

        cursor.close()

        print(result)

        zaman = result[0][0] if result else None

        saat = result[0][1]

        tarih = result[0][2]

        print(zaman)

        print(saat)

        print(tarih)

        if zaman == "Geçersiz":
            return "Geçersiz" , None , None 
        times = ['Sabah', 'Öğle', 'İkindi', 'Akşam', 'Gece']
        

        for i, time in enumerate(times):
            if time == zaman:
                # Yalnızca zaman'a kadar olan (ve girilmiş) değerleri kullan
                values = [float(blood_sugar_dict[t]) for t in times[:i+1] if t in blood_sugar_dict]
                print(values)
                if values:
                    mean = sum(values) / len(values)
                    break
        
        return int(mean) , saat , tarih
    
    def control_validation_of_date(self,hasta_tc,saat,tarih):
         cursor = self.conn.cursor()
        
         cursor.execute("""
                       SELECT saat_to_zaman(saat) AS zaman,kan_şekeri
                       FROM kan_şekeri_ölçüm
                       WHERE hasta_tc = %s and saat = %s and tarih = %s and saat_to_zaman(saat) <> 'Geçersiz'
                       """,(hasta_tc,saat,tarih))
        
         result = cursor.fetchone()

         if result is None :
             return "Geçersiz"


    def suggest_insulin(self,hasta_tc,data):
        if self.control_validation_of_date(hasta_tc,data.saat,data.tarih) == "Geçersiz":
            return "Geçersiz"
        
        bs_value , saat , tarih = self.get_blood_sugar_mean(hasta_tc)

        if bs_value == "Geçersiz":
            return "Geçersiz"

        değer = ""

        if bs_value <= 70 :
            değer = "Yok"
        elif 70 < bs_value <= 110:
            değer = "Yok"
        elif 110 < bs_value <= 150:
            değer = "1 ml"
        elif 151 <= bs_value < 200:
            değer = "2 ml"
        elif 200 <= bs_value :
            değer = "3 ml"
        
        self.add_insulin(hasta_tc,değer,saat,tarih)

        return değer

    def add_insulin(self,tc,insülin,saat,tarih):
        cursor = self.conn.cursor()

        #zaman , _  = self.find_time(saat.total_seconds()/3600)

        print(str(saat))


        cursor.execute("""
                       INSERT INTO insülin (
                        hasta_tc , insülin_değeri  , saat ,tarih
                       ) VALUES (%s , %s , %s , %s )
                       """,(
                           tc,
                           insülin,
                           str(saat),
                           tarih
                       )
                    )
        
        cursor.close()

    
    def send_message_to_doc_for_bs(self,measure,blood_sugar,end_of_day):
        if end_of_day == 1:
            if measure == 0:
                return "Hasta gün boyunca kan şekeri ölçümü yapmamıştır.Acil takip önerilir."
            elif measure < 3 :
                return "Hastanın günlük kan şekeri ölçüm sayısı yetersiz (<3).Durum izlenmelidir."
            elif 70 <= blood_sugar <= 110:
                return "Kan şekeri seviyesi normal aralıkta. Hiçbir işlem gerekmez."
            elif 110 <= blood_sugar <= 150:
                return "Hastanın kan şekeri 111-150 mg/dL arasında. Durum izlenmeli."
            elif 151 <= blood_sugar <= 200:
                return "Hastanın kan şekeri 151-200 mg/dL arasında. Diyabet kontrolü gereklidir."
        
        if blood_sugar > 200 :
            return "Hastanın kan şekeri 200 mg/dL'nin üzerinde.Hiperglisemi durumu. Acil müdahale gerekebilir."
        elif blood_sugar < 70 :
            return "Hastanın kan şekeri seviyesi 70 mg/dL'nin altına düştü. Hipoglisemi riski! Hızlı müdahale gerekebilir."
        
    def get_last_time_date(self,hasta_tc):
        cursor = self.conn.cursor(buffered=True)

        cursor.execute("""
                       SELECT saat , tarih
                       FROM kan_şekeri_ölçüm
                       WHERE hasta_tc = %s 
                       ORDER BY tarih DESC , saat DESC 
                       """,
                       (hasta_tc,))
        
        result = cursor.fetchone()
        
        cursor.close()    

        if result is None:
            return None , None

        return result[0] , result[1]

    
    def save_message_to_db(self,end_of_day,hasta_tc,data=None):
        if data is None:
            from app import BloodSugarData
            data = BloodSugarData(tarih="",saat="",kan_sekeri="")
            data.saat , data.tarih = self.get_last_time_date(hasta_tc)

        if self.control_validation_of_date(hasta_tc,data.saat,data.tarih) == "Geçersiz" and data.tarih != None and data.saat != None:
            return "Geçersiz"
        
        cursor = self.conn.cursor()

        cursor.execute("""
                    SELECT saat, tarih
                    FROM kan_şekeri_ölçüm
                    WHERE hasta_tc = %s
                    AND saat_to_zaman(saat) <> 'Geçersiz'
                    AND tarih = (
                        SELECT MAX(tarih)
                        FROM kan_şekeri_ölçüm
                        WHERE hasta_tc = %s
                            AND saat_to_zaman(saat) <> 'Geçersiz'
                    )
                    ORDER BY saat DESC
                """, (hasta_tc, hasta_tc))


        result = cursor.fetchall()

        print(result)

        measure = 0

        blood_sugar = self.get_blood_sugar_mean(hasta_tc)[0]

        if result:
            saat = result[0][0]
            tarih = result[0][1]
            measure = len(result) 
        else:
            blood_sugar = None
            saat = None
            tarih = None
            print(f"[UYARI] hasta_tc = {hasta_tc} için kan şekeri verisi bulunamadı.")
        

        print('Blood sugar',blood_sugar)

        print()

        msg = self.send_message_to_doc_for_bs(measure, blood_sugar, end_of_day)
        if msg is None:
            return ""
        message = f"Hasta TC : {hasta_tc} , {msg}"

             
        
        if message is None:
            return None
        
        print(message)

        cursor.execute("""
                       SELECT doktor_tc
                       FROM hasta
                       WHERE tc_kimlik = %s
                       """,
                       (hasta_tc,))
        
        result = cursor.fetchone()


        doktor_tc = result[0]


        print(doktor_tc)

        print(type(doktor_tc))

        cursor.execute("""
                        INSERT INTO doktora_mesaj(
                        doktor_tc , hasta_tc ,mesaj , saat , tarih
                       )
                        VALUES (%s ,%s ,%s, %s, %s)
                       """,(
                           doktor_tc,hasta_tc,message,saat,tarih
                       ))
        
        cursor.close()
