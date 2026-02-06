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
# from fastapi import FastAPI, Depends, HTTPException
# from pydantic import BaseModel, EmailStr
# from typing import Optional
# from sqlalchemy.orm import Session
# from models import Contact, Project, Base
# from database import SessionLocal, engine
# from fastapi.middleware.cors import CORSMiddleware
# from dotenv import load_dotenv
# import os
# import resend   # Correct import

# # Load environment variables
# load_dotenv()
# RESEND_API_KEY = os.getenv("RESEND_API_KEY")
# SENDER_EMAIL = os.getenv("SENDER_EMAIL")
# RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
# ADMIN_SECRET = os.getenv("ADMIN_SECRET")

# # Initialize Resend client
# resend.api_key = RESEND_API_KEY


# # Initialize FastAPI app
# app = FastAPI()


# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Allow all for development
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# # Create database tables
# Base.metadata.create_all(bind=engine)


# # Pydantic model
# class ContactRequest(BaseModel):
#     name: str
#     email: EmailStr
#     message: str
#     latitude: Optional[float] | None = None
#     longitude: Optional[float] | None = None


# class ProjectRequest(BaseModel):
#     title: str
#     slug: str
#     description: Optional[str] = None
#     image_path: Optional[str] = None
#     live_url: Optional[str] = None
#     repo_url: Optional[str] = None


# # Database dependency
# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()


# # Contact endpoint
# @app.post("/contact")
# def submit_contact(data: ContactRequest, db: Session = Depends(get_db)):
#     try:
#         # :one: Save to DB
#         new_message = Contact(
#             name=data.name,
#             email=data.email,
#             message=data.message,
#             latitude=data.latitude,
#             longitude=data.longitude

#         )
#         db.add(new_message)
#         db.commit()
#         db.refresh(new_message)

        
#         # :two: Send email via Resend
#         try:
#             resend.send(
#                 from_=SENDER_EMAIL,
#                 to=[RECEIVER_EMAIL],
#                 subject=f"New Contact Message from {data.name}",
#                 text=f"Name: {data.name}\nEmail: {data.email}\nMessage:\n{data.message}"
#             )
#         except Exception as email_error:

#             # Email failed but DB still saved
#             print(f"Email sending failed: {email_error}")
#         return {"message": "Contact form submitted successfully!"}
#     except Exception as db_error:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Server error: {db_error}")




# @app.get("/messages")
# def get_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     messages = db.query(Contact).order_by(Contact.timestamp.desc()).offset(skip).limit(limit).all()
#     return messages 

# # If you want only 10 recent messages

# @app.get("/messages/latest")
# def get_latest_messages(db: Session = Depends(get_db)):
#     messages = db.query(Contact).order_by(Contact.timestamp.desc()).limit(10).all()
#     return messages




#     # ----------------------------
# # ADMIN ROUTES (Backend)
# # ----------------------------
# # Simple admin auth with ?secret=ADMIN_SECRET
# def verify_admin(secret: str):
#     if secret != ADMIN_SECRET:
#         raise HTTPException(status_code=401, detail="Unauthorized")
    
# # Get ALL messages
# @app.get("/admin/messages")
# def get_all_messages(secret: str, db: Session = Depends(get_db)):
#     verify_admin(secret)
#     messages = db.query(Contact).order_by(Contact.timestamp.desc()).all()
#     return messages

# # Get ONE message by ID
# @app.get("/admin/messages/{message_id}")
# def get_one_message(message_id: int, secret: str, db: Session = Depends(get_db)):
#     verify_admin(secret)
#     message = db.query(Contact).filter(Contact.id == message_id).first()
#     if not message:
#         raise HTTPException(status_code=404, detail="Message not found")
#     return message



# @app.delete("/admin/messages/{message_id}")
# def delete_message(message_id: int, secret: str, db: Session = Depends(get_db)):
#     verify_admin(secret)
#     message = db.query(Contact).filter(Contact.id == message_id).first()
#     if not message:
#         raise HTTPException(status_code=404, detail="Message not found")
#     db.delete(message)
#     db.commit()
#     return {"detail": "Message deleted"}


# @app.get("/projects")
# def get_projects(db: Session = Depends(get_db)):
#     return db.query(Project).order_by(Project.created_at.desc()).all()

# @app.get("/projects")
# def get_projects(db: Session = Depends(get_db)):
#     return db.query(Project).order_by(Project.created_at.desc()).all()

# @app.post("/projects")
# def create_project(data: ProjectRequest, secret: str, db: Session = Depends(get_db)):
#     verify_admin(secret)
#     existing = db.query(Project).filter(Project.slug == data.slug).first()
#     if existing:
#         raise HTTPException(status_code=400, detail="Project with this slug already exists")
    
#     new_project = Project(
#         title=data.title,
#         slug=data.slug,
#         description=data.description,
#         image_path=data.image_path,
#         live_url=data.live_url,
#         repo_url=data.repo_url
#     )
#     db.add(new_project)
#     db.commit()
#     db.refresh(new_project)
#     return {"message": "Project created successfully", "project": new_project}





from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy.orm import Session
from models import Contact, Project, Cv, Base
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import resend


# Load environment variables
load_dotenv()
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

# Resend setup
resend.api_key = RESEND_API_KEY


# Initialize app
app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "Portfolio backend is live"}



# Create DB tables
if os.getenv("ENV") != "production" or os.getenv("ALLOW_DB_CREATE") == "true":
    Base.metadata.create_all(bind=engine)

# CORS (allow all for now — restrict later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------
# Pydantic Models
# -------------------------------

class ContactRequest(BaseModel):
    name: str
    email: EmailStr
    message: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class ProjectRequest(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    image_path: Optional[str] = None
    live_url: Optional[str] = None
    repo_url: Optional[str] = None

class CvRequest(BaseModel):
    content: Optional[str] = None
    file_url: Optional[str] = None


# -------------------------------
# DB Dependency
# -------------------------------

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------------
# Admin Helpers
# -------------------------------

def verify_admin(secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")


# -------------------------------------------------------------
# PUBLIC ROUTES
# -------------------------------------------------------------

@app.post("/contact")
def submit_contact(data: ContactRequest, db: Session = Depends(get_db)):
    """Save contact form + send email."""
    try:
        new_msg = Contact(
            name=data.name,
            email=data.email,
            message=data.message,
            latitude=data.latitude,
            longitude=data.longitude
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)

        # Try email
        try:
            resend.send(
                from_=SENDER_EMAIL,
                to=[RECEIVER_EMAIL],
                subject=f"New Message from {data.name}",
                text=(
                    f"Name: {data.name}\n"
                    f"Email: {data.email}\n"
                    f"Message:\n{data.message}\n\n"
                    f"Location: {data.latitude}, {data.longitude}"
                )
            )
        except Exception as e:
            print("Email failed:", e)

        return {"message": "Message submitted successfully!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# @app.get("/messages")
# def get_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
#     """Public paginated messages with read status."""
#     return (
#         db.query(Contact)
#         .order_by(Contact.timestamp.desc())
#         .offset(skip)
#         .limit(limit)
#         .all()
#     )




@app.get("/messages")
def get_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Public paginated messages with read status."""
    messages = (
        db.query(Contact)
        .order_by(Contact.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return messages



@app.get("/messages/latest")
def get_latest_messages(db: Session = Depends(get_db)):
    """Latest 10 messages."""
    return db.query(Contact).order_by(Contact.timestamp.desc()).limit(10).all() 


@app.get("/cv")
def get_cv(db: Session = Depends(get_db)):
    """Public CV endpoint."""
    cv = db.query(Cv).order_by(Cv.id.desc()).first()
    if not cv:
        raise HTTPException(status_code=404, detail="CV not found")
    return cv


#  # Optional: only return necessary fields for frontend 
#     return [ 
#         {
#             "id": m.id,
#             "name": m.name,
#             "email": m.email,
#             "message": m.message,
#             "latitude": m.latitude,
#             "longitude": m.longitude,
#             "timestamp": m.timestamp,
#             "read": m.read,  # <-- show read status
#             }
#         for m in messages
#     ]





# @app.get("/projects")
# def get_projects(db: Session = Depends(get_db)):
#     """Public projects list."""
#     return db.query(Project).order_by(Project.created_at.desc()).all()


# @app.get("/projects/{slug}")
# def get_single_project(slug: str, db: Session = Depends(get_db)):
#     project = db.query(Project).filter(Project.slug == slug).first()
#     if not project:
#         raise HTTPException(status_code=404, detail="Project not found")
#     return project


# -------------------------------------------------------------
# ADMIN ROUTES
# -------------------------------------------------------------

@app.get("/admin/messages")
def admin_get_messages(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    return db.query(Contact).order_by(Contact.timestamp.desc()).all()




@app.get("/admin/messages/{message_id}")
def admin_get_single_message(message_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    msg = db.query(Contact).filter(Contact.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg




@app.get("/admin/messages/unread")
def get_unread_messages(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    
    unread_messages = db.query(Contact).filter(Contact.read == False).order_by(Contact.timestamp.desc()).all()
    return unread_messages



@app.get("/admin/messages/unread/count")
def count_unread_messages(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    count = db.query(Contact).filter(Contact.read == False).count()
    return {"unread_count": count}


@app.get("/admin/messages/search")
def search_messages(q: str, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    results = db.query(Contact).filter(
        (Contact.name.ilike(f"%{q}%")) |
        (Contact.email.ilike(f"%{q}%")) |
        (Contact.message.ilike(f"%{q}%"))
    ).order_by(Contact.timestamp.desc()).all()
    return results




# @app.patch("/admin/messages/{message_id}/unread")
# def mark_message_unread(message_id: int, secret: str, db: Session = Depends(get_db)):
#     verify_admin(secret)

#     msg = db.query(Contact).filter(Contact.id == message_id).first()
#     if not msg:
#         raise HTTPException(status_code=404, detail="Message not found")

#     msg.read = False
#     db.commit()
#     db.refresh(msg)

#     return {"message": "Message marked as unread", "message_data": msg}




@app.patch("/admin/messages/{message_id}/read")
def mark_message_read(message_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    
    msg = db.query(Contact).filter(Contact.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    
    msg.read = True
    db.commit()
    db.refresh(msg)
    
    return {"detail": f"Message {message_id} marked as read", "message": msg}



@app.patch("/admin/messages/{message_id}/unread")
def mark_message_unread(message_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)

    msg = db.query(Contact).filter(Contact.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    msg.read = False
    db.commit()
    db.refresh(msg)

    return {"message": "Message marked as unread", "message_data": msg}




@app.patch("/admin/messages/mark_all_read")
def mark_all_messages_read(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    
    # Update all messages that are currently unread
    updated_count = db.query(Contact).filter(Contact.read == False).update({Contact.read: True})
    db.commit()
    
    return {"message": f"{updated_count} messages marked as read."}




@app.delete("/admin/messages/{message_id}")
def admin_delete_message(message_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    msg = db.query(Contact).filter(Contact.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")

    db.delete(msg)
    db.commit()
    return {"detail": "Message deleted successfully"}


@app.get("/admin/projects")
def admin_list_projects(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    return db.query(Project).order_by(Project.created_at.desc()).all()


@app.post("/admin/projects")
def admin_create_project(data: ProjectRequest, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)

    existing = db.query(Project).filter(Project.slug == data.slug).first()
    if existing:
        raise HTTPException(status_code=400, detail="Slug already exists")

    project = Project(
        title=data.title,
        slug=data.slug,
        description=data.description,
        image_path=data.image_path,
        live_url=data.live_url,
        repo_url=data.repo_url
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return {"message": "Project created", "project": project}

@app.get("/admin/projects/{project_id}")
def get_project_by_id(project_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project




@app.put("/admin/projects/{project_id}")
def update_project(project_id: int, data: ProjectRequest, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    project.title = data.title
    project.slug = data.slug
    project.description = data.description
    project.image_path = data.image_path
    project.live_url = data.live_url
    project.repo_url = data.repo_url

    db.commit()
    db.refresh(project)
    return {"message": "Project updated successfully", "project": project}




@app.delete("/admin/projects/{project_id}")
def admin_delete_project(project_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    db.delete(project)
    db.commit()
    return {"message": "Project deleted successfully"}


@app.put("/admin/cv")
def admin_update_cv(data: CvRequest, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)

    cv = db.query(Cv).order_by(Cv.id.desc()).first()
    if not cv:
        cv = Cv(content=data.content, file_url=data.file_url)
        db.add(cv)
    else:
        cv.content = data.content
        cv.file_url = data.file_url

    db.commit()
    db.refresh(cv)
    return {"message": "CV updated", "cv": cv}
