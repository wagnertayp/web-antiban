#!/usr/bin/env python3
"""
Webhook Handler para capturar interações do WhatsApp Business API
Detecta cliques em botões, respostas de usuários, status de entrega, etc.
"""
import logging
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os

class WhatsAppWebhookHandler:
    """Handler para processar webhooks do WhatsApp Business API"""
    
    def __init__(self, db=None):
        self.db = db
        self.verify_token = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN', 'webhook_verify_token_12345')
        
    def verify_webhook(self, mode: str, token: str, challenge: str) -> Optional[str]:
        """Verificar webhook do WhatsApp (processo de configuração inicial)"""
        if mode == 'subscribe' and token == self.verify_token:
            logging.info("Webhook verificado com sucesso")
            return challenge
        else:
            logging.error(f"Falha na verificação do webhook: mode={mode}, token={token}")
            return None
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """Processar webhook recebido do WhatsApp"""
        try:
            # Estrutura típica do webhook WhatsApp Business API
            entry_list = webhook_data.get('entry', [])
            
            results = []
            
            for entry in entry_list:
                changes = entry.get('changes', [])
                
                for change in changes:
                    field = change.get('field')
                    value = change.get('value', {})
                    
                    if field == 'messages':
                        # Processar mensagens recebidas e interações
                        result = self._process_messages(value)
                        if result:
                            results.append(result)
                    
                    elif field == 'message_template_status_update':
                        # Processar atualizações de status de template
                        result = self._process_template_status(value)
                        if result:
                            results.append(result)
            
            return {
                'success': True,
                'processed_events': len(results),
                'results': results
            }
            
        except Exception as e:
            logging.error(f"Erro ao processar webhook: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _process_messages(self, messages_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processar mensagens e interações recebidas"""
        try:
            # Extrair dados básicos
            messaging_product = messages_data.get('messaging_product', 'whatsapp')
            metadata = messages_data.get('metadata', {})
            phone_number_id = metadata.get('phone_number_id')
            
            # Processar mensagens recebidas
            messages = messages_data.get('messages', [])
            statuses = messages_data.get('statuses', [])
            
            results = []
            
            # Processar mensagens (respostas dos usuários)
            for message in messages:
                message_result = self._process_single_message(message, phone_number_id)
                if message_result:
                    results.append(message_result)
            
            # Processar status de mensagens enviadas
            for status in statuses:
                status_result = self._process_message_status(status, phone_number_id)
                if status_result:
                    results.append(status_result)
            
            return {
                'type': 'messages',
                'phone_number_id': phone_number_id,
                'results': results
            }
            
        except Exception as e:
            logging.error(f"Erro ao processar mensagens: {str(e)}")
            return None
    
    def _process_single_message(self, message: Dict[str, Any], phone_number_id: str) -> Optional[Dict[str, Any]]:
        """Processar uma mensagem individual recebida"""
        try:
            message_id = message.get('id')
            from_number = message.get('from')
            timestamp = message.get('timestamp')
            message_type = message.get('type')
            
            result = {
                'event_type': 'message_received',
                'message_id': message_id,
                'from': from_number,
                'timestamp': timestamp,
                'type': message_type,
                'phone_number_id': phone_number_id
            }
            
            # Processar diferentes tipos de mensagem
            if message_type == 'text':
                text_data = message.get('text', {})
                result['content'] = text_data.get('body', '')
                
            elif message_type == 'interactive':
                # CLIQUE EM BOTÃO INTERATIVO!
                interactive_data = message.get('interactive', {})
                interactive_type = interactive_data.get('type')
                
                if interactive_type == 'button_reply':
                    # Usuário clicou em um botão
                    button_reply = interactive_data.get('button_reply', {})
                    result['button_clicked'] = {
                        'button_id': button_reply.get('id'),
                        'button_title': button_reply.get('title')
                    }
                    logging.info(f"BOTÃO CLICADO: {button_reply.get('title')} por {from_number}")
                
                elif interactive_type == 'list_reply':
                    # Usuário selecionou item de lista
                    list_reply = interactive_data.get('list_reply', {})
                    result['list_selected'] = {
                        'list_id': list_reply.get('id'),
                        'list_title': list_reply.get('title'),
                        'list_description': list_reply.get('description')
                    }
                    logging.info(f"LISTA SELECIONADA: {list_reply.get('title')} por {from_number}")
            
            # Salvar no banco de dados se disponível
            if self.db:
                self._save_interaction_to_db(result)
            
            return result
            
        except Exception as e:
            logging.error(f"Erro ao processar mensagem individual: {str(e)}")
            return None
    
    def _process_message_status(self, status: Dict[str, Any], phone_number_id: str) -> Optional[Dict[str, Any]]:
        """Processar status de mensagem enviada (entregue, lida, etc.)"""
        try:
            message_id = status.get('id')
            recipient_id = status.get('recipient_id')
            status_type = status.get('status')  # sent, delivered, read, failed
            timestamp = status.get('timestamp')
            
            result = {
                'event_type': 'message_status',
                'message_id': message_id,
                'recipient_id': recipient_id,
                'status': status_type,
                'timestamp': timestamp,
                'phone_number_id': phone_number_id
            }
            
            # Informações adicionais para status de erro
            if status_type == 'failed':
                errors = status.get('errors', [])
                if errors:
                    result['error'] = {
                        'code': errors[0].get('code'),
                        'title': errors[0].get('title'),
                        'message': errors[0].get('message')
                    }
            
            # Salvar no banco se disponível
            if self.db:
                self._save_status_to_db(result)
            
            logging.info(f"STATUS UPDATE: {message_id} -> {status_type} para {recipient_id}")
            
            return result
            
        except Exception as e:
            logging.error(f"Erro ao processar status: {str(e)}")
            return None
    
    def _process_template_status(self, template_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Processar atualizações de status de template"""
        try:
            event = template_data.get('event')
            message_template_id = template_data.get('message_template_id')
            message_template_name = template_data.get('message_template_name')
            message_template_language = template_data.get('message_template_language')
            
            result = {
                'event_type': 'template_status',
                'event': event,
                'template_id': message_template_id,
                'template_name': message_template_name,
                'template_language': message_template_language
            }
            
            logging.info(f"TEMPLATE STATUS: {message_template_name} -> {event}")
            
            return result
            
        except Exception as e:
            logging.error(f"Erro ao processar status de template: {str(e)}")
            return None
    
    def _save_interaction_to_db(self, interaction_data: Dict[str, Any]):
        """Salvar interação no banco de dados"""
        try:
            if not self.db:
                return
                
            from models import ButtonInteraction
            
            # Extrair dados do botão se houver
            button_data = interaction_data.get('button_clicked', {})
            if not button_data:
                return
            
            interaction = ButtonInteraction(
                message_id=interaction_data.get('message_id'),
                from_phone=interaction_data.get('from'),
                phone_number_id=interaction_data.get('phone_number_id'),
                interaction_type=interaction_data.get('type', 'button_reply'),
                button_id=button_data.get('button_id'),
                button_title=button_data.get('button_title'),
                button_payload=json.dumps(button_data),
                interaction_timestamp=interaction_data.get('timestamp')
            )
            
            self.db.session.add(interaction)
            self.db.session.commit()
            
            logging.info(f"Interação salva: {button_data.get('button_title')} por {interaction_data.get('from')}")
            
        except Exception as e:
            logging.error(f"Erro ao salvar interação: {str(e)}")
            if self.db:
                self.db.session.rollback()
    
    def _save_status_to_db(self, status_data: Dict[str, Any]):
        """Salvar status no banco de dados"""
        try:
            if not self.db:
                return
                
            from models import MessageStatus
            
            # Verificar se já existe um status para esta mensagem
            existing_status = MessageStatus.query.filter_by(
                message_id=status_data.get('message_id'),
                status=status_data.get('status')
            ).first()
            
            if existing_status:
                return  # Status já existe
            
            error_data = status_data.get('error', {})
            
            status = MessageStatus(
                message_id=status_data.get('message_id'),
                recipient_phone=status_data.get('recipient_id'),
                phone_number_id=status_data.get('phone_number_id'),
                status=status_data.get('status'),
                status_timestamp=status_data.get('timestamp'),
                error_code=error_data.get('code'),
                error_title=error_data.get('title'),
                error_message=error_data.get('message')
            )
            
            self.db.session.add(status)
            self.db.session.commit()
            
            logging.info(f"Status salvo: {status_data.get('message_id')} -> {status_data.get('status')}")
            
        except Exception as e:
            logging.error(f"Erro ao salvar status: {str(e)}")
            if self.db:
                self.db.session.rollback()
    
    def get_button_interactions(self, phone_number: str = None, 
                              message_id: str = None, 
                              hours_back: int = 24) -> list:
        """Obter interações de botões dos últimos X horas"""
        try:
            if not self.db:
                return []
                
            from models import ButtonInteraction
            from datetime import datetime, timedelta
            
            # Construir query
            query = ButtonInteraction.query
            
            # Filtrar por telefone se especificado
            if phone_number:
                query = query.filter(ButtonInteraction.from_phone.like(f'%{phone_number}%'))
            
            # Filtrar por message_id se especificado
            if message_id:
                query = query.filter(ButtonInteraction.message_id == message_id)
            
            # Filtrar por tempo
            time_limit = datetime.utcnow() - timedelta(hours=hours_back)
            query = query.filter(ButtonInteraction.created_at >= time_limit)
            
            # Ordenar por mais recente
            query = query.order_by(ButtonInteraction.created_at.desc())
            
            interactions = query.all()
            
            return [interaction.to_dict() for interaction in interactions]
            
        except Exception as e:
            logging.error(f"Erro ao obter interações: {str(e)}")
            return []