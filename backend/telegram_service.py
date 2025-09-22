"""
Serviço para integração com o Telegram Bot
"""

import asyncio
import logging
from typing import List, Dict, Optional
from telegram import Bot
from telegram.error import TelegramError
import os

logger = logging.getLogger(__name__)

class TelegramService:
    """Serviço para gerenciar o bot do Telegram"""
    
    def __init__(self, token: str):
        self.token = token
        self.bot = Bot(token=token) if token else None
        
    async def send_message_to_group(self, chat_id: str, message: str) -> bool:
        """Envia mensagem para um grupo específico"""
        if not self.bot:
            raise Exception("Bot não configurado - token não fornecido")
        
        try:
            await self.bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Mensagem enviada para {chat_id}")
            return True
        except TelegramError as e:
            logger.error(f"Erro ao enviar mensagem para {chat_id}: {e}")
            return False
    
    async def send_message_to_groups(self, groups: List[Dict], message: str) -> Dict:
        """Envia mensagem para múltiplos grupos"""
        if not self.bot:
            raise Exception("Bot não configurado - token não fornecido")
        
        sent_groups = []
        failed_groups = []
        
        for group in groups:
            chat_id = group['chat_id']
            group_name = group['name']
            
            try:
                await self.bot.send_message(chat_id=chat_id, text=message)
                sent_groups.append(group_name)
                logger.info(f"Mensagem enviada para {group_name} ({chat_id})")
                
                # Delay entre mensagens para evitar rate limiting
                await asyncio.sleep(1)
                
            except TelegramError as e:
                failed_groups.append(f"{group_name}: {str(e)}")
                logger.error(f"Erro ao enviar para {group_name} ({chat_id}): {e}")
        
        return {
            'sent_groups': sent_groups,
            'failed_groups': failed_groups,
            'total_sent': len(sent_groups),
            'total_failed': len(failed_groups)
        }
    
    async def get_bot_info(self) -> Optional[Dict]:
        """Retorna informações sobre o bot"""
        if not self.bot:
            return None
        
        try:
            bot_info = await self.bot.get_me()
            return {
                'id': bot_info.id,
                'username': bot_info.username,
                'first_name': bot_info.first_name,
                'can_join_groups': bot_info.can_join_groups,
                'can_read_all_group_messages': bot_info.can_read_all_group_messages
            }
        except TelegramError as e:
            logger.error(f"Erro ao obter informações do bot: {e}")
            return None
    
    async def test_connection(self) -> bool:
        """Testa a conexão com o bot"""
        try:
            await self.bot.get_me()
            return True
        except Exception as e:
            logger.error(f"Erro na conexão com o bot: {e}")
            return False

# Instância global do serviço
telegram_service = None

def get_telegram_service() -> TelegramService:
    """Retorna a instância do serviço do Telegram"""
    global telegram_service
    
    if telegram_service is None:
        token = os.getenv('BOT_TOKEN')
        telegram_service = TelegramService(token)
    
    return telegram_service

def send_message_sync(groups: List[Dict], message: str) -> Dict:
    """Versão síncrona para envio de mensagens"""
    service = get_telegram_service()
    
    # Executar de forma síncrona
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        result = loop.run_until_complete(
            service.send_message_to_groups(groups, message)
        )
        return result
    finally:
        loop.close()
