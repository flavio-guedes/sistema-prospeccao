from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr
import os, requests, json, smtplib
from email.mime.text import MIMEText
from typing import Optional, List

app = FastAPI()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASS = os.getenv("SMTP_PASS", "")
ATZAP_URL = os.getenv("ATZAP_URL", "")
ATZAP_TOKEN = os.getenv("ATZAP_TOKEN", "")

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

@app.get("/api/health")
def health():
    return {"status": "ok"}

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
