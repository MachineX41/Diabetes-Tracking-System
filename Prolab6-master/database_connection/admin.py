from .user import User
from encryption.hashing import hash

class Admin(User):
    def create_all(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()

        cursor = self.conn.cursor()

        statements = [stmt.strip() for stmt in sql_script.strip().split(';') if stmt.strip()]
        for stmt in statements:
            try:
                cursor.execute(stmt)
            except Exception as e:
                print(f"Hata oluştu: {e} --> {stmt}")

        function_sql = """
            CREATE FUNCTION saat_to_zaman(saat TIME) RETURNS VARCHAR(10)
            BEGIN
                DECLARE zaman VARCHAR(10);

                IF saat >= '07:00:00' AND saat < '08:00:00' THEN
                    SET zaman = 'Sabah';
                ELSEIF saat >= '12:00:00' AND saat < '13:00:00' THEN
                    SET zaman = 'Öğle';
                ELSEIF saat >= '15:00:00' AND saat < '16:00:00' THEN
                    SET zaman = 'İkindi';
                ELSEIF saat >= '18:00:00' AND saat < '19:00:00' THEN
                    SET zaman = 'Akşam';
                ELSEIF saat >= '22:00:00' AND saat < '23:00:00' THEN
                    SET zaman = 'Gece';
                ELSE
                    SET zaman = 'Geçersiz';
                END IF;

                RETURN zaman;
            END
        """

        cursor.execute(function_sql)

        cursor.close()
        print(f"{file_path} dosyasındaki SQL sorguları başarıyla çalıştırıldı.")



    def insert_doctor(self,data):
        cursor = self.conn.cursor()

        # Doktorlar tablosuna veri ekle 
        cursor.execute("""
            INSERT INTO doktor (
                tc_kimlik, sifre, email, dogum_tarihi, cinsiyet, profil_resmi
            ) VALUES (%s, %s, %s, %s, %s, %s)
             """, (
                data.tc,
                hash(data.sifre),
                data.mail,
                data.dogumtarihi,
                data.cinsiyet,
                data.profilresmi
            )
        )


        # bağlantıyı kapat
        cursor.close()

    def drop_database(self):
        cursor = self.conn.cursor()

        cursor.execute("DROP DATABASE IF EXISTS diyabet_takip;")

        cursor.close()
    
    def create_database(self):
        cursor = self.conn.cursor()

        cursor.execute("""CREATE DATABASE diyabet_takip 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_turkish_ci;""")

        cursor.close()