from werkzeug.security import generate_password_hash, check_password_hash

def encrypt_password(password):
    """密码加盐哈希加密"""
    return generate_password_hash(password)

def verify_password(password_hash, password):
    """校验密码是否正确"""
    return check_password_hash(password_hash, password)
