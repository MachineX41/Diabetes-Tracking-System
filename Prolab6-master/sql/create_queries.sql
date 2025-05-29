DROP DATABASE IF EXISTS diyabet_takip;

CREATE DATABASE diyabet_takip 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_turkish_ci;

USE diyabet_takip;

CREATE TABLE doktor (
    tc_kimlik VARCHAR(100) PRIMARY KEY,
    sifre TEXT NOT NULL,
    email VARCHAR(100),
    dogum_tarihi DATE,
    cinsiyet  VARCHAR(10),
    profil_resmi TEXT,
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE hasta (
    tc_kimlik VARCHAR(100) PRIMARY KEY,
    doktor_tc VARCHAR(100),
    isim VARCHAR(100),
    sifre TEXT NOT NULL,
    email  VARCHAR(100),
    dogum_tarihi DATE,
    cinsiyet VARCHAR(10),
    profil_resmi TEXT,
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (doktor_tc) REFERENCES doktor(tc_kimlik)
);


CREATE TABLE hastalık_belirti (
    doktor_tc VARCHAR(100),
    hasta_tc VARCHAR(100),
    belirti VARCHAR(100),
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doktor_tc, hasta_tc, belirti),
    FOREIGN KEY (doktor_tc) REFERENCES doktor (tc_kimlik),
    FOREIGN KEY (hasta_tc) REFERENCES hasta (tc_kimlik)
);


CREATE TABLE diyet (
    doktor_tc VARCHAR(100),
    hasta_tc VARCHAR(100),
    diyet VARCHAR(100),
    saat TIME,
    tarih DATE,
    durum VARCHAR(100) DEFAULT 'Uygulanmadı',
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doktor_tc, hasta_tc,diyet),
    FOREIGN KEY (doktor_tc) REFERENCES doktor (tc_kimlik),
    FOREIGN KEY (hasta_tc) REFERENCES hasta (tc_kimlik)
);

CREATE TABLE egzersiz (
    doktor_tc VARCHAR(100),
    hasta_tc VARCHAR(100),
    egzersiz VARCHAR(100),
    saat TIME,
    tarih DATE,
    durum VARCHAR(100) DEFAULT 'Yapılmadı',
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (doktor_tc, hasta_tc,egzersiz),
    FOREIGN KEY (doktor_tc) REFERENCES doktor (tc_kimlik),
    FOREIGN KEY (hasta_tc) REFERENCES hasta (tc_kimlik)
);


CREATE TABLE kan_şekeri_ölçüm (
    hasta_tc VARCHAR(100) ,
    kan_şekeri INT,
    saat TIME,
    tarih DATE,
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(hasta_tc,saat,tarih),
    FOREIGN KEY (hasta_tc) REFERENCES hasta (tc_kimlik)
);


CREATE TABLE doktora_mesaj (
    mesaj_id INT AUTO_INCREMENT,
    doktor_tc VARCHAR(100) ,
    hasta_tc VARCHAR(100) ,
    mesaj VARCHAR(500) ,
    saat TIME,
    tarih DATE,
    PRIMARY KEY(mesaj_id),
    FOREIGN KEY (hasta_tc) REFERENCES hasta (tc_kimlik) ,
    FOREIGN KEY (doktor_tc) REFERENCES doktor (tc_kimlik)
);

CREATE TABLE insülin (
    hasta_tc VARCHAR(100),
    insülin_değeri VARCHAR(100),
    saat TIME,
    tarih DATE,
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(hasta_tc,saat,tarih),
    FOREIGN KEY (hasta_tc) REFERENCES hasta (tc_kimlik)
);

CREATE TABLE diyet_öneri(
    diyet_öneri_id INT AUTO_INCREMENT,
    doktor_tc VARCHAR(100),
    hasta_tc VARCHAR(100),
    diyet_öneri VARCHAR(100),
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(diyet_öneri_id),
    FOREIGN KEY(doktor_tc) REFERENCES doktor (tc_kimlik),
    FOREIGN KEY(hasta_tc) REFERENCES hasta (tc_kimlik)
);

CREATE TABLE egzersiz_öneri(
    egzersiz_öneri_id INT AUTO_INCREMENT,
    doktor_tc VARCHAR(100),
    hasta_tc VARCHAR(100),
    egzersiz_öneri VARCHAR(100),
    eklenme_zamanı TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(egzersiz_öneri_id),
    FOREIGN KEY(doktor_tc) REFERENCES doktor (tc_kimlik),
    FOREIGN KEY(hasta_tc) REFERENCES hasta (tc_kimlik)
);