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

from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from datetime import datetime
from database import Base

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(120), nullable=False)
    message = Column(Text, nullable=False)
    latitude = Column(Float, nullable=True)       # New
    longitude = Column(Float, nullable=True)      # New
    timestamp = Column(DateTime, default=datetime.utcnow)




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
    
