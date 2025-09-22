#!/usr/bin/env python3
"""
Script para criar usuários administradores via linha de comando
"""

import sys
import hashlib
import sqlite3
import getpass

DATABASE_PATH = 'bot_database.db'

def create_user(username, password):
    """Cria um novo usuário administrador"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', 
                      (username, password_hash))
        conn.commit()
        print(f"✅ Usuário '{username}' criado com sucesso!")
        return True
    except sqlite3.IntegrityError:
        print(f"❌ Erro: Usuário '{username}' já existe")
        return False
    finally:
        conn.close()

def list_users():
    """Lista todos os usuários administradores"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, username, created_at FROM admins ORDER BY username')
    users = cursor.fetchall()
    conn.close()
    
    if not users:
        print("📝 Nenhum usuário encontrado")
        return
    
    print("\n📋 Lista de usuários administradores:")
    print("-" * 50)
    for user in users:
        print(f"ID: {user[0]} | Usuário: {user[1]} | Criado em: {user[2]}")

def main():
    """Função principal"""
    if len(sys.argv) == 1:
        print("Uso: python create_user.py [comando]")
        print("\nComandos disponíveis:")
        print("  create    - Criar novo usuário")
        print("  list      - Listar usuários existentes")
        return
    
    command = sys.argv[1]
    
    if command == "create":
        if len(sys.argv) > 2:
            username = sys.argv[2]
        else:
            username = input("Digite o nome de usuário: ")
        
        password = getpass.getpass("Digite a senha: ")
        confirm_password = getpass.getpass("Confirme a senha: ")
        
        if password != confirm_password:
            print("❌ Erro: As senhas não coincidem")
            return
        
        if len(password) < 6:
            print("❌ Erro: A senha deve ter pelo menos 6 caracteres")
            return
        
        create_user(username, password)
        
    elif command == "list":
        list_users()
    
    else:
        print(f"❌ Comando desconhecido: {command}")
        print("Use 'create' ou 'list'")

if __name__ == '__main__':
    main()