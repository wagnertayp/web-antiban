from app import db
from datetime import datetime
import time

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
        return SentNumber(
            phone_number=phone_number,
            lead_name=lead_name,
            lead_cpf=lead_cpf,
            message_id=message_id
        )

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
        """Get all active proxies"""
        return Proxy.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_next_proxy():
        """Get next proxy for rotation (round-robin)"""
        proxies = Proxy.get_active_proxies()
        if not proxies:
            return None
        
        # Find least recently used proxy
        proxy = min(proxies, key=lambda p: p.last_used or datetime.min)
        proxy.last_used = datetime.utcnow()
        db.session.commit()
        return proxy
    
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