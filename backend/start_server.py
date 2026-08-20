#!/usr/bin/env python3
import os
import sys
sys.path.insert(0, '/Users/mac/repo-sistema-prospeccao/backend')

# Set env vars
os.environ['ANTHROPIC_API_KEY'] = os.popen("grep -E '^ANTHROPIC_API_KEY=' /Users/mac/.hermes/.env | cut -d= -f2-").read().strip()
os.environ['SMTP_HOST'] = ''
os.environ['SMTP_USER'] = ''
os.environ['SMTP_PASS'] = ''
os.environ['ATZAP_URL'] = ''
os.environ['ATZAP_TOKEN'] = ''
os.environ['LINKEDIN_EMAIL'] = ''
os.environ['LINKEDIN_PASSWORD'] = ''
os.environ['GOOGLE_CLIENT_ID'] = ''
os.environ['GOOGLE_CLIENT_SECRET'] = ''

import uvicorn
from main import app

uvicorn.run(app, host='0.0.0.0', port=8000)
