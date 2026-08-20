#!/bin/bash
set -e
cd /Users/mac/repo-sistema-prospeccao/backend
source .venv/bin/activate
export ANTHROPIC_API_KEY="$(grep -E '^ANTHROPIC_API_KEY=' /Users/mac/.hermes/.env | cut -d= -f2-)"
export SMTP_HOST=""
export SMTP_USER=""
export SMTP_PASS=""
export ATZAP_URL=""
export ATZAP_TOKEN=""
python3 test_local.py
