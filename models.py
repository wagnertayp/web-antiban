from app import db
from datetime import datetime, timezone, timedelta
import time
from typing import Optional

# 🇧🇷 TIMEZONE BRASILEIRO
def brasilia_now():
    """Retorna datetime atual no fuso horário de Brasília (UTC-3)"""
    brasil_tz = timezone(timedelta(hours=-3))
    return datetime.now(brasil_tz)

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
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, 
                              foreign_keys='ChatMessage.conversation_id', 
                              order_by='ChatMessage.created_at.desc()')
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
    """Modelo para mensagens bidirecionais"""
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'), nullable=False)
    whatsapp_message_id = db.Column(db.String(200), unique=True)  # ID da mensagem no WhatsApp
    direction = db.Column(db.String(10), nullable=False)  # 'inbound' ou 'outbound'
    message_type = db.Column(db.String(20), default='text')  # text, image, document, etc.
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, read, failed
    
    # Metadados para diferentes tipos de mensagem
    media_url = db.Column(db.String(500))  # Para imagens, documentos, etc.
    media_caption = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=brasilia_now)
    sent_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    read_at = db.Column(db.DateTime)
    
    # Dados do webhook (para inbound)
    webhook_data = db.Column(db.Text)  # JSON completo do webhook
    
    @staticmethod
    def create_inbound(conversation_id: int, whatsapp_message_id: str, content: str, 
                      message_type: str = 'text', webhook_data: str = None):
        """Cria mensagem recebida (inbound)"""
        message = ChatMessage(
            conversation_id=conversation_id,
            whatsapp_message_id=whatsapp_message_id,
            direction='inbound',
            message_type=message_type,
            content=content,
            status='received',
            webhook_data=webhook_data
        )
        db.session.add(message)
        
        # Atualizar conversa
        conversation = Conversation.query.get(conversation_id)
        if conversation:
            conversation.last_message_at = message.created_at
            conversation.unread_count += 1
            conversation.updated_at = message.created_at
        
        db.session.commit()
        return message
    
    @staticmethod
    def create_outbound(conversation_id: int, content: str, message_type: str = 'text'):
        """Cria mensagem enviada (outbound)"""
        message = ChatMessage(
            conversation_id=conversation_id,
            direction='outbound',
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
    """Estado persistente de conversas para automação"""
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    current_state = db.Column(db.String(50), default='initial')  # initial, waiting_cpf, confirming_name, pending_questions, approved_flow
    client_data = db.Column(db.Text)  # JSON com dados do cliente da API
    cpf_status = db.Column(db.String(20))  # APPROVED ou PENDING da API Recoverify
    original_cpf = db.Column(db.String(20))  # CPF original digitado pelo usuário
    question_count = db.Column(db.Integer, default=0)  # Contador de perguntas OpenAI
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
    
    def update_state(self, new_state: str, client_data: str = None):
        """Atualiza estado da conversa"""
        self.current_state = new_state
        if client_data:
            self.client_data = client_data
        self.updated_at = brasilia_now()
        db.session.commit()
    
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