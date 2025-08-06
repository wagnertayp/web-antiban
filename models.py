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