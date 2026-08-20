# Sistema de Prospecção V7 — Backend

## Rodar local
```bash
cd backend
chmod +x run.sh
./run.sh
```

## Variáveis obrigatórias
- `ANTHROPIC_API_KEY`
- `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS`
- `ATZAP_URL`, `ATZAP_TOKEN`

## Deploy
Use Render, Fly, Koyeb ou VPS com:
- Python 3.11+
- porta 8000
- variáveis de ambiente configuradas
