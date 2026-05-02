import bcrypt

def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(input_pw: str, stored_hash: str) -> bool:
    return bcrypt.checkpw(
        input_pw.encode('utf-8'),
        stored_hash.encode('utf-8')
    )