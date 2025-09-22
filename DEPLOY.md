# 🚀 Guia de Deploy em Produção

Este guia detalha como fazer deploy do sistema em diferentes plataformas de hospedagem.

## 🏗️ Arquitetura de Deploy

\`\`\`
Frontend (Netlify)     →     Backend (Render/Railway)     →     Telegram API
    ↓                            ↓                              ↓
HTML/CSS/JS            →     Flask API REST            →     Bot Messages
Static Files           →     SQLite Database           →     Group Management
\`\`\`

## 🔧 Preparação para Deploy

### 1. Estrutura de Arquivos

Organize seu projeto:
\`\`\`
telegram-bot-admin/
├── backend/
│   ├── app.py
│   ├── requirements.txt
│   ├── .env.example
│   └── ...
├── frontend/
│   ├── index.html
│   ├── static/
│   └── ...
├── README.md
└── .gitignore
\`\`\`

### 2. Arquivo .gitignore

\`\`\`gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
env.bak/
venv.bak/

# Database
*.db
*.sqlite
*.sqlite3

# Environment variables
.env
.env.local
.env.production

# Logs
*.log
logs/

# OS
.DS_Store
Thumbs.db

# IDE
.vscode/
.idea/
*.swp
*.swo

# Temporary files
*.tmp
*.temp
\`\`\`

## 🌐 Deploy do Backend

### Opção 1: Render.com (Recomendado)

#### Vantagens
- ✅ Deploy automático via Git
- ✅ SSL gratuito
- ✅ Banco de dados persistente
- ✅ Logs em tempo real
- ✅ Fácil configuração

#### Passo a passo

1. **Criar conta** em https://render.com

2. **Conectar repositório GitHub:**
   - "New" → "Web Service"
   - Conectar repositório
   - Selecionar branch (main/master)

3. **Configurar o serviço:**
   \`\`\`
   Name: telegram-bot-api
   Environment: Python 3
   Build Command: pip install -r backend/requirements.txt
   Start Command: cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app
   \`\`\`

4. **Configurar variáveis de ambiente:**
   \`\`\`
   BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
   ADMIN_PASSWORD=senha_super_segura_123
   SECRET_KEY=chave_jwt_muito_secreta_456
   FLASK_ENV=production
   \`\`\`

5. **Deploy automático** será executado

6. **Testar:** Acesse `https://seu-app.onrender.com/health`

#### Configuração avançada

**render.yaml** (opcional):
\`\`\`yaml
services:
  - type: web
    name: telegram-bot-api
    env: python
    buildCommand: pip install -r backend/requirements.txt
    startCommand: cd backend && gunicorn -w 4 -b 0.0.0.0:$PORT app:app
    envVars:
      - key: FLASK_ENV
        value: production
\`\`\`

### Opção 2: Railway.app

#### Vantagens
- ✅ Deploy simples via CLI
- ✅ Banco de dados PostgreSQL
- ✅ Scaling automático
- ✅ Integração com GitHub

#### Passo a passo

\`\`\`bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Inicializar projeto
cd telegram-bot-admin
railway init

# 4. Configurar variáveis de ambiente
railway variables set BOT_TOKEN=seu_token_aqui
railway variables set ADMIN_PASSWORD=senha_segura
railway variables set SECRET_KEY=chave_jwt_secreta
railway variables set FLASK_ENV=production

# 5. Deploy
railway up

# 6. Obter URL
railway domain
\`\`\`

#### Configuração do banco PostgreSQL (opcional)

\`\`\`bash
# Adicionar PostgreSQL
railway add postgresql

# Obter URL de conexão
railway variables
# Procure por DATABASE_URL
\`\`\`

Modificar `app.py` para usar PostgreSQL:
\`\`\`python
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')
if DATABASE_URL:
    # Usar PostgreSQL
    url = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
else:
    # Usar SQLite local
    conn = sqlite3.connect('bot_database.db')
\`\`\`

### Opção 3: Deta.sh

#### Vantagens
- ✅ Gratuito para projetos pequenos
- ✅ Deploy via CLI
- ✅ Banco de dados NoSQL integrado

#### Passo a passo

\`\`\`bash
# 1. Instalar Deta CLI
curl -fsSL https://get.deta.dev/cli.sh | sh

# 2. Login
deta login

# 3. Criar projeto
cd backend
deta new --python telegram-bot-api

# 4. Configurar variáveis
deta update -e .env

# 5. Deploy
deta deploy
\`\`\`

## 🎨 Deploy do Frontend

### Opção 1: Netlify (Recomendado)

#### Vantagens
- ✅ Deploy automático via Git
- ✅ CDN global
- ✅ SSL gratuito
- ✅ Domínio personalizado
- ✅ Formulários e funções

#### Método 1: Drag & Drop

1. **Preparar frontend:**
   \`\`\`bash
   cd frontend
   # Editar static/js/config.js
   # Alterar BASE_URL para URL do backend
   \`\`\`

2. **Fazer upload:**
   - Acesse https://app.netlify.com
   - Arraste a pasta `frontend` para a área de deploy
   - Aguarde o deploy

#### Método 2: Git Integration

1. **Conectar repositório:**
   - "New site from Git"
   - Conectar GitHub/GitLab
   - Selecionar repositório

2. **Configurar build:**
   \`\`\`
   Base directory: frontend
   Build command: (deixar vazio)
   Publish directory: .
   \`\`\`

3. **Deploy automático** a cada push

#### Configuração avançada

**netlify.toml:**
\`\`\`toml
[build]
  base = "frontend"
  publish = "."

[[headers]]
  for = "/static/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000"

[[redirects]]
  from = "/api/*"
  to = "https://seu-backend.onrender.com/api/:splat"
  status = 200
\`\`\`

### Opção 2: Vercel

\`\`\`bash
# 1. Instalar Vercel CLI
npm i -g vercel

# 2. Deploy
cd frontend
vercel

# 3. Configurar domínio
vercel --prod
\`\`\`

### Opção 3: GitHub Pages

1. **Configurar repositório:**
   - Settings → Pages
   - Source: Deploy from branch
   - Branch: main, folder: /frontend

2. **Configurar URL da API:**
   \`\`\`javascript
   // static/js/config.js
   const API_CONFIG = {
       BASE_URL: 'https://seu-backend.onrender.com/api'
   };
   \`\`\`

## 🔒 Configuração de Segurança

### 1. Variáveis de Ambiente

**Backend (.env):**
\`\`\`env
# Produção
BOT_TOKEN=token_real_do_bot
ADMIN_PASSWORD=senha_muito_segura_123!@#
SECRET_KEY=chave_jwt_super_secreta_456$%^
FLASK_ENV=production

# Opcional
DATABASE_URL=postgresql://user:pass@host:port/db
CORS_ORIGINS=https://seu-frontend.netlify.app
\`\`\`

### 2. CORS Configuration

\`\`\`python
# app.py
from flask_cors import CORS

# Configurar CORS para produção
if os.getenv('FLASK_ENV') == 'production':
    CORS(app, origins=[
        'https://seu-frontend.netlify.app',
        'https://seu-dominio.com'
    ])
else:
    CORS(app)  # Permitir todas as origens em desenvolvimento
\`\`\`

### 3. Rate Limiting

\`\`\`python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

@app.route('/api/send_message', methods=['POST'])
@limiter.limit("10 per minute")
@require_auth
def send_message():
    # ...
\`\`\`

## 📊 Monitoramento

### 1. Health Checks

\`\`\`python
@app.route('/health')
def health_check():
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': 'connected' if test_db_connection() else 'error'
    })
\`\`\`

### 2. Logging

\`\`\`python
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
\`\`\`

### 3. Error Tracking

Integração com Sentry:
\`\`\`python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="https://your-dsn@sentry.io/project-id",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
\`\`\`

## 🔄 CI/CD Pipeline

### GitHub Actions

**.github/workflows/deploy.yml:**
\`\`\`yaml
name: Deploy

on:
  push:
    branches: [ main ]

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Render
      run: |
        curl -X POST ${{ secrets.RENDER_DEPLOY_HOOK }}

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Deploy to Netlify
      run: |
        npm install -g netlify-cli
        netlify deploy --prod --dir=frontend --auth=${{ secrets.NETLIFY_AUTH_TOKEN }}
\`\`\`

## 🧪 Testes em Produção

### 1. Smoke Tests

\`\`\`bash
# Testar backend
curl https://seu-backend.onrender.com/health

# Testar autenticação (email + senha)
curl -X POST https://seu-backend.onrender.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"sua_senha"}'

# Testar frontend
curl -I https://seu-frontend.netlify.app
\`\`\`

### 2. Testes do Bot

\`\`\`python
# test_bot.py
import asyncio
from telegram_service import get_telegram_service

async def test_bot():
    service = get_telegram_service()
    info = await service.get_bot_info()
    print(f"Bot: {info['username']} - {info['first_name']}")
    
    connection = await service.test_connection()
    print(f"Conexão: {'OK' if connection else 'ERRO'}")

if __name__ == '__main__':
    asyncio.run(test_bot())
\`\`\`

## 📈 Otimização

### 1. Performance

- Use gunicorn com múltiplos workers
- Configure cache para arquivos estáticos
- Otimize consultas ao banco de dados
- Use CDN para assets

### 2. Scaling

\`\`\`python
# gunicorn.conf.py
bind = "0.0.0.0:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
\`\`\`

### 3. Database

Para alta carga, migre para PostgreSQL:
\`\`\`bash
# Render.com
# Adicionar PostgreSQL add-on
# Configurar DATABASE_URL
\`\`\`

## 🚨 Troubleshooting

### Problemas Comuns

1. **CORS Error:**
   - Verificar URL da API no frontend
   - Configurar CORS no backend

2. **Bot não responde:**
   - Verificar token do bot
   - Confirmar se bot é admin dos grupos

3. **Deploy falha:**
   - Verificar logs da plataforma
   - Confirmar dependências no requirements.txt

4. **Database error:**
   - Verificar se banco foi inicializado
   - Confirmar permissões de escrita

### Logs e Debug

\`\`\`bash
# Render.com
# Ver logs em tempo real no dashboard

# Railway
railway logs

# Netlify
# Ver logs no dashboard do site
\`\`\`

## 📞 Suporte

Para problemas específicos de deploy:

1. **Render:** https://render.com/docs
2. **Railway:** https://docs.railway.app
3. **Netlify:** https://docs.netlify.com
4. **Telegram Bot API:** https://core.telegram.org/bots/api

Documentação completa: README.md
