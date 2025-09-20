from app import db
from datetime import datetime
import time
from typing import Optional

class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(50), unique=True, nullable=False)
    total_leads = db.Column(db.Integer, default=0)
    sent_count = db.Column(db.Integer, default=0)
    failed_count = db.Column(db.Integer, default=0)
    progress = db.Column(db.Float, default=0.0)
    status = db.Column(db.String(20), default='processing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Z-API specific fields
    api_response = db.Column(db.Text)
    delivery_status = db.Column(db.String(50))

class SentNumber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_number = db.Column(db.String(20), nullable=False, index=True)
    lead_name = db.Column(db.String(100))
    lead_cpf = db.Column(db.String(20))
    message_id = db.Column(db.String(200))
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacionamentos
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, 
                              foreign_keys='ChatMessage.conversation_id', 
                              order_by='ChatMessage.created_at')
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
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
        
        now = datetime.utcnow()
        if status == 'sent':
            self.sent_at = now
        elif status == 'delivered':
            self.delivered_at = now
        elif status == 'read':
            self.read_at = now
        
        db.session.commit()

class Proxy(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    proxy_string = db.Column(db.String(500), nullable=False)  # format: host:port:user:pass
    is_active = db.Column(db.Boolean, default=True)
    last_used = db.Column(db.DateTime)
    success_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
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
        self.last_used = datetime.utcnow()
        db.session.commit()
    
    def increment_error(self):
        """Increment error counter"""
        self.error_count += 1
        db.session.commit()