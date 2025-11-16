# from fastapi import FastAPI
# from database import engine
# from models import Base
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from database import SessionLocal
# from models import Contact

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Contact, Base
from database import SessionLocal, engine

app = FastAPI()


from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(bind=engine)

# Pydantic model
class ContactRequest(BaseModel):
    name: str
    email: str
    message: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/contact")
def submit_contact(data: ContactRequest, db: Session = Depends(get_db)):
    new_message = Contact(
        name=data.name,
        email=data.email,
        message=data.message
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)

    return {"message": "Contact form submitted successfully!"}
