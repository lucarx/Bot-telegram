"""
Modelos de dados para o Bot Telegram
"""

import sqlite3
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

DATABASE_PATH = 'bot_database.db'

class DatabaseManager:
    """Gerenciador de conexões com o banco de dados"""
    
    @staticmethod
    def get_connection():
        """Retorna uma conexão com o banco de dados"""
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row  # Permite acesso por nome da coluna
        return conn

class Admin:
    """Modelo para administradores"""
    
    @staticmethod
    def authenticate(username: str, password: str) -> Optional[Dict]:
        """Autentica um administrador"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, username, created_at 
            FROM admins 
            WHERE username = ? AND password_hash = ?
        ''', (username, password_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'id': result['id'],
                'username': result['username'],
                'created_at': result['created_at']
            }
        return None
    
    @staticmethod
    def create(username: str, password: str) -> bool:
        """Cria um novo administrador"""
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO admins (username, password_hash) 
                VALUES (?, ?)
            ''', (username, password_hash))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Retorna todos os administradores"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, username, created_at FROM admins ORDER BY username')
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    @staticmethod
    def delete(admin_id: int) -> bool:
        """Deleta um administrador"""
        # Não permitir deletar o admin padrão (ID 1)
        if admin_id == 1:
            return False
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM admins WHERE id = ?', (admin_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def exists(username: str) -> bool:
        """Verifica se um usuário existe"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM admins WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        
        return result is not None

        
        return [dict(row) for row in results]
    
    @staticmethod
    def get_active() -> List[Dict]:
        """Retorna apenas grupos ativos"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM groups WHERE active = 1 ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    @staticmethod
    def create(chat_id: str, name: str) -> bool:
        """Cria um novo grupo"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO groups (chat_id, name) 
                VALUES (?, ?)
            ''', (chat_id, name))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    @staticmethod
    def update_status(group_id: int, active: bool) -> bool:
        """Atualiza o status de um grupo"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE groups SET active = ? WHERE id = ?
        ''', (active, group_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def get_by_ids(group_ids: List[int]) -> List[Dict]:
        """Retorna grupos pelos IDs"""
        if not group_ids:
            return []
        
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        placeholders = ','.join('?' * len(group_ids))
        cursor.execute(f'''
            SELECT * FROM groups 
            WHERE id IN ({placeholders}) AND active = 1
        ''', group_ids)
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]

class Template:
    """Modelo para templates de mensagem"""
    
    @staticmethod
    def get_all() -> List[Dict]:
        """Retorna todos os templates"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM templates ORDER BY name')
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    @staticmethod
    def create(name: str, content: str) -> bool:
        """Cria um novo template"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO templates (name, content) 
            VALUES (?, ?)
        ''', (name, content))
        
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def update(template_id: int, name: str, content: str) -> bool:
        """Atualiza um template"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE templates SET name = ?, content = ? 
            WHERE id = ?
        ''', (name, content, template_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def delete(template_id: int) -> bool:
        """Deleta um template"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM templates WHERE id = ?', (template_id,))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    @staticmethod
    def get_by_id(template_id: int) -> Optional[Dict]:
        """Retorna um template pelo ID"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM templates WHERE id = ?', (template_id,))
        result = cursor.fetchone()
        conn.close()
        
        return dict(result) if result else None

class MessageHistory:
    """Modelo para histórico de mensagens"""
    
    @staticmethod
    def create(message_text: str, groups_sent: str, status: str = 'sent') -> bool:
        """Cria um registro no histórico"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO message_history (message_text, groups_sent, status) 
            VALUES (?, ?, ?)
        ''', (message_text, groups_sent, status))
        
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_recent(limit: int = 50) -> List[Dict]:
        """Retorna o histórico recente"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM message_history 
            ORDER BY sent_at DESC 
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in results]
    
    @staticmethod
    def get_stats() -> Dict:
        """Retorna estatísticas do histórico"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        # Total de mensagens enviadas
        cursor.execute('SELECT COUNT(*) FROM message_history WHERE status = "sent"')
        total_messages = cursor.fetchone()[0]
        
        # Mensagens enviadas hoje
        cursor.execute('''
            SELECT COUNT(*) FROM message_history 
            WHERE DATE(sent_at) = DATE('now') AND status = 'sent'
        ''')
        messages_today = cursor.fetchone()[0]
        
        # Mensagens desta semana
        cursor.execute('''
            SELECT COUNT(*) FROM message_history 
            WHERE DATE(sent_at) >= DATE('now', '-7 days') AND status = 'sent'
        ''')
        messages_week = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_messages': total_messages,
            'messages_today': messages_today,
            'messages_week': messages_week
        }

class Settings:
    """Modelo para configurações do sistema"""
    
    @staticmethod
    def get(key: str, default_value: str = None) -> Optional[str]:
        """Retorna uma configuração"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        
        return result['value'] if result else default_value
    
    @staticmethod
    def set(key: str, value: str) -> bool:
        """Define uma configuração"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO settings (key, value, updated_at) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (key, value))
        
        conn.commit()
        conn.close()
        return True
    
    @staticmethod
    def get_all() -> Dict[str, str]:
        """Retorna todas as configurações"""
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT key, value FROM settings')
        results = cursor.fetchall()
        conn.close()
        
        return {row['key']: row['value'] for row in results}
