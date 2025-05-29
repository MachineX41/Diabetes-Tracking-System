import bcrypt

def hash(data: str) -> bytes:
    # Datayı UTF-8 formatına çevir
    data_bytes = data.encode('utf-8')

    # Rastgele salt üret ve şifreyi hashle
    salt = bcrypt.gensalt()

    hashed = bcrypt.hashpw(data_bytes, salt)

    return hashed

# Şifreyi doğrulama
def verify_hash(data: str, hashed: bytes) -> bool:
    data_bytes = data.encode('utf-8')
    return bcrypt.checkpw(data_bytes, hashed)

if __name__ == '__main__':
    # Örnek kullanım
    password = "user_password123"
    hashed_password = hash(password)
    print("Hashed Password:", hashed_password)

    # Doğrulama
    is_valid = verify_hash("user_password123", hashed_password)
    print("Password Valid:", is_valid)  # True