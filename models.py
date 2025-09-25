from app import db
from datetime import datetime, timezone, timedelta
import time
import logging
from typing import Optional

# 🇧🇷 TIMEZONE BRASILEIRO
def brasilia_now():
    """⚠️ DESIGN DECISION ADR-001 - DO NOT CHANGE ⚠️
    Returns current datetime in Brazil timezone (UTC-3) as NAIVE datetime.
    
    CRITICAL: This function MUST return naive datetime (no tzinfo).
    Timezone-aware values are FORBIDDEN in our database schema.
    This design ensures:
    - Human-friendly timestamps in Brazilian time
    - Consistent ordering without DB timezone conversion quirks
    - Avoids mixed timezone ordering bugs
    
    Changing this requires data migration and extensive testing!
    """
    # ✅ CORRIGIDO: Retorna datetime naive já no horário brasileiro
    # Evita problemas de conversão do PostgreSQL
    brasil_tz = timezone(timedelta(hours=-3))
    br_time = datetime.now(brasil_tz)
    return br_time.replace(tzinfo=None)  # Remove timezone, mantém horário brasileiro

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), unique=True, nullable=False)
    total_leads = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    progress = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='processing')
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    lead_name = db.Column(db.String(100))
    lead_cpf = db.Column(db.String(20))
    template_name = db.Column(db.String(100))
    phone_number_id = db.Column(db.String(50))
    message_id = db.Column(db.String(200))
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=brasilia_now)
    
    # Z-API specific fields
    api_response = db.Column(db.Text)
    delivery_status = db.Column(db.String(50))

class SentNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    lead_name = db.Column(db.String(100))
    lead_cpf = db.Column(db.String(20))
    message_id = db.Column(db.String(200))
    sent_at = db.Column(db.DateTime, default=brasilia_now)
    
    @staticmethod
    def is_number_sent(phone_number):
        """Check if a phone number has already been sent a message"""
        return SentNumber.query.filter_by(phone_number=phone_number).first() is not None
    
    @staticmethod  
    def add_sent_number(phone_number, lead_name=None, lead_cpf=None, message_id=None):
        """Add a phone number to the sent list"""
        sent_number = SentNumber()
        sent_number.phone_number = phone_number
        sent_number.lead_name = lead_name
        sent_number.lead_cpf = lead_cpf
        sent_number.message_id = message_id
        return sent_number

class Contact(db.Model):
    """Modelo para gerenciar contatos/clientes"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100))
    profile_picture_url = db.Column(db.String(500))
    last_message_at = db.Column(db.DateTime)
    is_blocked = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)
    
    # Relacionamentos
    conversations = db.relationship('Conversation', backref='contact', lazy=True)
    
    @staticmethod
    def get_or_create(phone_number: str, name: Optional[str] = None):
        """Busca contato existente ou cria novo"""
        contact = Contact.query.filter_by(phone_number=phone_number).first()
        if not contact:
            contact = Contact(
                phone_number=phone_number,
                name=name or f"Cliente {phone_number[-4:]}"
            )
            db.session.add(contact)
            db.session.commit()
        elif name and not contact.name:
            contact.name = name
            db.session.commit()
        return contact

class Conversation(db.Model):
    """Modelo para conversas/chats"""
    id = db.Column(db.Integer, primary_key=True)
    contact_id = db.Column(db.Integer, db.ForeignKey('contact.id'), nullable=False)
    whatsapp_phone_id = db.Column(db.String(50), nullable=False)  # ID do número do WhatsApp Business usado
    last_message_id = db.Column(db.Integer, db.ForeignKey('chat_message.id'))
    last_message_at = db.Column(db.DateTime)
    unread_count = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)
    
    # Relacionamentos
    # 🛡️ FIXED: Order by ID to match API consistency (avoids timezone ordering bugs)
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, 
                              foreign_keys='ChatMessage.conversation_id', 
                              order_by='ChatMessage.id.asc()')
    last_message = db.relationship('ChatMessage', foreign_keys=[last_message_id], 
                                  post_update=True, viewonly=True)
    
    @staticmethod
    def get_or_create(contact_id: int, whatsapp_phone_id: str):
        """Busca conversa existente ou cria nova"""
        conversation = Conversation.query.filter_by(
            contact_id=contact_id,
            whatsapp_phone_id=whatsapp_phone_id
        ).first()
        
        if not conversation:
            conversation = Conversation(
                contact_id=contact_id,
                whatsapp_phone_id=whatsapp_phone_id
            )
            db.session.add(conversation)
            db.session.commit()
        
        return conversation
    
    def mark_as_read(self):
        """Marca conversa como lida"""
        self.unread_count = 0
        db.session.commit()

class ChatMessage(db.Model):
    """⚠️ CRITICAL PATH MODEL - HANDLE WITH EXTREME CARE ⚠️
    
    This model is part of the core webhook→database→chat flow.
    Any changes to this schema or field behavior can break:
    - WhatsApp webhook message saving
    - Chat interface message display 
    - Message ordering and chronology
    
    PROTECTED INVARIANTS:
    - created_at: MUST use brasilia_now() (naive BR time only)
    - direction: MUST be 'inbound' or 'outbound' only
    - content: MUST NOT be null (required for display)
    - whatsapp_message_id: MUST be unique (prevents duplicates)
    - conversation_id: MUST be valid FK (required for queries)
    
    UPDATE TESTS BEFORE MODIFYING!
    """
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    whatsapp_message_id = db.Column(db.String(200), unique=True)  # ID da mensagem no WhatsApp
    direction = db.Column(db.String(10), nullable=False)  # 'inbound' ou 'outbound'
    message_type = db.Column(db.String(20), default='text')  # text, image, document, etc.
    content = db.Column(db.Text, nullable=False)  # 🛡️ PROTECTED: Required for display
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, read, failed
    
    # Metadados para diferentes tipos de mensagem
    media_url = db.Column(db.String(500))  # Para imagens, documentos, etc.
    media_caption = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=brasilia_now)  # 🛡️ PROTECTED: naive BR time only
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    
    # Dados do webhook (para inbound)
    webhook_data = db.Column(db.Text)  # JSON completo do webhook
    
    @staticmethod
    def create_inbound(conversation_id: int, whatsapp_message_id: str, content: str, 
                      message_type: str = 'text', webhook_data: str = None):
        """🛡️ PROTECTED: Cria mensagem recebida (inbound)"""
        # 🛡️ RUNTIME PROTECTION: Validate critical fields (but allow WhatsApp flexibility)
        if conversation_id is None:
            logging.error("CRITICAL: conversation_id cannot be None")
            raise ValueError("conversation_id cannot be None")
        
        # 🛡️ SAFE HANDLING: Never crash webhook flow, always log and adapt
        if not message_type or message_type == 'text':
            if not content or not content.strip():
                logging.warning("Text message with empty content - using fallback")
                content = "[Mensagem vazia]"  # Safe fallback for display
        
        # Ensure content is never None (satisfies nullable=False constraint)
        if not content:
            content = ""  # Safe fallback for non-text messages
        
        # Log unknown message types but don't block them (WhatsApp adds new types)
        known_types = ['text', 'image', 'document', 'audio', 'video', 'interactive', 'button', 'sticker', 'contacts', 'location', 'reaction', 'system']
        if message_type and message_type not in known_types:
            logging.warning(f"Unknown message_type: {message_type} - allowing but consider updating known types")
        
        message = ChatMessage(
            conversation_id=conversation_id,
            whatsapp_message_id=whatsapp_message_id,
            direction='inbound',  # 🛡️ PROTECTED: Must be 'inbound'
            message_type=message_type,
            content=content,
            status='received',
            webhook_data=webhook_data
        )
        db.session.add(message)
        
        # Atualizar conversa
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            # Usar timestamp atual explicitamente
            current_time = brasilia_now()
            message.created_at = current_time  # Garantir que está definido
            conversation.last_message_at = current_time
            conversation.last_message_id = None  # Será atualizado após commit
            conversation.unread_count += 1
            conversation.updated_at = current_time
        
        db.session.commit()
        
        # Atualizar last_message_id após commit (quando message.id já existe)
        if conversation:
            conversation.last_message_id = message.id
            db.session.commit()
            
        return message
    
    @staticmethod
    def create_outbound(conversation_id: int, content: str, message_type: str = 'text'):
        """🛡️ PROTECTED: Cria mensagem enviada (outbound)"""
        # 🛡️ RUNTIME PROTECTION: Validate critical fields
        if conversation_id is None:
            logging.error("CRITICAL: conversation_id cannot be None")
            raise ValueError("conversation_id cannot be None")
        
        # 🛡️ SAFE HANDLING: Never crash outbound flow
        if not content or not content.strip():
            logging.warning("Outbound message with empty content - using fallback")
            content = "[Mensagem vazia]"  # Safe fallback
        
        # Log unknown message types but don't block them
        known_types = ['text', 'image', 'document', 'audio', 'video', 'interactive', 'button']
        if message_type and message_type not in known_types:
            logging.warning(f"Unknown outbound message_type: {message_type} - allowing but consider updating known types")
        
        message = ChatMessage(
            conversation_id=conversation_id,
            direction='outbound',  # 🛡️ PROTECTED: Must be 'outbound'
            message_type=message_type,
            content=content,
            status='pending'
        )
        db.session.add(message)
        db.session.commit()
        return message
    
    def update_status(self, status: str, whatsapp_message_id: str = None):
        """Atualiza status da mensagem"""
        self.status = status
        if whatsapp_message_id:
            self.whatsapp_message_id = whatsapp_message_id
        
        now = brasilia_now()
        if status == 'sent':
            self.sent_at = now
        elif status == 'delivered':
            self.delivered_at = now
        elif status == 'read':
            self.read_at = now
        
        db.session.commit()

class ConversationState(db.Model):
    """Estado persistente de conversas para automação com IA totalmente autônoma"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    
    # Estados expandidos para IA autônoma
    current_state = db.Column(db.String(50), default='initial')  
    # Estados possíveis: initial, greeting_sent, intent_detected, information_gathering, 
    # api_consulting, resolving_issue, waiting_user_response, human_handoff, closed
    
    # Dados do contexto conversacional
    context_data = db.Column(db.Text)  # JSON com contexto da conversa para IA
    client_data = db.Column(db.Text)  # JSON com dados do cliente da API
    intent_detected = db.Column(db.String(100))  # Intenção detectada pela IA
    last_ai_action = db.Column(db.String(100))  # Última ação executada pela IA
    last_user_message_at = db.Column(db.DateTime)  # Timestamp da última mensagem do usuário
    
    # Campos legados (mantidos para compatibilidade)
    cpf_status = db.Column(db.String(20))  # APPROVED ou PENDING da API Recoverify
    original_cpf = db.Column(db.String(20))  # CPF original digitado pelo usuário
    question_count = db.Column(db.Integer, default=0)  # Contador de perguntas OpenAI
    
    # Controle de IA
    ai_enabled = db.Column(db.Boolean, default=True)  # Se IA está ativa para esta conversa
    escalation_reason = db.Column(db.String(200))  # Motivo de transferência para humano
    
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)
    
    @staticmethod
    def get_or_create(phone_number: str):
        """Busca ou cria estado de conversa"""
        state = ConversationState.query.filter_by(phone_number=phone_number).first()
        if not state:
            state = ConversationState(phone_number=phone_number)
            db.session.add(state)
            db.session.commit()
        return state
    
    def update_state(self, new_state: str, context_data: str = None, client_data: str = None):
        """Atualiza estado da conversa com contexto de IA"""
        self.current_state = new_state
        if context_data:
            self.context_data = context_data
        if client_data:
            self.client_data = client_data
        self.updated_at = brasilia_now()
        db.session.commit()
    
    def set_ai_context(self, intent: str = None, action: str = None, context: dict = None):
        """Define contexto de IA para a conversa"""
        import json
        
        if intent:
            self.intent_detected = intent
        if action:
            self.last_ai_action = action
        if context:
            self.context_data = json.dumps(context, ensure_ascii=False)
        
        self.last_user_message_at = brasilia_now()
        self.updated_at = brasilia_now()
        db.session.commit()
    
    def get_context_dict(self):
        """Retorna contexto como dicionário"""
        import json
        try:
            return json.loads(self.context_data) if self.context_data else {}
        except:
            return {}
    
    def disable_ai(self, reason: str = None):
        """Desabilita IA e transfere para humano"""
        self.ai_enabled = False
        self.current_state = 'human_handoff'
        if reason:
            self.escalation_reason = reason
        self.updated_at = brasilia_now()
        db.session.commit()
    
    def is_ai_conversation(self) -> bool:
        """Verifica se conversa deve ser processada por IA"""
        return self.ai_enabled and self.current_state not in ['human_handoff', 'closed']
    
    def clear_state(self):
        """Limpa estado da conversa"""
        db.session.delete(self)
        db.session.commit()

class Proxy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    proxy_string = db.Column(db.String(500), nullable=False)  # format: host:port:user:pass
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    success_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)
    
    @staticmethod
    def get_active_proxies():
        """Get all active proxies - MUST be called within Flask app context"""
        return Proxy.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_next_proxy():
        """Get next proxy for rotation - MUST be called within Flask app context"""
        proxies = Proxy.get_active_proxies()
        if not proxies:
            return None
        
        # Find least recently used proxy - DO NOT commit here, let service handle it
        return min(proxies, key=lambda p: p.last_used or datetime.min)
    
    def parse_proxy_string(self):
        """Parse proxy string into components"""
        try:
            parts = self.proxy_string.split(':')
            if len(parts) >= 4:
                return {
                    'host': parts[0],
                    'port': int(parts[1]),
                    'username': parts[2],
                    'password': parts[3]
                }
        except:
            pass
        return None
    
    def get_requests_proxy_dict(self):
        """Get proxy in format for requests library"""
        parsed = self.parse_proxy_string()
        if parsed:
            proxy_url = f"http://{parsed['username']}:{parsed['password']}@{parsed['host']}:{parsed['port']}"
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        return None
    
    def increment_success(self):
        """Increment success counter"""
        self.success_count += 1
        self.last_used = brasilia_now()
        db.session.commit()
    
    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1
        db.session.commit()

class DeliveryPartner(db.Model):
    """Modelo para armazenar dados de entregadores Shopee da API Recoveryfy"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    
    # Dados pessoais da API
    cpf = db.Column(db.String(20), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(300))
    telefone = db.Column(db.String(20))
    data_nascimento = db.Column(db.String(20))
    
    # Dados de endereço
    cidade = db.Column(db.String(100))
    estado = db.Column(db.String(10))
    cep = db.Column(db.String(20))
    bairro = db.Column(db.String(200))
    logradouro = db.Column(db.String(500))
    
    # Dados do veículo
    placa = db.Column(db.String(20))
    tipo_veiculo = db.Column(db.String(50))
    veiculo_ano = db.Column(db.String(10))
    veiculo_cor = db.Column(db.String(50))
    veiculo_marca = db.Column(db.String(100))
    veiculo_modelo = db.Column(db.String(100))
    veiculo_chassi = db.Column(db.String(50))
    veiculo_ano_modelo = db.Column(db.String(10))
    
    # Outros dados
    tamanho_luva = db.Column(db.String(10))
    numero_calcado = db.Column(db.String(10))
    tamanho_colete = db.Column(db.String(10))
    carro_alugado = db.Column(db.String(50))
    
    # Status e confirmações
    confirmed_personal_data = db.Column(db.Boolean, default=False)
    confirmed_vehicle_data = db.Column(db.Boolean, default=False)
    registration_approved = db.Column(db.Boolean, default=False)
    
    # Dados da API original
    recoveryfy_id = db.Column(db.Integer)
    api_response = db.Column(db.Text)  # JSON completo da resposta da API
    
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)
    
    @staticmethod
    def create_from_api_data(phone_number: str, conversation_id: int, api_data: dict):
        """Cria entregador a partir dos dados da API Recoveryfy"""
        import json
        
        dados = api_data.get('dados', [{}])[0] if api_data.get('dados') else {}
        endereco = dados.get('endereco', {})
        info_veiculo = dados.get('info_veiculo', {})
        
        partner = DeliveryPartner(
            phone_number=phone_number,
            conversation_id=conversation_id,
            cpf=dados.get('cpf'),
            nome=dados.get('nome'),
            email=dados.get('email'),
            telefone=dados.get('telefone'),
            data_nascimento=dados.get('data_nascimento'),
            cidade=dados.get('cidade'),
            estado=dados.get('estado'),
            cep=dados.get('cep'),
            bairro=endereco.get('bairro'),
            logradouro=endereco.get('logradouro'),
            placa=dados.get('placa'),
            tipo_veiculo=dados.get('tipo_veiculo'),
            veiculo_ano=info_veiculo.get('ano'),
            veiculo_cor=info_veiculo.get('cor'),
            veiculo_marca=info_veiculo.get('marca'),
            veiculo_modelo=info_veiculo.get('modelo'),
            veiculo_chassi=info_veiculo.get('chassi'),
            veiculo_ano_modelo=info_veiculo.get('anoModelo'),
            tamanho_luva=dados.get('tamanho_luva'),
            numero_calcado=dados.get('numero_calcado'),
            tamanho_colete=dados.get('tamanho_colete'),
            carro_alugado=dados.get('carro_alugado'),
            recoveryfy_id=dados.get('id'),
            api_response=json.dumps(api_data, ensure_ascii=False)
        )
        
        db.session.add(partner)
        db.session.commit()
        return partner
    
    @staticmethod
    def get_by_phone(phone_number: str):
        """Busca entregador por telefone"""
        return DeliveryPartner.query.filter_by(phone_number=phone_number).first()

class ScheduledMessage(db.Model):
    """Modelo para mensagens agendadas - sistema persistente para alta concorrência"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    whatsapp_phone_id = db.Column(db.String(50), nullable=False)  # Para envio correto
    first_name = db.Column(db.String(100), nullable=False)
    message_type = db.Column(db.String(50), default='urgency_alert')
    message_content = db.Column(db.Text, nullable=False)
    scheduled_for = db.Column(db.DateTime, nullable=False, index=True)
    status = db.Column(db.String(20), default='pending')  # pending, processing, sent, failed
    created_at = db.Column(db.DateTime, default=brasilia_now)
    sent_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    
    # Índice único para prevenir duplicação de agendamentos
    __table_args__ = (
        db.UniqueConstraint('phone_number', 'conversation_id', 'message_type', name='_scheduled_message_unique'),
    )
    
    @staticmethod
    def schedule_urgency_message(phone_number: str, conversation_id: int, first_name: str, whatsapp_phone_id: str, delay_minutes: int = 3):
        """Agendar mensagem de urgência para ser enviada depois de X minutos"""
        from datetime import timedelta
        
        # Calcular horário de envio
        send_time = brasilia_now() + timedelta(minutes=delay_minutes)
        
        # Criar conteúdo da mensagem
        message_content = (
            f"⚠️ *URGENTE {first_name}!*\n\n"
            f"🔥 As vagas de entregador da Shopee na sua região estão se esgotando rapidamente!\n\n"
            f"📋 Apenas os entregadores que se inscreverem no curso de treinamento serão chamados para trabalhar.\n\n"
            f"⏰ *ATENÇÃO:* Se você não realizar o pagamento do treinamento, poderá perder sua vaga definitivamente a qualquer momento!\n\n"
            f"🚨 Não deixe essa oportunidade passar!"
        )
        
        try:
            # Criar registro de agendamento (com proteção contra duplicata)
            scheduled = ScheduledMessage(
                phone_number=phone_number,
                conversation_id=conversation_id,
                whatsapp_phone_id=whatsapp_phone_id,
                first_name=first_name,
                message_type='urgency_alert',
                message_content=message_content,
                scheduled_for=send_time
            )
            
            db.session.add(scheduled)
            db.session.commit()
            
            logging.info(f"📅 Mensagem de urgência agendada para {phone_number} às {send_time.strftime('%H:%M:%S')}")
            return scheduled
            
        except db.IntegrityError:
            # Já existe agendamento para este usuário
            db.session.rollback()
            logging.info(f"⚠️ Agendamento já existe para {phone_number}")
            return None
        except Exception as e:
            db.session.rollback()
            logging.error(f"Erro ao agendar mensagem para {phone_number}: {str(e)}")
            return None
    
    @staticmethod
    def get_and_claim_pending_messages():
        """Buscar e reivindicar mensagens pendentes atomicamente (previne duplicação)"""
        now = brasilia_now()
        # Selecionar mensagens pendentes e marcar como processing atomicamente
        messages = db.session.query(ScheduledMessage).filter(
            ScheduledMessage.status == 'pending',
            ScheduledMessage.scheduled_for <= now
        ).with_for_update(skip_locked=True).limit(50).all()
        
        # Marcar como processing imediatamente
        for msg in messages:
            msg.status = 'processing'
        
        if messages:
            db.session.commit()
            
        return messages
    
    def mark_as_sent(self, message_id: str = None):
        """Marcar mensagem como enviada"""
        self.status = 'sent'
        self.sent_at = brasilia_now()
        if message_id:
            self.error_message = f"WhatsApp ID: {message_id}"
        db.session.commit()
    
    def mark_as_failed(self, error: str):
        """Marcar mensagem como falha"""
        self.status = 'failed'
        self.error_message = error
        db.session.commit()

class PendingClient(db.Model):
    """Modelo para rastrear clientes PENDING e follow-up automático"""
    id = db.Column(db.Integer, primary_key=True)
    cpf = db.Column(db.String(20), unique=True, nullable=False, index=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    first_name = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(200))
    
    # Status de pagamento da API Recoverify
    payment_status = db.Column(db.String(20), default='PENDING', index=True)  # PENDING, APPROVED
    last_checked_at = db.Column(db.DateTime, default=brasilia_now, index=True)
    
    # Controle de mensagens de follow-up
    first_followup_sent = db.Column(db.Boolean, default=False)
    first_followup_sent_at = db.Column(db.DateTime)
    daily_followup_sent = db.Column(db.Boolean, default=False)
    daily_followup_sent_at = db.Column(db.DateTime)
    
    # Dados adicionais do cliente
    client_data = db.Column(db.Text)  # JSON com dados completos da API
    
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)
    
    @staticmethod
    def add_pending_client(cpf: str, phone_number: str, first_name: str, full_name: str = None, client_data: str = None):
        """Adicionar ou atualizar cliente PENDING"""
        try:
            # Verificar se já existe
            existing = PendingClient.query.filter_by(cpf=cpf).first()
            
            if existing:
                # Atualizar dados se mudaram
                existing.phone_number = phone_number
                existing.first_name = first_name
                if full_name:
                    existing.full_name = full_name
                if client_data:
                    existing.client_data = client_data
                existing.updated_at = brasilia_now()
                db.session.commit()
                return existing
            else:
                # Criar novo registro
                client = PendingClient(
                    cpf=cpf,
                    phone_number=phone_number,
                    first_name=first_name,
                    full_name=full_name,
                    client_data=client_data
                )
                db.session.add(client)
                db.session.commit()
                return client
                
        except Exception as e:
            db.session.rollback()
            import logging
            logging.error(f"Erro ao adicionar cliente PENDING {cpf}: {str(e)}")
            return None
    
    @staticmethod
    def get_clients_for_check():
        """Buscar clientes PENDING que precisam ser verificados"""
        from datetime import timedelta
        five_minutes_ago = brasilia_now() - timedelta(minutes=5)
        
        return PendingClient.query.filter(
            PendingClient.payment_status == 'PENDING',
            db.or_(
                PendingClient.last_checked_at.is_(None),  # Novos clientes nunca verificados
                PendingClient.last_checked_at < five_minutes_ago  # Clientes não verificados há 5+ min
            )
        ).all()
    
    @staticmethod
    def get_clients_for_first_followup():
        """Buscar clientes que precisam receber primeira mensagem de follow-up"""
        return PendingClient.query.filter(
            PendingClient.payment_status == 'PENDING',
            PendingClient.first_followup_sent == False
        ).all()
    
    @staticmethod
    def get_clients_for_daily_followup():
        """Buscar clientes que precisam receber mensagem diária (12:00)"""
        from datetime import date
        today = date.today()
        
        # Clientes que ainda não receberam a mensagem diária de hoje
        return PendingClient.query.filter(
            PendingClient.payment_status == 'PENDING',
            db.or_(
                PendingClient.daily_followup_sent == False,
                db.func.date(PendingClient.daily_followup_sent_at) < today
            )
        ).all()
    
    def update_payment_status(self, new_status: str):
        """Atualizar status de pagamento"""
        self.payment_status = new_status
        self.last_checked_at = brasilia_now()
        self.updated_at = brasilia_now()
        db.session.commit()
    
    def mark_first_followup_sent(self):
        """Marcar primeira mensagem de follow-up como enviada"""
        self.first_followup_sent = True
        self.first_followup_sent_at = brasilia_now()
        self.updated_at = brasilia_now()
        db.session.commit()
    
    def mark_daily_followup_sent(self):
        """Marcar mensagem diária como enviada"""
        self.daily_followup_sent = True
        self.daily_followup_sent_at = brasilia_now()
        self.updated_at = brasilia_now()
        db.session.commit()

class SystemConfig(db.Model):
    """Configurações globais do sistema para persistência entre sessões"""
    id = db.Column(db.Integer, primary_key=True)
    config_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    config_value = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=brasilia_now)
    updated_at = db.Column(db.DateTime, default=brasilia_now, onupdate=brasilia_now)
    
    @staticmethod
    def set_config(key: str, value: str):
        """Define ou atualiza uma configuração"""
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            config.config_value = value
            config.updated_at = brasilia_now()
        else:
            config = SystemConfig(config_key=key, config_value=value)
            db.session.add(config)
        db.session.commit()
        return config
    
    @staticmethod
    def get_config(key: str, default=None):
        """Busca uma configuração"""
        config = SystemConfig.query.filter_by(config_key=key).first()
        return config.config_value if config else default
    
    @staticmethod
    def delete_config(key: str):
        """Remove uma configuração"""
        config = SystemConfig.query.filter_by(config_key=key).first()
        if config:
            db.session.delete(config)
            db.session.commit()
            return True
        return False