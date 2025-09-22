"""
Script para inicializar o banco de dados SQLite
"""

import sqlite3
import hashlib
import os
from datetime import datetime

DATABASE_PATH = 'bot_database.db'

def create_tables():
    """Cria todas as tabelas necessárias"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("Criando tabelas...")
    
    # Tabela de admins
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de grupos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de templates
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Tabela de histórico
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS message_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_text TEXT NOT NULL,
            groups_sent TEXT NOT NULL,
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'sent'
        )
    ''')
    
    # Tabela de configurações
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    print("Tabelas criadas com sucesso!")
    
    return conn, cursor

def create_admin_user():
    """Cria usuário admin padrão"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')
    password_hash = hashlib.sha256(admin_password.encode()).hexdigest()
    
    try:
        cursor.execute('''
            INSERT INTO admins (username, password_hash) 
            VALUES (?, ?)
        ''', ('admin', password_hash))
        conn.commit()
        print(f"Usuário admin criado com senha: {admin_password}")
    except sqlite3.IntegrityError:
        print("Usuário admin já existe")
    
    conn.close()

def show_users():
    """Mostra todos os usuários"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, created_at FROM admins ORDER BY username')
    users = cursor.fetchall()
    
    print("\n👥 Usuários administradores:")
    for user in users:
        print(f"  - ID: {user[0]}, Usuário: {user[1]}, Criado em: {user[2]}")
    
    conn.close()

def show_database_info():
    """Mostra informações sobre o banco de dados"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("INFORMAÇÕES DO BANCO DE DADOS")
    print("="*50)
    
    # Contar registros em cada tabela
    tables = ['admins', 'groups', 'templates', 'message_history', 'settings']
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"{table.capitalize()}: {count} registros")
    
    # Mostrar usuários
    show_users()
    
    # Mostrar templates
    cursor.execute('SELECT name FROM templates')
    templates = cursor.fetchall()
    if templates:
        print(f"\nTemplates disponíveis:")
        for (name,) in templates:
            print(f"  - {name}")
    
    conn.close()
    print("="*50)



def add_sample_data():
    """Adiciona dados de exemplo"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Templates de exemplo
    sample_templates = [
        ("Bom dia", "🌅 Bom dia! Tenha um excelente dia!"),
        ("Promoção", "🔥 PROMOÇÃO ESPECIAL! \n\nNão perca esta oportunidade única!\n\n💰 Desconto de 50%\n⏰ Válido até amanhã"),
        ("Lembrete", "📅 LEMBRETE IMPORTANTE\n\nNão se esqueça do nosso evento hoje às 19h!\n\n📍 Local: Centro de Convenções\n🎫 Entrada gratuita")
    ]
    
    for name, content in sample_templates:
        try:
            cursor.execute('INSERT INTO templates (name, content) VALUES (?, ?)', (name, content))
            print(f"Template '{name}' adicionado")
        except sqlite3.IntegrityError:
            print(f"Template '{name}' já existe")
    
    # Configurações padrão
    default_settings = [
        ("bot_status", "active"),
        ("max_groups_per_message", "10"),
        ("message_delay", "1")
    ]
    
    for key, value in default_settings:
        try:
            cursor.execute('INSERT INTO settings (key, value) VALUES (?, ?)', (key, value))
            print(f"Configuração '{key}' adicionada")
        except sqlite3.IntegrityError:
            print(f"Configuração '{key}' já existe")
    
    conn.commit()
    conn.close()

def show_database_info():
    """Mostra informações sobre o banco de dados"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    print("\n" + "="*50)
    print("INFORMAÇÕES DO BANCO DE DADOS")
    print("="*50)
    
    # Contar registros em cada tabela
    tables = ['admins', 'groups', 'templates', 'message_history', 'settings']
    
    for table in tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"{table.capitalize()}: {count} registros")
    
    # Mostrar admins
    cursor.execute('SELECT username, created_at FROM admins')
    admins = cursor.fetchall()
    print(f"\nUsuários admin:")
    for username, created_at in admins:
        print(f"  - {username} (criado em: {created_at})")
    
    # Mostrar templates
    cursor.execute('SELECT name FROM templates')
    templates = cursor.fetchall()
    if templates:
        print(f"\nTemplates disponíveis:")
        for (name,) in templates:
            print(f"  - {name}")
    
    conn.close()
    print("="*50)

def main():
    """Função principal"""
    print("Inicializando banco de dados do Bot Telegram...")
    print(f"Arquivo do banco: {DATABASE_PATH}")
    
    # Verificar se o banco já existe
    db_exists = os.path.exists(DATABASE_PATH)
    if db_exists:
        print("Banco de dados já existe. Atualizando estrutura...")
    else:
        print("Criando novo banco de dados...")
    
    # Criar tabelas
    conn, cursor = create_tables()
    conn.close()
    
    # Criar usuário admin
    create_admin_user()
    
    # Adicionar dados de exemplo
    add_sample_data()
    
    # Mostrar informações
    show_database_info()
    
    print("\n✅ Banco de dados inicializado com sucesso!")
    print("\n📝 Próximos passos:")
    print("1. Configure o token do bot no arquivo .env")
    print("2. Execute: python run.py")
    print("3. Acesse o painel em: http://localhost:5000")

if __name__ == '__main__':
    main()
