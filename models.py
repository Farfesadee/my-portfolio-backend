# from sqlalchemy import Column, Integer, String, Text, DateTime
# from datetime import datetime
# from database import Base


# class Contact(Base):
#     __tablename__ = "contacts"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     email = Column(String(120), nullable=False)
#     message = Column(Text, nullable=False)
#     timestamp = Column(DateTime, default=datetime.utcnow)

# from sqlalchemy import Column, Integer, String, Text, DateTime, Float
# from datetime import datetime
# from database import Base

# class Contact(Base):
#     __tablename__ = "contacts"

#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     email = Column(String(120), nullable=False)
#     message = Column(Text, nullable=False)
#     latitude = Column(Float, nullable=True)       # New
#     longitude = Column(Float, nullable=True)      # New
#     timestamp = Column(DateTime, default=datetime.utcnow)




    # This will automactically create the time stamp in the database

# from sqlalchemy import Column, Integer, String, Text, DateTime, func
# from database import Base
# class Contact(Base):
#     __tablename__ = "contacts"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(100), nullable=False)
#     email = Column(String(120), nullable=False)
#     message = Column(Text, nullable=False)
#     timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    



# models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    read = Column(Boolean, default=False, nullable=False)

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, index=True, nullable=False)
    description = Column(Text)
    image_path = Column(String(1024))
    live_url = Column(String(1024))
    repo_url = Column(String(1024))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Cv(Base):
    __tablename__ = "cv"
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=True)
    file_url = Column(String(1024), nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
