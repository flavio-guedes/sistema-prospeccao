import requests, json
base='http://localhost:8000'
print('HEALTH:', requests.get(base+'/api/health').json())
print('ANTHROPIC_PROXY:', requests.post(base+'/api/anthropic', json={"model":"claude-sonnet-4-6","max_tokens":5,"messages":[{"role":"user","content":"ping"}]}, headers={'Content-Type':'application/json'}).status_code)
print('EMAIL:', requests.post(base+'/api/send-email', json={"to":"test@example.com","subject":"Test","body":"Body"}, headers={'Content-Type':'application/json'}).json())
print('WHATSAPP:', requests.post(base+'/api/send-whatsapp', json={"to":"5521999999999","body":"Teste"}, headers={'Content-Type':'application/json'}).json())
