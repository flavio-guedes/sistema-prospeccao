from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os, requests, json, smtplib
from email.mime.text import MIMEText
from typing import Optional, List

app = FastAPI()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "") or os.getenv("HERMES_ANTHROPIC_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ATZAP_URL = os.getenv("ATZAP_URL", "")
ATZAP_TOKEN = os.getenv("ATZAP_TOKEN", "")
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL", "")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")

class AnthropicRequest(BaseModel):
    model: str
    max_tokens: int
    messages: List[dict]
    tools: Optional[List[dict]] = None

class EmailRequest(BaseModel):
    to: EmailStr
    subject: str
    body: str
    reply_to: Optional[str] = None

class WhatsAppRequest(BaseModel):
    to: str
    body: str
    group_id: Optional[str] = None

class LinkedInRequest(BaseModel):
    action: str
    target: str
    message: Optional[str] = None

class GoogleRequest(BaseModel):
    action: str
    params: Optional[dict] = None

class IntegrationStatusResponse(BaseModel):
    linkedin: dict
    google: dict
    smtp: dict
    whatsapp: dict
    anthropic: dict

@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.get("/api/integrations/status", response_model=IntegrationStatusResponse)
def integration_status():
    return {
        "linkedin": {
            "configured": bool(LINKEDIN_EMAIL and LINKEDIN_PASSWORD),
            "email": LINKEDIN_EMAIL or None,
        },
        "google": {
            "configured": bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET),
            "client_id": GOOGLE_CLIENT_ID or None,
        },
        "smtp": {
            "configured": bool(SMTP_HOST and SMTP_USER and SMTP_PASS),
            "host": SMTP_HOST or None,
            "user": SMTP_USER or None,
        },
        "whatsapp": {
            "configured": bool(ATZAP_URL and ATZAP_TOKEN),
            "url": ATZAP_URL or None,
        },
        "anthropic": {
            "configured": bool(ANTHROPIC_API_KEY),
            "key_prefix": (ANTHROPIC_API_KEY[:7] + "..." + ANTHROPIC_API_KEY[-4:]) if ANTHROPIC_API_KEY else None,
        },
    }

@app.post("/api/integrations/linkedin/action")
def linkedin_action(req: LinkedInRequest):
    if not LINKEDIN_EMAIL or not LINKEDIN_PASSWORD:
        raise HTTPException(status_code=500, detail="LinkedIn credentials missing")
    # Placeholder for LinkedIn automation
    return {"status": "queued", "action": req.action, "target": req.target}

@app.post("/api/integrations/google/action")
def google_action(req: GoogleRequest):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google credentials missing")
    # Placeholder for Google Workspace integration
    return {"status": "queued", "action": req.action, "params": req.params or {}}

@app.post("/api/anthropic")
def anthropic_proxy(req: AnthropicRequest):
    if not ANTHROPIC_API_KEY:
        raise HTTPException(status_code=500, detail="ANTHROPIC_API_KEY missing")
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_API_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={"model": req.model, "max_tokens": req.max_tokens, "messages": req.messages, "tools": req.tools or []},
            timeout=60,
        )
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/api/send-email")
def send_email(req: EmailRequest):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        raise HTTPException(status_code=500, detail="SMTP credentials missing")
    try:
        msg = MIMEText(req.body, "plain", "utf-8")
        msg["Subject"] = req.subject
        msg["From"] = SMTP_USER
        msg["To"] = req.to
        if req.reply_to:
            msg["Reply-To"] = req.reply_to
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_USER, [req.to], msg.as_string())
        return {"status": "sent", "to": req.to}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

@app.post("/api/send-whatsapp")
def send_whatsapp(req: WhatsAppRequest):
    if not ATZAP_URL or not ATZAP_TOKEN:
        raise HTTPException(status_code=500, detail="ATZAP credentials missing")
    payload = {"to": req.to, "body": req.body}
    if req.group_id:
        payload["group_id"] = req.group_id
    try:
        r = requests.post(
            f"{ATZAP_URL}/api/send-message",
            headers={"Authorization": f"Bearer {ATZAP_TOKEN}", "Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))
