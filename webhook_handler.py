#!/usr/bin/env python3
"""
Webhook Handler para capturar interações do WhatsApp Business API
Detecta cliques em botões, respostas de usuários, status de entrega, etc.
"""
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional
import json
import os

class WhatsAppWebhookHandler:
    """Handler para processar webhooks do WhatsApp Business API"""
    
    def __init__(self, db=None):
        self.db = db
        # Require secure webhook token
        verify_token = os.getenv('WHATSAPP_WEBHOOK_VERIFY_TOKEN')
        if not verify_token:
            # For development and production, use the same token that's in the interface
            verify_token = 'webhook_verify_token_12345_dev_only'
            logging.info("✅ Using interface webhook verify token: webhook_verify_token_12345_dev_only")
        else:
            logging.info(f"✅ Using environment webhook verify token: {verify_token}")
        self.verify_token = verify_token
        logging.info(f"🔑 Webhook Handler inicializado com token: {verify_token}")
        
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
                
            elif message_type == 'audio':
                # MENSAGEM DE ÁUDIO recebida
                audio_data = message.get('audio', {})
                result['media_url'] = audio_data.get('id')  # ID da mídia para download
                result['content'] = '[Áudio recebido]'
                result['mime_type'] = audio_data.get('mime_type', 'audio/ogg')
                logging.info(f"🎵 ÁUDIO RECEBIDO: {audio_data.get('id')} de {from_number}")
                
            elif message_type == 'voice':
                # MENSAGEM DE VOZ (nota de voz) recebida
                voice_data = message.get('voice', {})
                result['media_url'] = voice_data.get('id')  # ID da mídia para download
                result['content'] = '[Nota de voz recebida]'
                result['mime_type'] = voice_data.get('mime_type', 'audio/ogg')
                logging.info(f"🎤 VOZ RECEBIDA: {voice_data.get('id')} de {from_number}")
                
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
        """Salvar mensagem recebida no banco de dados usando novos modelos"""
        try:
            if not self.db:
                return
                
            from models import Contact, Conversation, ChatMessage
            
            phone_number = interaction_data.get('from')
            phone_number_id = interaction_data.get('phone_number_id')
            message_content = interaction_data.get('content', '')
            message_type = interaction_data.get('type', 'text')
            whatsapp_message_id = interaction_data.get('message_id')
            media_url = interaction_data.get('media_url')  # Para áudios e outras mídias
            
            # Processar clique em botão se houver
            button_data = interaction_data.get('button_clicked', {})
            if button_data:
                message_content = f"Botão clicado: {button_data.get('button_title', 'N/A')}"
                message_type = 'button_reply'
            
            # Processar seleção de lista se houver
            list_data = interaction_data.get('list_selected', {})
            if list_data:
                message_content = f"Lista selecionada: {list_data.get('list_title', 'N/A')}"
                message_type = 'list_reply'
            
            if not phone_number or not message_content or not phone_number_id:
                logging.warning(f"Dados incompletos: phone={phone_number}, content={message_content}, phone_id={phone_number_id}")
                return
            
            # Normalizar número (remover + e garantir formato consistente)
            def normalize_phone(phone):
                if not phone:
                    return phone
                # Remove + e espaços
                phone = phone.replace('+', '').replace(' ', '').replace('-', '')
                # Garantir que tem 13 dígitos (55 + 11 dígitos)
                if len(phone) == 11 and not phone.startswith('55'):
                    phone = '55' + phone
                return phone
            
            normalized_phone = normalize_phone(phone_number)
            contact = Contact.get_or_create(normalized_phone)
            
            # Buscar ou criar conversa
            conversation = Conversation.get_or_create(contact.id, phone_number_id)
            
            # ✅ PROTEÇÃO ANTI-DUPLICAÇÃO: Verificar se mensagem já existe
            existing_message = None
            if whatsapp_message_id:
                existing_message = ChatMessage.query.filter_by(
                    whatsapp_message_id=whatsapp_message_id
                ).first()
            
            if existing_message:
                logging.info(f"⚠️ Mensagem duplicada ignorada: {whatsapp_message_id}")
                return  # Não processar webhook duplicado
            
            # Criar mensagem (apenas se não existe)
            message = ChatMessage.create_inbound(
                conversation_id=conversation.id,
                whatsapp_message_id=whatsapp_message_id or f"fallback_{conversation.id}_{int(time.time())}",
                content=message_content,
                message_type=message_type,
                webhook_data=json.dumps(interaction_data)
            )
            
            # Adicionar URL de mídia se for áudio/voz
            if media_url and message_type in ['audio', 'voice']:
                message.media_url = media_url
                self.db.session.commit()
            
            logging.info(f"Mensagem recebida salva: {message_content[:50]}... de {phone_number}")
            
            # Commit da mensagem primeiro, depois disparar automação
            self.db.session.commit()
            
            # 🤖 DISPARAR AUTOMAÇÃO DE CONVERSAS (após commit)
            self._trigger_conversation_automation(normalized_phone, conversation.id, message_content, phone_number_id)
            
        except Exception as e:
            logging.error(f"Erro ao salvar mensagem: {str(e)}")
            if self.db:
                self.db.session.rollback()
    
    def _trigger_conversation_automation(self, phone_number: str, conversation_id: int, message_content: str, phone_number_id: str):
        """Disparar automação de conversa se necessário"""
        try:
            from services.conversation_automation import ConversationAutomation
            from services.whatsapp_business_api import WhatsAppBusinessAPI
            from app import app
            
            # Mapear botões interativos para texto padrão
            if message_content.startswith("Botão clicado:"):
                if "confirm_name_yes" in message_content or "✅ SIM" in message_content:
                    message_content = "SIM"
                elif "confirm_name_no" in message_content or "❌ NÃO" in message_content:
                    message_content = "NAO"
            
            # Usar nova sessão para automação (evitar conflitos)
            with app.app_context():
                # Inicializar WhatsApp API
                whatsapp_api = WhatsAppBusinessAPI()
                
                # FORÇAR uso do token válido armazenado globalmente
                # O token da sessão já foi carregado na inicialização da app
                valid_token = getattr(app, '_current_valid_token', None)
                if valid_token:
                    logging.info(f"🔑 Usando token válido armazenado: {valid_token[-6:]}")
                    whatsapp_api._access_token = valid_token
                    whatsapp_api._headers = {'Authorization': f'Bearer {valid_token}', 'Content-Type': 'application/json'}
                    whatsapp_api._phone_number_id = phone_number_id
                else:
                    logging.warning("⚠️ Nenhum token válido encontrado, usando padrão")
                
                # Inicializar automação com nova sessão e phone_number_id correto
                automation = ConversationAutomation(whatsapp_api, self.db, phone_number_id)
                
                # Verificar se deve disparar automação
                if automation.should_trigger_automation(phone_number, conversation_id):
                    logging.info(f"🤖 DISPARANDO AUTOMAÇÃO para {phone_number}")
                    automation.process_automation(phone_number, conversation_id, message_content, phone_number_id)
                else:
                    # Processar mensagem em conversa existente
                    logging.info(f"🤖 Processando mensagem em conversa existente: {phone_number}")
                    automation.process_automation(phone_number, conversation_id, message_content, phone_number_id)
            
        except Exception as e:
            logging.error(f"Erro na automação de conversa: {str(e)}")
    
    def _save_status_to_db(self, status_data: Dict[str, Any]):
        """Atualizar status de mensagem usando novos modelos"""
        try:
            if not self.db:
                return
                
            from models import ChatMessage
            
            whatsapp_message_id = status_data.get('message_id')
            new_status = status_data.get('status')
            
            if not whatsapp_message_id or not new_status:
                return
            
            # Buscar mensagem pelo WhatsApp message ID
            message = ChatMessage.query.filter_by(
                whatsapp_message_id=whatsapp_message_id
            ).first()
            
            if message:
                message.update_status(new_status)
                logging.info(f"Status atualizado: {whatsapp_message_id} -> {new_status}")
            else:
                logging.warning(f"Mensagem não encontrada para atualização de status: {whatsapp_message_id}")
            
        except Exception as e:
            logging.error(f"Erro ao atualizar status: {str(e)}")
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