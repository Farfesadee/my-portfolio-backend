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




from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from models import Contact, Base
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import os
load_dotenv()

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
from dotenv import load_dotenv
from resend import Resend

# Load environment variables
load_dotenv()
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
resend = Resend(api_key=RESEND_API_KEY)
app = FastAPI()
# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Create tables
Base.metadata.create_all(bind=engine)
# Pydantic model
class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
# DB dependency
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
        # :one: Save in DB
        new_message = Contact(
            name=data.name,
            email=data.email,
            message=data.message
        )
        db.add(new_message)
        db.commit()
        db.refresh(new_message)
        # :two: Send email via Resend
        try:
            resend.emails.send(
                from_="you@yourdomain.com",  # must be verified in Resend
                to=["you@yourdomain.com"],   # your personal inbox
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