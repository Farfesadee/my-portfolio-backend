from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in environment variables")

# Build SSL cert path (needed for TiDB Cloud)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ssl_cert_path = os.path.join(BASE_DIR, "isrgrootx1.pem")

# Use SSL if the cert file exists and connecting to TiDB Cloud
connect_args = {}
if os.path.exists(ssl_cert_path) and "tidb" in DATABASE_URL.lower():
    connect_args = {"ssl": {"ca": ssl_cert_path}}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,   # reconnect automatically if connection dropped
    pool_recycle=300,     # recycle connections every 5 min
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)
