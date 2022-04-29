from passlib.context import CryptContext

pass_ctx = CryptContext(schemes=["bcrypt"])


def get_hashed_password(plain_text:str)->str:
    return pass_ctx.hash(plain_text)

def verify_password(plain_text:str,hashed_password)->bool:
    return pass_ctx.verify(plain_text,hashed_password)


