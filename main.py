from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_ANON_KEY")

# These headers are what Supabase expects for every request
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": "Bearer " + SUPABASE_KEY,
    "Content-Type": "application/json"
}


# --- Keep-alive: pings this server every 10 minutes so Render doesn't sleep ---
def keep_alive():
    time.sleep(60)
    while True:
        try:
            requests.get(os.environ.get("RENDER_EXTERNAL_URL") + "/health")
        except:
            pass
        time.sleep(600)

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

    # Post directly to Supabase REST API — no library needed
    response = requests.post(
        SUPABASE_URL + "/rest/v1/submissions",
        headers=HEADERS,
        json={
            "name":    form.name,
            "email":   form.email,
            "message": form.message,
        }
    )

    if response.status_code != 201:
        return {"error": "Database error: " + response.text}

    return {"success": True}