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
        
    def should_trigger_automation(self, phone_number: str, conversation_id: int, message_content: str = "") -> bool:
        """Verifica se deve disparar automação para esta conversa"""
        try:
            from models import ChatMessage, ConversationState
            
            # 🚚 PRIORIDADE MÁXIMA: Mensagem trigger de entregador SEMPRE usa sistema automático
            delivery_trigger = "olá, desejo finalizar meu cadastro como entregador shopee"
            # Remover pontuação para comparação mais flexível
            clean_message = message_content.lower().strip().rstrip('.,!?;:')
            if clean_message == delivery_trigger.lower():
                logging.info(f"🚚 TRIGGER ENTREGADOR detectado - SISTEMA AUTOMÁTICO para {phone_number}")
                return True
            
            # Verificar estado persistente
            normalized_phone = self._normalize_phone(phone_number)
            conv_state = ConversationState.query.filter_by(phone_number=normalized_phone).first()
            
            # 🚨 NOVA LÓGICA: Sistema automático sempre tem prioridade
            if conv_state:
                # ✅ SEMPRE PROCESSAR se está em fluxo de entregador ou estados específicos
                delivery_states = [
                    'initial', 'waiting_personal_confirmation', 'waiting_vehicle_confirmation',
                    'waiting_cpf', 'confirming_name'
                ]
                
                if conv_state.current_state in delivery_states:
                    logging.info(f"🚚 SISTEMA AUTOMÁTICO ativo - Estado: {conv_state.current_state} para {phone_number}")
                    return True
                
                # ⚠️ ESTADOS HÍBRIDOS: Verificar se IA deve ter precedência
                hybrid_states = ['pending_questions']
                if conv_state.current_state in hybrid_states:
                    if conv_state.ai_enabled:
                        # IA habilitada - deixar IA processar
                        logging.info(f"🤖 IA ativa para estado híbrido: {conv_state.current_state} para {phone_number}")
                        return False
                    else:
                        # Sistema automático primeiro
                        logging.info(f"🚚 SISTEMA AUTOMÁTICO primeiro para estado híbrido: {conv_state.current_state} para {phone_number}")
                        return True
                
                # Para outros estados, processar pelo sistema automático
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
            
            # 🚚 NOVO FLUXO ENTREGADOR: Detectar mensagem específica
            if current_state == 'initial' and self._is_delivery_partner_message(message_content):
                return self._handle_delivery_partner_registration(conv_state, conversation_id, phone_number_id)
            elif current_state == 'initial':
                return self._handle_initial_contact(conv_state, conversation_id, phone_number_id)
            elif current_state == 'waiting_cpf':
                return self._handle_cpf_input(conv_state, conversation_id, message_content, phone_number_id)
            elif current_state == 'confirming_name':
                return self._handle_name_confirmation(conv_state, conversation_id, message_content, phone_number_id)
            # 🚚 NOVOS ESTADOS PARA ENTREGADOR
            elif current_state == 'waiting_personal_confirmation':
                return self._handle_personal_data_confirmation(conv_state, conversation_id, message_content, phone_number_id)
            elif current_state == 'waiting_vehicle_confirmation':
                return self._handle_vehicle_data_confirmation(conv_state, conversation_id, message_content, phone_number_id)
            # 🤖 ESTADOS HÍBRIDOS: Sistema automático verifica primeiro, depois IA
            elif current_state == 'pending_questions':
                # Verificar se é uma resposta do fluxo automático
                if self._is_automatic_flow_response(message_content, conv_state):
                    return self._handle_pending_questions(conv_state, conversation_id, message_content, phone_number_id)
                else:
                    # Habilitar IA para processar mensagem e persistir mudança
                    if not conv_state.ai_enabled:
                        conv_state.ai_enabled = True
                        from datetime import datetime, timezone, timedelta
                        brasilia_tz = timezone(timedelta(hours=-3))  # UTC-3 (Brasília)
                        conv_state.updated_at = datetime.now(brasilia_tz)
                        from app import db
                        db.session.commit()  # Persistir para próxima verificação
                        logging.info(f"🤖 IA habilitada e persistida para processar mensagem fora do fluxo: {message_content[:50]}")
                    
                    # Sinalizar que automação não processou - IA deve ser chamada
                    logging.info(f"🤖 Mensagem fora do fluxo automático - deixando IA processar: {message_content[:50]}")
                    return False
            
            return False
            
        except Exception as e:
            logging.error(f"Erro na automação: {str(e)}")
            return False
    
    def _is_automatic_flow_response(self, message_content: str, conv_state) -> bool:
        """Verifica se a mensagem é uma resposta esperada do fluxo automático"""
        message_lower = message_content.lower().strip()
        
        # Respostas padrão esperadas no fluxo automático
        expected_responses = [
            'sim', 's', 'yes', 'y', 'confirmo', 'ok', 'certo', 'correto',
            'não', 'nao', 'n', 'no', 'incorreto', 'errado'
        ]
        
        # CPF (11 dígitos)
        import re
        if re.match(r'^\d{11}$', message_content.strip()):
            return True
        
        # Respostas de botão clicado (formato: "Botão clicado: SIM")
        if 'botão clicado:' in message_lower or 'confirm_' in message_lower:
            return True
        
        # Respostas de botão/confirmação
        for response in expected_responses:
            if response in message_lower:  # Mudança: usar 'in' em vez de '=='
                return True
        
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
    
    def _is_delivery_partner_message(self, message_content: str) -> bool:
        """Verifica se a mensagem é de cadastro de entregador"""
        message_lower = message_content.lower().strip()
        delivery_keywords = [
            "olá, desejo finalizar meu cadastro como entregador shopee",
            "desejo finalizar meu cadastro como entregador shopee",
            "finalizar meu cadastro como entregador shopee",
            "cadastro como entregador shopee",
            "entregador shopee"
        ]
        
        for keyword in delivery_keywords:
            if keyword in message_lower:
                logging.info(f"🚚 MENSAGEM DE ENTREGADOR detectada: {message_content[:50]}")
                return True
        
        return False
    
    def _handle_delivery_partner_registration(self, conv_state, conversation_id: int, phone_number_id: str) -> bool:
        """Processa cadastro de entregador Shopee"""
        try:
            # Enviar mensagem de aguarde (SEM IA - só sistema automático)
            wait_message = (
                ""Aguarde um momento..."\n\n"
                "Estou buscando seu cadastro no sistema.\n"
            )
            
            success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, wait_message)
            if success:
                self._save_outbound_message(conversation_id, wait_message, result.get('messageId'))
            
            # Buscar dados na API Recoveryfy - extrair telefone correto
            from services.recoveryfy_api import RecoveryfyAPI
            api = RecoveryfyAPI()

            clean_phone = conv_state.phone_number.replace('+', '').replace(' ', '').replace('-', '')
            
            # Remover apenas o código do país "55" se presente
            if clean_phone.startswith('55') and len(clean_phone) == 12:
                # Seu caso: 556199114066
                # 55 (código) + 61 (DDD) + 99114066 (número)
                # Resultado: 61 + 9 + 99114066 = 61999114066
                ddd = clean_phone[2:4]  # 61
                numero = clean_phone[4:]  # 99114066  
                clean_phone = ddd + '9' + numero  # 61 + 9 + 99114066 = 61999114066
                logging.info(f"📱 Formato corrigido: {ddd} + 9 + {numero} = {clean_phone}")
            elif clean_phone.startswith('55'):
                # Caso geral - remover apenas 55
                clean_phone = clean_phone[2:]
            
            logging.info(f"📱 Telefone original: {conv_state.phone_number}")
            logging.info(f"📱 Telefone limpo para API: {clean_phone}")
            
            logging.info(f"🔍 Buscando dados na API para telefone: {clean_phone}")
            success, api_response = api.get_delivery_partner_data(clean_phone)
            
            # Verificar se retornou dados válidos
            if success and api_response and api_response.get('sucesso'):
                # Dados encontrados - criar/atualizar registro no banco
                from models import DeliveryPartner
                
                partner = DeliveryPartner.create_from_api_data(
                    phone_number=conv_state.phone_number, 
                    conversation_id=conversation_id, 
                    api_data=api_response
                )
                
                # Enviar mensagem de confirmação dos dados pessoais
                dados = api_response.get('dados', [{}])[0]
                nome = dados.get('nome', 'Nome não informado')
                cpf = dados.get('cpf', 'CPF não informado')
                cidade = dados.get('cidade', 'Cidade não informada')
                
                confirmation_message = (
                    f"✅ *Cadastro encontrado com sucesso!*\n\n"
                    f"Me confirme seus dados pessoais:\n\n"
                    f"*Nome:* {nome}\n"
                    f"*CPF:* {cpf}\n"
                    f"*Cidade:* {cidade}\n\n"
                    f"Se seus dados estão corretos clique no botão *SIM* abaixo:"
                )
                
                # Enviar com botão SIM
                buttons = [{"id": "confirm_yes", "title": "SIM"}]
                success_confirm, result_confirm = self.whatsapp_api.send_interactive_buttons(
                    conv_state.phone_number,
                    confirmation_message,
                    buttons
                )
                
                if success_confirm:
                    # Atualizar estado
                    conv_state.update_state('waiting_personal_confirmation')
                    self._save_outbound_message(conversation_id, confirmation_message + "\n[Botão: SIM]", result_confirm.get('messageId'))
                    
                    logging.info(f"✅ Dados do entregador enviados para confirmação: {nome}")
                    return True
                else:
                    # Fallback sem botão
                    simple_message = confirmation_message + "\n\nDigite *SIM* para confirmar."
                    success_simple, result_simple = self.whatsapp_api.send_text_message(conv_state.phone_number, simple_message)
                    if success_simple:
                        conv_state.update_state('waiting_personal_confirmation')
                        self._save_outbound_message(conversation_id, simple_message, result_simple.get('messageId'))
                        return True
            else:
                # Dados não encontrados
                error_message = (
                    "❌ Não conseguimos encontrar seus dados de cadastro no sistema.\n\n"
                    "🤔 Isso pode acontecer por alguns motivos:\n"
                    "• Seu telefone não está cadastrado\n"
                    "• Os dados ainda estão sendo processados\n"
                    "• Há algum erro no sistema\n\n"
                    "📞 Por favor, entre em contato com nosso suporte para verificação manual."
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, error_message)
                if success:
                    self._save_outbound_message(conversation_id, error_message, result.get('messageId'))
                
                return True
                
        except Exception as e:
            logging.error(f"Erro no cadastro de entregador: {str(e)}")
            return False
        
        return False
    
    def _handle_personal_data_confirmation(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processa confirmação dos dados pessoais"""
        try:
            message_lower = message_content.lower().strip()
            
            # Detectar resposta SIM (incluindo botões clicados)
            if (message_lower in ['sim', 's', 'yes', 'y', 'confirmo'] or 
                'sim' in message_lower or 'confirm_yes' in message_lower):
                # Dados confirmados - marcar no banco e enviar dados do veículo
                from models import DeliveryPartner
                
                partner = DeliveryPartner.get_by_phone(conv_state.phone_number)
                if partner:
                    partner.confirmed_personal_data = True
                    
                    # Enviar dados do veículo para confirmação
                    # Verificar se o carro é alugado/emprestado
                    carro_status = ""
                    if partner.carro_alugado and partner.carro_alugado.lower() in ['true', 'sim', '1', 'yes']:
                        carro_status = f"🔄 *Status:* Veículo alugado/emprestado\n"
                    
                    vehicle_message = (
                        f"✅ *Dados pessoais confirmados!*\n\n"
                        f"🚗 Agora confirme os dados do seu veículo:\n\n"
                        f"🚙 *Tipo:* {partner.tipo_veiculo or 'Não informado'}\n"
                        f"🏷️ *Placa:* {partner.placa or 'Não informada'}\n"
                        f"🎨 *Cor:* {partner.veiculo_cor or 'Não informada'}\n"
                        f"🏭 *Marca:* {partner.veiculo_marca or 'Não informada'}\n"
                        f"🚗 *Modelo:* {partner.veiculo_modelo or 'Não informado'}\n"
                        f"📅 *Ano:* {partner.veiculo_ano or 'Não informado'}\n"
                        f"{carro_status}"
                        f"\n❓ Os dados do veículo estão corretos?"
                    )
                    
                    # Enviar com botão SIM
                    buttons = [{"id": "confirm_vehicle_yes", "title": "SIM"}]
                    success_vehicle, result_vehicle = self.whatsapp_api.send_interactive_buttons(
                        conv_state.phone_number,
                        vehicle_message,
                        buttons
                    )
                    
                    if success_vehicle:
                        conv_state.update_state('waiting_vehicle_confirmation')
                        self._save_outbound_message(conversation_id, vehicle_message + "\n[Botão: SIM]", result_vehicle.get('messageId'))
                        return True
                    else:
                        # Fallback sem botão
                        simple_message = vehicle_message + "\n\nDigite *SIM* para confirmar."
                        success_simple, result_simple = self.whatsapp_api.send_text_message(conv_state.phone_number, simple_message)
                        if success_simple:
                            conv_state.update_state('waiting_vehicle_confirmation')
                            self._save_outbound_message(conversation_id, simple_message, result_simple.get('messageId'))
                            return True
                else:
                    logging.error("❌ Entregador não encontrado no banco")
                    return False
                    
            else:
                # Não confirmou - solicitar correção
                error_message = (
                    "❌ Para prosseguir, você precisa confirmar que seus dados pessoais estão corretos.\n\n"
                    "📞 Se há algum erro nos dados, entre em contato com nosso suporte.\n\n"
                    "✅ Digite *SIM* para confirmar que os dados estão corretos."
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, error_message)
                if success:
                    self._save_outbound_message(conversation_id, error_message, result.get('messageId'))
                
                return True
                
        except Exception as e:
            logging.error(f"Erro na confirmação de dados pessoais: {str(e)}")
            return False
    
    def _handle_vehicle_data_confirmation(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processa confirmação dos dados do veículo"""
        try:
            message_lower = message_content.lower().strip()
            
            # Detectar resposta SIM (incluindo botões clicados)
            if (message_lower in ['sim', 's', 'yes', 'y', 'confirmo'] or 
                'sim' in message_lower or 'confirm_vehicle_yes' in message_lower):
                # Dados do veículo confirmados - finalizar cadastro
                from models import DeliveryPartner
                
                partner = DeliveryPartner.get_by_phone(conv_state.phone_number)
                if partner:
                    partner.confirmed_vehicle_data = True
                    partner.registration_approved = True
                    
                    # Verificar status na API de cliente
                    from services.recoveryfy_api import RecoveryfyAPI
                    api = RecoveryfyAPI()
                    
                    success_status, status_data = api.check_client_status(partner.cpf)
                    
                    if success_status and status_data.get('status') == 'PENDING':
                        # Status PENDING - ativar IA
                        approval_message = (
                            f"🎉 *Parabéns! Seu cadastro como Entregador Shopee foi aprovado com sucesso!*\n\n"
                            f"✅ Todos os seus dados foram confirmados e validados.\n\n"
                            f"📋 Para finalizar completamente seu processo, nossa assistente Zilma irá te ajudar com os próximos passos.\n\n"
                            f"💬 Continue a conversa para receber todas as orientações!"
                        )
                        
                        success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, approval_message)
                        if success:
                            self._save_outbound_message(conversation_id, approval_message, result.get('messageId'))
                        
                        # Ativar IA para próximas interações, mas manter sistema automático disponível
                        conv_state.cpf_status = 'PENDING'
                        conv_state.original_cpf = partner.cpf
                        conv_state.ai_enabled = True  # IA habilitada apenas como backup
                        conv_state.update_state('pending_questions')
                        
                        logging.info(f"✅ Cadastro de entregador aprovado - IA ativada para {conv_state.phone_number}")
                        return True
                    else:
                        # Status não é PENDING - enviar informações sobre Kit EPI e taxa
                        cpf_clean = partner.cpf.replace('.', '').replace('-', '')
                        payment_link = f"https://shopee.acesso.inc/{cpf_clean}"
                        
                        kit_message = (
                            f"🎉 *Cadastro aprovado com sucesso!*\n\n"
                            f"✅ Parabéns! Seu cadastro como Entregador Shopee foi aprovado!\n\n"
                            f"Para começar a realizar as entregas, você precisa receber:\n"
                            f"• Kit EPI (Equipamentos de Proteção Individual)\n"
                            f"• Cartão salário\n\n"
                            f"A Shopee cobra uma taxa de entrega no valor de *R$ 64,90*\n\n"
                            f"❗ Esta taxa existe porque muitas pessoas estavam se cadastrando apenas para receber os equipamentos gratuitamente, prejudicamento a nossa empresa. Após 15 dias realizando entregas com a nossa empresa vamos reembolsar este valor em seu Cartão Shopee.\n\n"
                            f"*Prazo de entrega:* até 5 dias úteis\n\n"
                            f"*Processo:* Após o pagamento, nos envie o comprovante que aprovaremos seu cadastro ainda hoje e passaremos todas as instruções!"
                        )
                        
                        # Enviar mensagem com botão de pagamento
                        success_kit, result_kit = self.whatsapp_api.send_interactive_cta_url_message(
                            conv_state.phone_number,
                            kit_message,
                            "Finalizar Cadastro",
                            payment_link
                        )
                        
                        if success_kit:
                            self._save_outbound_message(conversation_id, kit_message + f"\n[Botão: Finalizar Cadastro - {payment_link}]", result_kit.get('messageId'))
                        
                        # Segunda mensagem sobre dúvidas
                        doubt_message = (
                            f"💬 Se você tiver alguma dúvida, pode escrever ou mandar um áudio!\n\n"
                            f"👨‍💼 Estou de prontidão para tirar todas as suas dúvidas. 😊"
                        )
                        
                        success_doubt, result_doubt = self.whatsapp_api.send_text_message(conv_state.phone_number, doubt_message)
                        if success_doubt:
                            self._save_outbound_message(conversation_id, doubt_message, result_doubt.get('messageId'))
                        
                        # Ativar IA a partir deste momento
                        conv_state.cpf_status = 'PENDING'
                        conv_state.original_cpf = partner.cpf
                        conv_state.ai_enabled = True
                        conv_state.update_state('pending_questions')
                        
                        logging.info(f"✅ Kit EPI enviado e IA ativada para {conv_state.phone_number}")
                        return True
                        
                else:
                    logging.error("❌ Entregador não encontrado no banco")
                    return False
                    
            else:
                # Não confirmou - solicitar correção
                error_message = (
                    "❌ Para prosseguir, você precisa confirmar que os dados do veículo estão corretos.\n\n"
                    "📞 Se há algum erro nos dados, entre em contato com nosso suporte.\n\n"
                    "✅ Digite *SIM* para confirmar que os dados estão corretos."
                )
                
                success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, error_message)
                if success:
                    self._save_outbound_message(conversation_id, error_message, result.get('messageId'))
                
                return True
                
        except Exception as e:
            logging.error(f"Erro na confirmação de dados do veículo: {str(e)}")
            return False
        
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
    
    def _save_outbound_message(self, conversation_id: int, content: str, whatsapp_message_id: Optional[str] = None):
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
            import os
            cache_file = os.path.join(tempfile.gettempdir(), "whatsapp_active_token.txt")
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    return f.read().strip()
        except Exception as e:
            logging.warning(f"Falha ao carregar token ativo: {e}")
        return ""
    
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
                
                # Enviar mensagem com botões (usando método interno)
                success2, result2 = self._send_interactive_buttons(
                    conv_state.phone_number,
                    second_message,
                    [
                        {
                            'type': 'reply',
                            'reply': {
                                'id': 'pending_doubt_yes',
                                'title': '✅ SIM'
                            }
                        },
                        {
                            'type': 'reply',
                            'reply': {
                                'id': 'pending_doubt_no',
                                'title': '❌ NÃO'
                            }
                        }
                    ]
                )
                
                if success2:
                    self._save_outbound_message(conversation_id, second_message + " [Com botões: SIM/NÃO]", result2.get('messageId'))
                    
                    # Atualizar estado para aguardar resposta dos botões
                    conv_state.update_state('pending_questions')
                    
                    # ✅ SALVAR CLIENTE PENDING PARA RASTREAMENTO AUTOMÁTICO
                    self._save_pending_client_for_tracking(conv_state, nome)
                    
                    logging.info(f"✅ Fluxo PENDING iniciado para {conv_state.phone_number}: {nome[:20]}...")
                    return True
                else:
                    # Se falhar, tenta enviar apenas a mensagem básica
                    basic_message = second_message + "\n\n🤔 Pode me responder SIM ou NÃO?"
                    
                    success3, result3 = self.whatsapp_api.send_text_message(conv_state.phone_number, basic_message)
                    if success3:
                        self._save_outbound_message(conversation_id, basic_message, result3.get('messageId'))
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
            
            # Verificar se é problema com PIX (código inválido, não consegue gerar, etc)
            elif any(keyword in content_lower for keyword in [
                'pix inválido', 'pix invalido', 'não consegue gerar', 'nao consegue gerar',
                'código inválido', 'codigo invalido', 'não funciona o pix', 'nao funciona o pix',
                'erro no pix', 'pix não', 'pix nao', 'problema pix', 'deu erro', 'não gerou',
                'nao gerou', 'pix expirado', 'expirou', 'código expirado', 'codigo expirado'
            ]):
                # Cliente tem problema com PIX - enviar código copia e cola
                return self._send_pix_copy_paste(conv_state, conversation_id, message_content, phone_number_id)
                
            else:
                # É uma pergunta do usuário - processar com OpenAI
                return self._process_openai_question(conv_state, conversation_id, message_content, phone_number_id)
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao processar perguntas PENDING: {str(e)}")
            return False
    
    def _build_conversation_context(self, conversation_id: int) -> list:
        """Construir contexto da conversa para IA com as últimas mensagens"""
        try:
            from models import ChatMessage
            
            # Buscar últimas 10 mensagens da conversa (5 pares pergunta/resposta)
            messages = ChatMessage.query.filter_by(
                conversation_id=conversation_id
            ).order_by(ChatMessage.created_at.desc()).limit(10).all()
            
            # Reverter ordem para cronológica (mais antiga primeiro)
            messages.reverse()
            
            conversation_history = []
            
            for msg in messages:
                # Filtrar apenas mensagens relevantes (texto, não status)
                if msg.message_type == 'text' and msg.content and msg.content.strip():
                    # Limpar prefixos do sistema
                    content = msg.content
                    if content.startswith('🤖 IA: '):
                        content = content[7:]  # Remove prefix "🤖 IA: "
                    
                    # Mapear direção para role da IA
                    if msg.direction == 'inbound':
                        role = 'user'
                    else:
                        role = 'assistant'
                    
                    # Filtrar mensagens que não são conversacionais (botões, sistemas, etc)
                    if not any(x in content.lower() for x in [
                        'finalizar cadastro', 'gancho #', '🎣', 'whatsapp',
                        'sistema', 'status', 'webhook', 'button', '❌', '✅'
                    ]):
                        conversation_history.append({
                            "role": role,
                            "content": content.strip()
                        })
            
            logging.info(f"📚 Contexto construído: {len(conversation_history)} mensagens para conversation_id={conversation_id}")
            return conversation_history[-6:]  # Últimas 6 mensagens para não sobrecarregar
            
        except Exception as e:
            logging.error(f"Erro ao construir contexto da conversa: {str(e)}")
            return []  # Retorna lista vazia em caso de erro
    
    def _process_openai_question(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Processar pergunta do usuário usando OpenAI (texto ou áudio)"""
        try:
            from openai_service import ShopeeDeliveryAssistant
            from models import ChatMessage
            
            # 🚀 LIMITE REMOVIDO: IA pode conversar indefinidamente até convencer o cliente
            current_ai_count = conv_state.question_count or 0
            
            # Incrementar contador de perguntas (apenas para estatísticas)
            conv_state.question_count = current_ai_count + 1
            
            logging.info(f"🤖 Processando pergunta #{conv_state.question_count} via OpenAI para {conv_state.phone_number} - SEM LIMITE")
            
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
                    # Buscar histórico da conversa para contexto do áudio também
                    conversation_history = self._build_conversation_context(conversation_id)
                    
                    ai_response = ShopeeDeliveryAssistant.get_response_from_audio(
                        media_download_url,
                        self.whatsapp_api._access_token,
                        conversation_history
                    )
                else:
                    ai_response = "Desculpe, não consegui processar o áudio. Pode me escrever sua dúvida?"
            else:
                # Buscar histórico da conversa para contexto
                conversation_history = self._build_conversation_context(conversation_id)
                
                # Processar como texto normal com contexto
                ai_response = ShopeeDeliveryAssistant.get_response(message_content, conversation_history)
            
            # 🐛 DEBUG: Verificar resposta da IA antes de enviar
            logging.info(f"🔍 DEBUG ai_response: '{ai_response}' (tipo: {type(ai_response)})")
            
            if not ai_response or ai_response.strip() == "":
                logging.error("🚨 AI_RESPONSE VAZIO! Usando fallback urgente")
                ai_response = "Entendo sua dúvida! 😊\n\nO Kit EPI (R$ 64,90) é obrigatório e precisa ser pago via PIX para enviarmos os equipamentos e ativar seu Cartão Salário. É um processo padrão para todos os entregadores da Shopee.\n\nVamos finalizar?"
            
            # Enviar resposta da IA
            success, result = self.whatsapp_api.send_text_message(conv_state.phone_number, ai_response)
            if success:
                self._save_outbound_message(conversation_id, f"🤖 IA: {ai_response}", result.get('messageId'))
                
                # Salvar contador já incrementado no início do método
                self.db.session.commit()
                
                # 🚀 SEMPRE enviar botão de pagamento após cada resposta da IA
                import time
                time.sleep(1)  # Pequena pausa para parecer natural
                
                # 🚀 LIMITE REMOVIDO: Sempre continuar tentando convencer o cliente
                # Para qualquer tentativa: Enviar mensagem de gancho + botão
                return self._send_hook_with_payment_button(conv_state, conversation_id, phone_number_id)
                
                # Código antigo removido - agora sempre vai para pagamento
            
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
    
    def _send_hook_with_payment_button(self, conv_state, conversation_id: int, phone_number_id: str) -> bool:
        """Enviar mensagem de gancho + botão de pagamento após resposta da IA"""
        try:
            # Extrair primeiro nome
            import json
            client_data = json.loads(conv_state.client_data) if conv_state.client_data else {}
            cliente_info = client_data.get('cliente', {})
            full_name = cliente_info.get('nome', 'Usuário')
            first_name = full_name.split()[0] if full_name and full_name != 'Usuário' else 'Usuário'
            
            # Mensagem de gancho baseada no número da tentativa
            hook_messages = [
                f"Espero ter esclarecido sua dúvida {first_name}! 💡\n\nPara finalizar seu cadastro como entregador Shopee, falta apenas o pagamento da taxa de entrega do Kit EPI e do Cartão Salário.\n\n⚠️ *URGENTE:* Restam apenas 2 vagas na sua região!",
                f"Perfeito {first_name}! 🎯\n\nSeu cadastro está quase completo. Para iniciar suas atividades como entregador, precisamos processar o pagamento da taxa de entrega do equipamento obrigatório.\n\n📋 Finalize agora para começar a trabalhar:",
                f"Excelente pergunta {first_name}! 💪\n\nComo gerente de contratação, confirmo que falta apenas o pagamento da taxa de entrega para concluirmos seu processo de contratação.\n\n📲 Finalize seu cadastro:",
                f"Fico feliz em esclarecer isso {first_name}! ✅\n\nA Shopee precisa processar a taxa de entrega do Kit EPI e Cartão Salário para ativar seu cadastro profissional.\n\n⚡ Complete seu cadastro:",
                f"Esperava essa pergunta {first_name}! 🧠\n\nO processo é simples e seguro. Após o pagamento da taxa de entrega, você receberá todo o material necessário para iniciar.\n\n💎 Finalize agora:",
            ]
            
            # Usar mensagem baseada no número da tentativa (ciclo entre as mensagens)
            hook_index = (conv_state.question_count - 1) % len(hook_messages)
            hook_message = hook_messages[hook_index]
            
            # Criar link personalizado usando CPF original sem pontuação
            cpf_clean = conv_state.original_cpf  # CPF já está sem pontuação
            payment_link = f"https://shopee.acesso.inc/{cpf_clean}"
            
            # Enviar mensagem com botão de pagamento
            success, result = self.whatsapp_api.send_interactive_cta_url_message(
                conv_state.phone_number,
                hook_message,
                "Finalizar Cadastro",
                payment_link
            )
            
            if success:
                self._save_outbound_message(conversation_id, hook_message + f"\n[Botão: Finalizar Cadastro - {payment_link}]", result.get('messageId'))
                logging.info(f"🎣 Gancho #{conv_state.question_count} enviado para {conv_state.phone_number}")
                
                # Manter no estado pending_questions para permitir mais perguntas
                return True
            else:
                # Se falhar, tentar novamente com botão mais simples
                simple_message = f"Para finalizar seu cadastro {first_name}, falta apenas o pagamento da taxa de entrega.\n\nClique no botão abaixo:"
                success_retry, result_retry = self.whatsapp_api.send_interactive_cta_url_message(
                    conv_state.phone_number,
                    simple_message,
                    "Finalizar",
                    payment_link
                )
                if success_retry:
                    self._save_outbound_message(conversation_id, simple_message + f"\n[Botão: Finalizar Cadastro - {payment_link}]", result_retry.get('messageId'))
                    return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao enviar gancho com botão: {str(e)}")
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
                "Finalizar Cadastro",
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
    
    def _send_pix_copy_paste(self, conv_state, conversation_id: int, message_content: str, phone_number_id: str) -> bool:
        """Enviar código PIX copia e cola quando cliente tem problemas com PIX"""
        try:
            import json
            
            # Extrair dados do cliente salvos
            if not conv_state.client_data:
                logging.error("Dados do cliente não encontrados para enviar código PIX")
                return False
            
            client_data = json.loads(conv_state.client_data)
            
            # Extrair código PIX da última transação
            ultima_transacao = client_data.get('ultima_transacao', {})
            codigo_pix = ultima_transacao.get('codigo_pix')
            
            if not codigo_pix:
                logging.warning("Código PIX não encontrado nos dados do cliente")
                # Fallback - enviar link de pagamento normal
                return self._send_pending_payment_link(conv_state, conversation_id, phone_number_id)
            
            # Extrair nome do cliente para personalizar resposta
            cliente_info = client_data.get('cliente', {})
            full_name = cliente_info.get('nome', 'Usuário')
            first_name = full_name.split()[0] if full_name and full_name != 'Usuário' else 'Usuário'
            
            # Usar IA para formular resposta sobre o problema com PIX
            from openai_service import ShopeeDeliveryAssistant
            
            ai_context = f"Cliente {first_name} está com problema no PIX: '{message_content}'. Responda de forma empática e explique que vou enviar o código copia e cola."
            ai_response = ShopeeDeliveryAssistant.get_response(ai_context)
            
            # Enviar resposta da IA primeiro (SEM prefixo para o usuário)
            success1, result1 = self.whatsapp_api.send_text_message(conv_state.phone_number, ai_response)
            if success1:
                # Salvar no banco COM prefixo apenas para logs internos
                self._save_outbound_message(conversation_id, f"🤖 IA: {ai_response}", result1.get('messageId'))
            
            # Pequena pausa para parecer natural
            import time
            time.sleep(2)
            
            # Mensagem com código PIX
            pix_message = (
                f"📋 *CÓDIGO PIX COPIA E COLA*\n\n"
                f"Aqui está seu código PIX para pagamento do Kit EPI + Cartão Salário (R$ 64,90):\n\n"
                f"```{codigo_pix}```\n\n"
                f"📱 *Como usar:*\n"
                f"1. Abra seu app do banco\n"
                f"2. Vá em PIX → Pagar\n"
                f"3. Escolha 'Código copia e cola'\n"
                f"4. Cole o código acima\n"
                f"5. Confirme o pagamento de R$ 64,90\n\n"
                f"⚡ Seu cadastro será ativado automaticamente após o pagamento!"
            )
            
            # Enviar código PIX como texto (WhatsApp não suporta botão de copiar nativo)
            time.sleep(1)
            
            # Mensagem simples com código PIX formatado para fácil cópia
            final_pix_message = (
                f"📋 *CÓDIGO PIX COPIA E COLA*\n\n"
                f"{codigo_pix}\n\n"
                f"💡 *Como usar:*\n"
                f"1. Toque e segure no código acima para copiar\n"
                f"2. Abra seu app do banco\n"
                f"3. Vá em PIX → Pagar → Código copia e cola\n"
                f"4. Cole o código\n"
                f"5. Confirme o pagamento de R$ 64,90\n\n"
                f"⚡ Após o pagamento, seu cadastro será ativado automaticamente!"
            )
            
            success2, result2 = self.whatsapp_api.send_text_message(conv_state.phone_number, final_pix_message)
            
            if success2:
                self._save_outbound_message(conversation_id, final_pix_message, result2.get('messageId'))
                
                # Limpar estado da automação após enviar PIX
                conv_state.clear_state()
                logging.info(f"✅ Código PIX copia e cola enviado para {conv_state.phone_number}")
                return True
            
            return False
            
        except Exception as e:
            logging.error(f"Erro ao enviar código PIX copia e cola: {str(e)}")
            # Fallback em caso de erro
            return self._send_pending_payment_link(conv_state, conversation_id, phone_number_id)
    
    def _save_pending_client_for_tracking(self, conv_state, nome: str):
        """Salvar cliente PENDING na tabela para rastreamento automático"""
        try:
            from models import PendingClient
            import json
            
            # Extrair dados do cliente
            if not conv_state.client_data or not conv_state.original_cpf:
                logging.warning(f"Dados insuficientes para salvar cliente PENDING: {conv_state.phone_number}")
                return
            
            client_data = json.loads(conv_state.client_data)
            cliente_info = client_data.get('cliente', {})
            
            # Extrair nome completo da API, se não tiver usa o passado
            full_name = cliente_info.get('nome', nome)
            first_name = nome.split()[0] if nome else 'Cliente'
            
            # Salvar na tabela PendingClient
            pending_client = PendingClient.add_pending_client(
                cpf=conv_state.original_cpf,
                phone_number=conv_state.phone_number,
                first_name=first_name,
                full_name=full_name,
                client_data=conv_state.client_data
            )
            
            if pending_client:
                logging.info(f"✅ Cliente PENDING salvo para rastreamento: {conv_state.original_cpf} - {first_name}")
            else:
                logging.error(f"❌ Erro ao salvar cliente PENDING: {conv_state.original_cpf}")
                
        except Exception as e:
            logging.error(f"Erro ao salvar cliente PENDING para rastreamento: {str(e)}")