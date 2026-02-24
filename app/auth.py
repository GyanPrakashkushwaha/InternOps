from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    """
    Checks if the plain password matches the hashed password from the DB.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """
    Takes a plain password and returns a secure hash to store in the DB.
    """
    return pwd_context.hash(password[:72])