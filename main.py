from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from supabase import create_client
import os
import threading
import time
import requests

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Using anon key instead of service role key
# The anon key is safe to use on the backend when RLS is enabled on the table
# RLS policy (set in Supabase) controls what the anon key is allowed to do
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

db = create_client(SUPABASE_URL, SUPABASE_KEY)


# --- Keep-alive: pings this server every 10 minutes so Render doesn't sleep ---
def keep_alive():
    # Wait 1 minute after startup before starting pings
    time.sleep(60)
    while True:
        try:
            requests.get(os.environ.get("RENDER_EXTERNAL_URL") + "/health")
        except:
            pass
        time.sleep(600)  # ping every 10 minutes

# Runs in the background, doesn't block anything
threading.Thread(target=keep_alive, daemon=True).start()
# ------------------------------------------------------------------------------


class FormData(BaseModel):
    name: str
    email: str
    message: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/submit")
def submit(form: FormData):

    if form.name == "":
        return {"error": "Name is empty"}
    if "@" not in form.email:
        return {"error": "Email looks wrong"}
    if form.message == "":
        return {"error": "Message is empty"}

    db.table("submissions").insert({
        "name":    form.name,
        "email":   form.email,
        "message": form.message,
    }).execute()

    return {"success": True}