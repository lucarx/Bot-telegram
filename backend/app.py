from flask import Flask, request, jsonify, g
from flask_cors import CORS
import sqlite3
import hashlib
import bcrypt
import jwt
import datetime
import os
import asyncio
import threading
from telegram import Bot
from telegram.error import TelegramError
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Permitir requisições do frontend

# Configurações
SECRET_KEY = os.getenv('SECRET_KEY', 'sua-chave-secreta-aqui')
BOT_TOKEN = os.getenv('BOT_TOKEN', '')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
username = os.getenv('username', 'admin')
DATABASE_PATH = os.getenv('DATABASE_PATH', 'bot_database.db')

app.config['SECRET_KEY'] = SECRET_KEY

# Inicializar bot do Telegram
bot = None
if BOT_TOKEN:
    bot = Bot(token=BOT_TOKEN)

def init_database():
    """Inicializa o banco de dados SQLite"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Tabela de usuários (multi-tenant)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de grupos (associado ao usuário)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de templates (associado ao usuário)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de histórico (associado ao usuário)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_text TEXT NOT NULL,
            groups_sent TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'sent'
        )
    ''')
    
    # Criar admin padrão se não existir (email: admin@example.com)
    cursor.execute('SELECT id FROM users WHERE email = ?', ('admin@example.com',))
    if cursor.fetchone() is None:
        password_hash = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
        cursor.execute('''
            INSERT INTO users (name, email, password_hash, is_admin) 
            VALUES (?, ?, ?, 1)
        ''', ('Admin', 'admin@example.com', password_hash))

    # Obter id do admin para migração de dados antigos
    cursor.execute('SELECT id FROM users WHERE email = ?', ('admin@example.com',))
    admin_row = cursor.fetchone()
    admin_id = admin_row[0] if admin_row else 1

    # Migração: adicionar colunas user_id se estiverem faltando e preencher com admin_id
    def ensure_column(table: str, column: str, add_sql: str):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cursor.fetchall()]
        if column not in cols:
            cursor.execute(add_sql)

    ensure_column('groups', 'user_id', 'ALTER TABLE groups ADD COLUMN user_id INTEGER')
    ensure_column('templates', 'user_id', 'ALTER TABLE templates ADD COLUMN user_id INTEGER')
    ensure_column('message_history', 'user_id', 'ALTER TABLE message_history ADD COLUMN user_id INTEGER')

    # Backfill user_id nulos com admin_id
    cursor.execute('UPDATE groups SET user_id = COALESCE(user_id, ?) WHERE user_id IS NULL', (admin_id,))
    cursor.execute('UPDATE templates SET user_id = COALESCE(user_id, ?) WHERE user_id IS NULL', (admin_id,))
    cursor.execute('UPDATE message_history SET user_id = COALESCE(user_id, ?) WHERE user_id IS NULL', (admin_id,))

    # Índices para escalabilidade
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_groups_user_id ON groups(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_templates_user_id ON templates(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user_id ON message_history(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user_date ON message_history(user_id, sent_at)')
    
    conn.commit()
    conn.close()

def generate_token(user):
    """Gera token JWT para autenticação"""
    payload = {
        'sub': user['id'],
        'email': user['email'],
        'name': user.get('name'),
        'is_admin': bool(user.get('is_admin', 0)),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def verify_token(token):
    """Verifica token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_auth(f):
    """Decorator para rotas que requerem autenticação"""
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token não fornecido'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Token inválido'}), 401
        g.user_id = payload.get('sub')
        g.is_admin = bool(payload.get('is_admin', False))
        g.user_email = payload.get('email')
        
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

def require_admin(f):
    """Decorator para rotas exclusivas do admin"""
    @require_auth
    def decorated(*args, **kwargs):
        if not getattr(g, 'is_admin', False):
            return jsonify({'error': 'Acesso restrito ao admin'}), 403
        return f(*args, **kwargs)
    decorated.__name__ = f.__name__
    return decorated

# Rotas da API
@app.route('/api/register', methods=['POST'])
@require_admin
def register_user():
    """Admin registra um novo cliente"""
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    if len(password) < 6:
        return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400
    
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO users (name, email, password_hash, is_admin) VALUES (?, ?, ?, 0)', 
                      (name, email, password_hash))
        conn.commit()
        return jsonify({'message': 'Cliente criado com sucesso'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email já cadastrado'}), 400
    finally:
        conn.close()

@app.route('/api/users', methods=['GET'])
@require_admin
def list_users():
    """Admin lista todos os usuários"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, is_admin, created_at FROM users ORDER BY created_at DESC')
    users = cursor.fetchall()
    conn.close()
    users_list = [
        {
            'id': row[0],
            'name': row[1],
            'email': row[2],
            'is_admin': bool(row[3]),
            'created_at': row[4]
        } for row in users
    ]
    return jsonify(users_list)

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_user(user_id):
    """Admin deleta um cliente (não pode deletar a si mesmo)"""
    if user_id == getattr(g, 'user_id', None):
        return jsonify({'error': 'Admin não pode deletar a si mesmo'}), 400
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE id = ? AND is_admin = 0', (user_id,))
    conn.commit()
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Usuário não encontrado ou é admin'}), 404
    conn.close()
    return jsonify({'message': 'Usuário deletado com sucesso'})


@app.route('/api/login', methods=['POST'])
def login():
    """Autenticação de usuário multi-tenant"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'Email e senha são obrigatórios'}), 400
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, password_hash, is_admin FROM users WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Credenciais inválidas'}), 401
    stored_hash = row[3]
    if not bcrypt.checkpw(password.encode(), stored_hash.encode() if isinstance(stored_hash, str) else stored_hash):
        return jsonify({'error': 'Credenciais inválidas'}), 401
    user = {
        'id': row[0],
        'name': row[1],
        'email': row[2],
        'is_admin': row[4]
    }
    token = generate_token(user)
    return jsonify({'token': token, 'user': {'id': user['id'], 'name': user['name'], 'email': user['email'], 'is_admin': bool(user['is_admin'])}})

@app.route('/api/me', methods=['GET'])
@require_auth
def get_me():
    """Dados do usuário logado"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, email, is_admin, created_at FROM users WHERE id = ?', (g.user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    return jsonify({'id': row[0], 'name': row[1], 'email': row[2], 'is_admin': bool(row[3]), 'created_at': row[4]})

@app.route('/api/me', methods=['PUT'])
@require_auth
def update_me():
    """Atualiza perfil do próprio usuário (nome e senha)"""
    data = request.get_json()
    name = data.get('name')
    password = data.get('password')
    updates = []
    params = []
    if name:
        updates.append('name = ?')
        params.append(name)
    if password:
        if len(password) < 6:
            return jsonify({'error': 'A senha deve ter pelo menos 6 caracteres'}), 400
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        updates.append('password_hash = ?')
        params.append(password_hash)
    if not updates:
        return jsonify({'error': 'Nada para atualizar'}), 400
    params.append(g.user_id)
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute(f'UPDATE users SET {", ".join(updates)} WHERE id = ?', tuple(params))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Perfil atualizado com sucesso'})

@app.route('/api/groups', methods=['GET'])
@require_auth
def get_groups():
    """Lista grupos do usuário"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, chat_id, name, active, created_at FROM groups WHERE user_id = ? ORDER BY name', (g.user_id,))
    groups = cursor.fetchall()
    conn.close()
    
    groups_list = []
    for row in groups:
        groups_list.append({
            'id': row[0],
            'chat_id': row[1],
            'name': row[2],
            'active': bool(row[3]),
            'created_at': row[4]
        })
    
    return jsonify(groups_list)

@app.route('/api/groups', methods=['POST'])
@require_auth
def add_group():
    """Adiciona um novo grupo para o usuário"""
    data = request.get_json()
    chat_id = data.get('chat_id')
    name = data.get('name')
    
    if not chat_id or not name:
        return jsonify({'error': 'Chat ID e nome são obrigatórios'}), 400
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('INSERT INTO groups (chat_id, name, user_id) VALUES (?, ?, ?)', (chat_id, name, g.user_id))
        conn.commit()
        return jsonify({'message': 'Grupo adicionado com sucesso'})
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Grupo já existe'}), 400
    finally:
        conn.close()

@app.route('/api/templates', methods=['GET'])
@require_auth
def get_templates():
    """Lista templates do usuário"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name, content, created_at FROM templates WHERE user_id = ? ORDER BY name', (g.user_id,))
    templates = cursor.fetchall()
    conn.close()
    
    templates_list = []
    for row in templates:
        templates_list.append({
            'id': row[0],
            'name': row[1],
            'content': row[2],
            'created_at': row[3]
        })
    
    return jsonify(templates_list)

@app.route('/api/templates', methods=['POST'])
@require_auth
def create_template():
    """Cria um novo template do usuário"""
    data = request.get_json()
    name = data.get('name')
    content = data.get('content')
    
    if not name or not content:
        return jsonify({'error': 'Nome e conteúdo são obrigatórios'}), 400
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO templates (name, content, user_id) VALUES (?, ?, ?)', (name, content, g.user_id))
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Template criado com sucesso'})

@app.route('/api/templates/<int:template_id>', methods=['DELETE'])
@require_auth
def delete_template(template_id):
    """Deleta um template do usuário"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM templates WHERE id = ? AND user_id = ?', (template_id, g.user_id))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    if deleted == 0:
        return jsonify({'error': 'Template não encontrado'}), 404
    return jsonify({'message': 'Template deletado com sucesso'})

@app.route('/api/send_message', methods=['POST'])
@require_auth
def send_message():
    """Envia mensagem para grupos selecionados"""
    data = request.get_json()
    message_text = data.get('message')
    selected_groups = data.get('groups', [])
    
    if not message_text:
        return jsonify({'error': 'Mensagem é obrigatória'}), 400
    
    if not selected_groups:
        return jsonify({'error': 'Selecione pelo menos um grupo'}), 400
    
    if not bot:
        return jsonify({'error': 'Bot não configurado'}), 500
    
    # Enviar mensagens
    sent_groups = []
    failed_groups = []
    
    for group_id in selected_groups:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT chat_id, name FROM groups WHERE id = ? AND user_id = ?', (group_id, g.user_id))
        group = cursor.fetchone()
        conn.close()
        
        if group:
            chat_id, group_name = group
            try:
                # Executar envio de forma síncrona
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(bot.send_message(chat_id=chat_id, text=message_text))
                loop.close()
                
                sent_groups.append(group_name)
                logger.info(f"Mensagem enviada para {group_name}")
            except Exception as e:
                failed_groups.append(f"{group_name}: {str(e)}")
                logger.error(f"Erro ao enviar para {group_name}: {e}")
    
    # Salvar no histórico
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO message_history (message_text, groups_sent, status, user_id) 
        VALUES (?, ?, ?, ?)
    ''', (message_text, ', '.join(sent_groups), 'sent' if sent_groups else 'failed', g.user_id))
    conn.commit()
    conn.close()
    
    result = {
        'sent_groups': sent_groups,
        'failed_groups': failed_groups,
        'total_sent': len(sent_groups),
        'total_failed': len(failed_groups)
    }
    
    return jsonify(result)

@app.route('/api/history', methods=['GET'])
@require_auth
def get_history():
    """Lista histórico de mensagens do usuário"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, message_text, groups_sent, sent_at, status FROM message_history WHERE user_id = ? ORDER BY sent_at DESC LIMIT 50', (g.user_id,))
    history = cursor.fetchall()
    conn.close()
    
    history_list = []
    for row in history:
        history_list.append({
            'id': row[0],
            'message_text': row[1],
            'groups_sent': row[2],
            'sent_at': row[3],
            'status': row[4]
        })
    
    return jsonify(history_list)

@app.route('/api/stats', methods=['GET'])
@require_auth
def get_stats():
    """Retorna estatísticas do usuário"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM groups WHERE active = 1 AND user_id = ?', (g.user_id,))
    active_groups = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM templates WHERE user_id = ?', (g.user_id,))
    total_templates = cursor.fetchone()[0]
    cursor.execute('''
        SELECT COUNT(*) FROM message_history 
        WHERE DATE(sent_at) = DATE('now') AND status = 'sent' AND user_id = ?
    ''', (g.user_id,))
    messages_today = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM message_history WHERE status = "sent" AND user_id = ?', (g.user_id,))
    total_messages = cursor.fetchone()[0]
    
    conn.close()
    
    return jsonify({
        'active_groups': active_groups,
        'total_templates': total_templates,
        'messages_today': messages_today,
        'total_messages': total_messages
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check para monitoramento"""
    return jsonify({'status': 'ok', 'timestamp': datetime.datetime.utcnow().isoformat()})

if __name__ == '__main__':
    init_database()
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
