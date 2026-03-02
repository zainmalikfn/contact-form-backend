from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import os

app = FastAPI()

# This lets your Vercel frontend talk to this backend
# "*" means allow any website (fine for learning, lock it down later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read secrets from environment variables (you set these on Render)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

# Connect to Supabase
db = create_client(SUPABASE_URL, SUPABASE_KEY)


# This defines what we expect the form to send us
class FormData(BaseModel):
    name: str
    email: str
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submit")
def submit(form: FormData):

    # Basic checks
    if form.name == "":
        return {"error": "Name is empty"}
    if "@" not in form.email:
        return {"error": "Email looks wrong"}
    if form.message == "":
        return {"error": "Message is empty"}

    # Insert into Supabase
    db.table("submissions").insert({
        "name":    form.name,
        "email":   form.email,
        "message": form.message,
    }).execute()

    return {"success": True}
