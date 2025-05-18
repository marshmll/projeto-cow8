from base64 import b64encode, b64decode
import bcrypt

class Pbkdf():
    @staticmethod
    def hash_password(password: str):
        salt = bcrypt.gensalt(rounds=12)
        salt_str = b64encode(salt).decode('utf-8')
        key = bcrypt.kdf(password=password.encode(), salt=salt, desired_key_bytes=32, rounds=100)
        key_str = b64encode(key).decode('utf-8')
        
        return (key_str, salt_str)
    
    @staticmethod
    def is_valid_password(key: str, salt: str, password: str):
        entered_key = bcrypt.kdf(password=password.encode(), salt=b64decode(salt), desired_key_bytes=32, rounds=100)
        return entered_key == b64decode(key)