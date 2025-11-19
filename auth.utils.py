# # auth_utils.py
# from passlib.context import CryptContext
# import jwt, os
# from datetime import datetime, timedelta
# from dotenv import load_dotenv

# load_dotenv()

# pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
# JWT_SECRET = os.getenv("JWT_SECRET", "change_me")
# JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
# ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 1440))

# def hash_password(password: str) -> str:
#     return pwd_ctx.hash(password)

# def verify_password(plain: str, hashed: str) -> bool:
#     return pwd_ctx.verify(plain, hashed)

# def create_access_token(subject: str, data: dict = None, expires_delta: timedelta | None = None) -> str:
#     to_encode = {"sub": subject}
#     if data:
#         to_encode.update(data)
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
#     to_encode.update({"exp": expire})
#     return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

# def decode_token(token: str) -> dict:
#     return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])