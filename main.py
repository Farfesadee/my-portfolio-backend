# # from fastapi import FastAPI
# # from database import engine
# # from models import Base
# # from fastapi import Depends
# # from sqlalchemy.orm import Session
# # from database import SessionLocal
# # from models import Contact

# from fastapi import FastAPI, Depends
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from models import Contact, Base
# from database import SessionLocal, engine

# app = FastAPI()


# from fastapi.middleware.cors import CORSMiddleware

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # allow all for development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# Base.metadata.create_all(bind=engine)

# # Pydantic model
# class ContactRequest(BaseModel):
#     name: str
#     email: str
#     message: str

# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.post("/contact")
# def submit_contact(data: ContactRequest, db: Session = Depends(get_db)):
#     new_message = Contact(
#         name=data.name,
#         email=data.email,
#         message=data.message
#     )
#     db.add(new_message)
#     db.commit()
#     db.refresh(new_message)

#     return {"message": "Contact form submitted successfully!"}




# main.py
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from models import Contact, Base
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import resend   # Correct import

# Load environment variables
load_dotenv()
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

# Initialize Resend client
resend.api_key = RESEND_API_KEY


# Initialize FastAPI app
app = FastAPI()


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create database tables
Base.metadata.create_all(bind=engine)


# Pydantic model
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
    latitude: Optional[float] | None = None
    longitude: Optional[float] | None = None


# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Contact endpoint
@app.post("/contact")
def submit_contact(data: ContactRequest, db: Session = Depends(get_db)):
    try:
        # :one: Save to DB
        new_message = Contact(
            name=data.name,
            email=data.email,
            message=data.message,
            latitude=data.latitude,
            longitude=data.longitude

        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)

        
        # :two: Send email via Resend
        try:
            resend.send(
                from_=SENDER_EMAIL,
                to=[RECEIVER_EMAIL],
                subject=f"New Contact Message from {data.name}",
                text=f"Name: {data.name}\nEmail: {data.email}\nMessage:\n{data.message}"
            )
        except Exception as email_error:
            
            # Email failed but DB still saved
            print(f"Email sending failed: {email_error}")
        return {"message": "Contact form submitted successfully!"}
    except Exception as db_error:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Server error: {db_error}")




@app.get("/messages")
def get_messages(db: Session = Depends(get_db)):
    messages = db.query(Contact).order_by(Contact.timestamp.desc()).all()
    return messages 

# If you want only 10 recent messages

# @app.get("/messages/latest")
# def get_latest_messages(db: Session = Depends(get_db)):
#     messages = db.query(Contact).order_by(Contact.timestamp.desc()).limit(10).all()
#     return messages




    # ----------------------------
# ADMIN ROUTES (Backend)
# ----------------------------
# Simple admin auth with ?secret=ADMIN_SECRET
def verify_admin(secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")
    
# Get ALL messages
@app.get("/admin/messages")
def get_all_messages(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    messages = db.query(Contact).all()
    return messages

# Get ONE message by ID
@app.get("/admin/messages/{message_id}")
def get_one_message(message_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    message = db.query(Contact).filter(Contact.id == message_id).first()
    if not message:
        raise HTTPException(status_code=404, detail="Message not found")
    return message