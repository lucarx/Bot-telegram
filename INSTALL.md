# 📦 Guia de Instalação Completo

Este guia detalha como instalar e configurar o sistema completo do Bot Telegram + Painel Web.

## 📋 Pré-requisitos

### Sistema
- Python 3.8+ 
- Git
- Navegador web moderno
- Conta no Telegram

### Serviços (para produção)
- Conta no Render.com, Railway.app ou Deta.sh (backend)
- Conta no Netlify.com (frontend)

## 🤖 1. Configuração do Bot no Telegram

### Criar o Bot

1. **Abra o Telegram** e procure por `@BotFather`
2. **Inicie uma conversa** e digite `/start`
3. **Crie um novo bot** com `/newbot`
4. **Escolha um nome** para seu bot (ex: "Meu Bot Admin")
5. **Escolha um username** (deve terminar com "bot", ex: "meubot_admin_bot")
6. **Anote o token** fornecido (formato: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Configurar o Bot

\`\`\`
/setdescription - Definir descrição do bot
/setabouttext - Definir texto "sobre"
/setuserpic - Definir foto do perfil
/setcommands - Definir comandos disponíveis
\`\`\`

Comandos sugeridos:
\`\`\`
start - Iniciar o bot
help - Ajuda
info - Informações do bot
\`\`\`

## 💻 2. Instalação Local (Desenvolvimento)

### Backend

\`\`\`bash
# 1. Clonar o repositório
git clone <seu-repositorio>
cd telegram-bot-admin

# 2. Criar ambiente virtual Python
python -m venv venv

# 3. Ativar ambiente virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependências
cd backend
pip install -r requirements.txt

# 5. Configurar variáveis de ambiente
cp .env.example .env
\`\`\`

### Editar arquivo .env

\`\`\`env
# Token do bot (obrigatório)
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Senha do admin (altere para uma senha segura)
ADMIN_PASSWORD=minha_senha_super_segura

# Chave secreta para JWT (gere uma chave aleatória)
SECRET_KEY=minha_chave_jwt_super_secreta_123

# Porta do servidor (opcional)
PORT=5000
\`\`\`

### Inicializar o banco de dados

\`\`\`bash
# Executar script de inicialização
python init_db.py
\`\`\`

Saída esperada:
\`\`\`
Inicializando banco de dados do Bot Telegram...
Criando tabelas...
Tabelas criadas com sucesso!
Usuário admin criado com senha: minha_senha_super_segura
Template 'Bom dia' adicionado
Template 'Promoção' adicionado
Template 'Lembrete' adicionado
...
✅ Banco de dados inicializado com sucesso!
\`\`\`

### Executar o backend

\`\`\`bash
# Método 1: Desenvolvimento
python run.py

# Método 2: Produção local
gunicorn -w 4 -b 0.0.0.0:5000 app:app
\`\`\`

### Frontend

\`\`\`bash
# 1. Navegar para a pasta frontend
cd ../frontend

# 2. Configurar URL da API
# Editar static/js/config.js
# Manter BASE_URL: 'http://localhost:5000/api' para desenvolvimento local

# 3. Servir arquivos estáticos
# Opção 1: Python
python -m http.server 8000

# Opção 2: Node.js (se instalado)
npx serve .

# Opção 3: Abrir diretamente no navegador
# Abrir index.html no navegador
\`\`\`

### Testar a instalação

1. **Backend:** Acesse http://localhost:5000/health
   - Deve retornar: `{"status": "ok", "timestamp": "..."}`

2. **Frontend:** Acesse http://localhost:8000
   - Deve mostrar a tela de login

3. **Login:** Use as credenciais:
   - Usuário: `admin`
   - Senha: (a que você definiu no .env)

## 🌐 3. Deploy em Produção

### Backend - Render.com

1. **Criar conta** em https://render.com
2. **Conectar repositório** do GitHub
3. **Criar Web Service:**
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `cd backend && python run.py`
   - Environment: Python 3

4. **Configurar variáveis de ambiente:**
   \`\`\`
   BOT_TOKEN=seu_token_aqui
   ADMIN_PASSWORD=senha_segura
   SECRET_KEY=chave_jwt_secreta
   PORT=10000
   \`\`\`

5. **Deploy automático** será executado

### Backend - Railway.app

\`\`\`bash
# 1. Instalar Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Inicializar projeto
railway init

# 4. Configurar variáveis
railway variables set BOT_TOKEN=seu_token
railway variables set ADMIN_PASSWORD=senha_segura
railway variables set SECRET_KEY=chave_secreta

# 5. Deploy
railway up
\`\`\`

### Frontend - Netlify

1. **Preparar frontend para produção:**
   \`\`\`bash
   cd frontend
   # Editar static/js/config.js
   # Alterar BASE_URL para a URL do seu backend
   \`\`\`

   \`\`\`javascript
   const API_CONFIG = {
       BASE_URL: 'https://seu-app.onrender.com/api'
   };
   \`\`\`

2. **Deploy no Netlify:**
   - Método 1: Arrastar pasta `frontend` para https://app.netlify.com
   - Método 2: Conectar repositório GitHub

3. **Configurar domínio personalizado** (opcional)

## 🔧 4. Configuração dos Grupos

### Adicionar Bot aos Grupos

1. **Abra o grupo** no Telegram
2. **Adicione o bot** usando o username (@seubot_admin_bot)
3. **Torne o bot administrador:**
   - Toque no nome do grupo
   - "Administradores" → "Adicionar administrador"
   - Selecione seu bot
   - Marque "Deletar mensagens" e "Banir usuários"

### Obter Chat ID do Grupo

**Método 1: Bot auxiliar**
1. Adicione `@userinfobot` ao grupo
2. Digite `/id`
3. Anote o Chat ID (ex: `-1001234567890`)

**Método 2: API do Telegram**
1. Envie uma mensagem no grupo
2. Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
3. Procure pelo `chat.id` na resposta

### Cadastrar no Painel

1. **Acesse o painel web**
2. **Vá em "Grupos"** → "Adicionar Grupo"
3. **Preencha:**
   - Chat ID: `-1001234567890`
   - Nome: "Meu Grupo de Teste"
4. **Salvar**

## ✅ 5. Verificação da Instalação

### Checklist Backend
- [ ] Servidor rodando sem erros
- [ ] `/health` retorna status OK
- [ ] Banco de dados criado com tabelas
- [ ] Variáveis de ambiente configuradas
- [ ] Bot conecta com Telegram

### Checklist Frontend
- [ ] Página carrega sem erros
- [ ] Login funciona
- [ ] Dashboard mostra estatísticas
- [ ] Formulários respondem
- [ ] API se comunica com backend

### Checklist Bot
- [ ] Bot responde no Telegram
- [ ] Bot é admin dos grupos
- [ ] Chat IDs corretos no painel
- [ ] Mensagens são enviadas com sucesso

## 🐛 6. Solução de Problemas

### Erro: "Bot não configurado"
\`\`\`bash
# Verificar se o token está correto
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Token:', os.getenv('BOT_TOKEN'))
"
\`\`\`

### Erro: "CORS policy"
- Verificar se a URL da API está correta em `config.js`
- Confirmar que o backend está rodando

### Erro: "Token inválido"
- Verificar se o JWT não expirou (24h)
- Fazer logout e login novamente

### Erro: "Chat not found"
- Verificar se o Chat ID está correto
- Confirmar se o bot está no grupo
- Verificar se o bot é administrador

### Logs do Backend
\`\`\`bash
# Ver logs em tempo real
tail -f app.log

# Ou executar com debug
python run.py --debug
\`\`\`

## 📞 7. Suporte

Se encontrar problemas:

1. **Verifique os logs** do backend
2. **Teste a conexão** com `/health`
3. **Confirme as configurações** do bot
4. **Verifique as variáveis** de ambiente

Para mais ajuda, consulte a documentação completa no README.md.
