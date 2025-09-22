# 🚀 Instruções de Deploy

Este guia detalha como fazer o deploy do projeto em produção.

## 📋 Pré-requisitos

1. **Conta no GitHub** (para hospedar o código)
2. **Token do Bot do Telegram** (obtenha com @BotFather)
3. **Conta em uma das plataformas de deploy**:
   - [Render](https://render.com) (recomendado)
   - [Railway](https://railway.app)
   - [Deta](https://deta.space)

## 🔧 Configuração Inicial

### 1. Preparar o Repositório

```bash
# Clonar o repositório
git clone <seu-repositorio>
cd <seu-projeto>

# Fazer commit das mudanças
git add .
git commit -m "Reestruturação para deploy separado"
git push origin main
```

### 2. Configurar o Bot do Telegram

1. Acesse [@BotFather](https://t.me/botfather) no Telegram
2. Crie um novo bot com `/newbot`
3. Anote o token fornecido
4. Adicione o bot aos grupos desejados
5. Obtenha os Chat IDs dos grupos:
   - Envie uma mensagem no grupo
   - Acesse: `https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`
   - Encontre o `chat.id` de cada grupo

## 🌐 Deploy do Backend

### Opção 1: Render (Recomendado)

1. **Acesse [Render](https://render.com)**
2. **Conecte sua conta GitHub**
3. **Crie um novo Web Service**
4. **Configure o serviço**:
   - **Repository**: Seu repositório
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (ou pago para melhor performance)

5. **Configure as variáveis de ambiente**:
   ```
   BOT_TOKEN=seu_token_do_bot_aqui
   SECRET_KEY=uma_chave_secreta_muito_longa_e_aleatoria
   ADMIN_PASSWORD=senha_admin_segura
   DATABASE_PATH=bot_database.db
   PORT=10000
   ```

6. **Deploy**: Clique em "Create Web Service"

7. **Aguarde o deploy** (pode levar alguns minutos)

8. **Anote a URL**: `https://seu-app.onrender.com`

### Opção 2: Railway

1. **Acesse [Railway](https://railway.app)**
2. **Conecte sua conta GitHub**
3. **Crie um novo projeto**
4. **Selecione o repositório**
5. **Configure o serviço**:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`

6. **Configure as variáveis de ambiente** (mesmas do Render)

7. **Deploy automático**

8. **Anote a URL**: `https://seu-app.railway.app`

### Opção 3: Deta

1. **Instale o Deta CLI**:
   ```bash
   pip install deta
   ```

2. **Configure o Deta**:
   ```bash
   deta login
   ```

3. **Crie um novo projeto**:
   ```bash
   cd backend
   deta new
   ```

4. **Configure as variáveis de ambiente**:
   ```bash
   deta env set BOT_TOKEN=seu_token_do_bot_aqui
   deta env set SECRET_KEY=uma_chave_secreta_muito_longa_e_aleatoria
   deta env set ADMIN_PASSWORD=senha_admin_segura
   deta env set DATABASE_PATH=bot_database.db
   ```

5. **Deploy**:
   ```bash
   deta deploy
   ```

6. **Anote a URL**: `https://seu-app.deta.dev`

## 🎨 Deploy do Frontend (Netlify)

1. **Acesse [Netlify](https://netlify.com)**
2. **Conecte sua conta GitHub**
3. **Crie um novo site**
4. **Configure o build**:
   - **Repository**: Seu repositório
   - **Base directory**: `frontend`
   - **Build command**: (deixar vazio)
   - **Publish directory**: `frontend`

5. **Configure as variáveis de ambiente**:
   ```
   REACT_APP_API_URL=https://seu-backend.onrender.com/api
   ```

6. **Deploy**: Clique em "Deploy site"

7. **Aguarde o deploy** (alguns minutos)

8. **Anote a URL**: `https://seu-site.netlify.app`

## ⚙️ Configuração Final

### 1. Atualizar URL da API no Frontend

Edite o arquivo `frontend/static/js/config.js`:

```javascript
// Substitua pela URL do seu backend
API_CONFIG.BASE_URL = "https://seu-backend.onrender.com/api"
```

### 2. Fazer Deploy da Atualização

```bash
git add frontend/static/js/config.js
git commit -m "Atualizar URL da API para produção"
git push origin main
```

### 3. Testar o Sistema

1. **Acesse o frontend**: `https://seu-site.netlify.app`
2. **Faça login** com as credenciais configuradas
3. **Adicione grupos** com os Chat IDs obtidos
4. **Teste o envio** de uma mensagem

## 🔍 Verificação de Funcionamento

### Backend
- **Health Check**: `https://seu-backend.onrender.com/health`
- **API Status**: Deve retornar `{"status": "ok"}`

### Frontend
- **Login**: Deve funcionar com as credenciais configuradas
- **API Calls**: Verifique no console do navegador se não há erros de CORS
- **Envio de Mensagens**: Teste com um grupo pequeno primeiro

## 🐛 Solução de Problemas

### Erro de CORS
- Verifique se o CORS está habilitado no backend
- Confirme se a URL da API está correta

### Bot não envia mensagens
- Verifique se o token do bot está correto
- Confirme se o bot foi adicionado aos grupos
- Verifique se os Chat IDs estão corretos

### Erro 500 no backend
- Verifique os logs no painel da plataforma
- Confirme se todas as variáveis de ambiente estão configuradas

### Frontend não carrega
- Verifique se o build foi bem-sucedido
- Confirme se a URL da API está acessível

## 📊 Monitoramento

### Render
- Acesse o dashboard para ver logs e métricas
- Configure alertas para downtime

### Railway
- Use o dashboard para monitorar performance
- Configure webhooks para notificações

### Deta
- Use o CLI para ver logs: `deta logs`
- Monitore uso de recursos no dashboard

## 🔄 Atualizações

Para atualizar o sistema:

1. **Faça as mudanças** no código
2. **Commit e push** para o GitHub
3. **Aguarde o deploy automático** (1-2 minutos)
4. **Teste** as funcionalidades

## 💡 Dicas de Produção

1. **Use senhas fortes** para o admin
2. **Configure backup** do banco de dados
3. **Monitore logs** regularmente
4. **Teste** antes de enviar mensagens em massa
5. **Configure rate limiting** se necessário

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** da plataforma
2. **Teste localmente** primeiro
3. **Abra uma issue** no GitHub
4. **Consulte a documentação** da plataforma

---

**🎉 Parabéns! Seu sistema está funcionando em produção!**
