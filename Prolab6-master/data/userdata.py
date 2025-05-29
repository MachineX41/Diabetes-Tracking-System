from abc import ABC 

class UserData(ABC):
    def __init__(self,tc=None,sifre=None,mail=None,cinsiyet=None,dogumtarihi=None,profilresmi=None):
        self.isim = None
        self.tc = tc
        self.sifre = sifre
        self.mail = mail
        self.cinsiyet = cinsiyet
        self.dogumtarihi = dogumtarihi
        self.profilresmi = profilresmi