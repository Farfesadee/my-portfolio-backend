from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from sqlalchemy.orm import Session
from models import Contact, Project, Cv, Base
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
import resend
import httpx

# Load environment variables
load_dotenv()
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
ADMIN_SECRET = os.getenv("ADMIN_SECRET")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "llama-3.3-70b-versatile"

# Resend setup
resend.api_key = RESEND_API_KEY

# Initialize app
app = FastAPI()

# Health check
@app.get("/")
def health_check():
    return {"status": "Portfolio backend is live"}

# Create DB tables (skip in production unless explicitly allowed)
if os.getenv("ENV") != "production" or os.getenv("ALLOW_DB_CREATE") == "true":
    Base.metadata.create_all(bind=engine)

# CORS
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


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    system_prompt: Optional[str] = None


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
# Admin Helper
# -------------------------------

def verify_admin(secret: str):
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Unauthorized")


# -------------------------------------------------------------
# PUBLIC ROUTES
# -------------------------------------------------------------

@app.post("/chat")
async def chat(data: ChatRequest):
    """Proxy chat messages to Groq API (key stays server-side)."""
    if not GROQ_API_KEY:
        raise HTTPException(status_code=503, detail="Chatbot is not configured yet.")

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            *([{"role": "system", "content": data.system_prompt}] if data.system_prompt else []),
            *[{"role": m.role, "content": m.content} for m in data.messages],
        ],
        "temperature": 0.6,
        "max_tokens": 500,
    }

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                GROQ_API_URL,
                headers={
                    "Authorization": f"Bearer {GROQ_API_KEY}",
                    "Content-Type": "application/json",
                },
                json=payload,
            )
        if response.status_code != 200:
            err = response.json().get("error", {}).get("message", "Unknown Groq error")
            raise HTTPException(status_code=502, detail=err)

        reply = (
            response.json()
            .get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
            .strip()
        )
        return {"reply": reply or "I'm not sure how to answer that. Please reach out via the Contact page!"}

    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Groq API timed out. Please try again.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/contact")
def submit_contact(data: ContactRequest, db: Session = Depends(get_db)):
    """Save contact form + send email."""
    try:
        new_msg = Contact(
            name=data.name,
            email=data.email,
            message=data.message,
            latitude=data.latitude,
            longitude=data.longitude,
        )
        db.add(new_msg)
        db.commit()
        db.refresh(new_msg)

        # Try sending email via Resend
        try:
            resend.Emails.send({
                "from": SENDER_EMAIL,
                "to": [RECEIVER_EMAIL],
                "subject": f"New Message from {data.name}",
                "text": (
                    f"Name: {data.name}\n"
                    f"Email: {data.email}\n"
                    f"Message:\n{data.message}\n\n"
                    f"Location: {data.latitude}, {data.longitude}"
                ),
            })
        except Exception as e:
            print("Email failed:", e)

        return {"message": "Message submitted successfully!"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages")
def get_messages(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Public paginated messages."""
    return (
        db.query(Contact)
        .order_by(Contact.timestamp.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


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


# -------------------------------------------------------------
# ADMIN ROUTES — Messages
# NOTE: static paths (/unread, /search, /mark_all_read) MUST be
# declared BEFORE the dynamic path (/{message_id}) so FastAPI
# doesn't treat the literal word "unread" as an integer ID.
# -------------------------------------------------------------

@app.get("/admin/messages")
def admin_get_messages(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    return db.query(Contact).order_by(Contact.timestamp.desc()).all()


@app.get("/admin/messages/unread")
def get_unread_messages(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    return (
        db.query(Contact)
        .filter(Contact.read == False)
        .order_by(Contact.timestamp.desc())
        .all()
    )


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


@app.patch("/admin/messages/mark_all_read")
def mark_all_messages_read(secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    updated_count = db.query(Contact).filter(Contact.read == False).update({Contact.read: True})
    db.commit()
    return {"message": f"{updated_count} messages marked as read."}


# Dynamic path routes — must come AFTER all static paths above
@app.get("/admin/messages/{message_id}")
def admin_get_single_message(message_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    msg = db.query(Contact).filter(Contact.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg


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


@app.delete("/admin/messages/{message_id}")
def admin_delete_message(message_id: int, secret: str, db: Session = Depends(get_db)):
    verify_admin(secret)
    msg = db.query(Contact).filter(Contact.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    db.delete(msg)
    db.commit()
    return {"detail": "Message deleted successfully"}


# -------------------------------------------------------------
# ADMIN ROUTES — Projects
# -------------------------------------------------------------

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
        repo_url=data.repo_url,
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


# -------------------------------------------------------------
# ADMIN ROUTES — CV
# -------------------------------------------------------------

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
