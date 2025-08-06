import logging
import time
import gc
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from models import Campaign, Message

class MessageService:
    """Service for managing message campaigns"""
    
    def __init__(self, db, whatsapp_service, app=None):
        self.db = db
        self.whatsapp_service = whatsapp_service
        self.app = app
    
    def create_campaign(self, leads: List[Dict], template_name: str, buttons: List[Dict]) -> int:
        """Create a new message campaign"""
        try:
            # Create campaign record with template name
            campaign = Campaign(
                template=template_name,  # Store template name instead of content
                buttons=buttons,
                total_leads=len(leads),
                status='pending'
            )
            
            self.db.session.add(campaign)
            self.db.session.flush()  # Get the campaign ID
            
            # Create message records for each lead
            for lead in leads:
                # For template-based messages, store template name and lead data
                # Variables will be filled by WhatsApp Business API during sending
                
                # Process buttons for personalization
                personalized_buttons = []
                for button in buttons:
                    button_copy = button.copy()
                    if button_copy.get('url'):
                        # Support old format
                        button_copy['url'] = button_copy['url'].replace('{nome}', lead.get('nome', ''))
                        button_copy['url'] = button_copy['url'].replace('{cpf}', lead.get('cpf', ''))
                        button_copy['url'] = button_copy['url'].replace('{numero}', lead.get('numero', ''))
                        # Support new format
                        button_copy['url'] = button_copy['url'].replace('{{customer_name}}', lead.get('nome', ''))
                        button_copy['url'] = button_copy['url'].replace('{{cpf}}', lead.get('cpf', ''))
                        button_copy['url'] = button_copy['url'].replace('{{numero}}', lead.get('numero', ''))
                    personalized_buttons.append(button_copy)
                
                message = Message(
                    campaign_id=campaign.id,
                    phone_number=lead['numero'],
                    lead_name=lead.get('nome', ''),
                    lead_cpf=lead.get('cpf', ''),
                    message_text=template_name,  # Store template name instead of processed text
                    buttons=personalized_buttons
                )
                
                self.db.session.add(message)
            
            self.db.session.commit()
            logging.info(f"Created campaign {campaign.id} with {len(leads)} messages")
            return campaign.id
        
        except Exception as e:
            self.db.session.rollback()
            logging.error(f"Error creating campaign: {str(e)}")
            raise
    
    def send_campaign_messages(self, campaign_id: int):
        """Send all messages in a campaign"""
        try:
            campaign = Campaign.query.get(campaign_id)
            if not campaign:
                logging.error(f"Campaign {campaign_id} not found")
                return
            
            campaign.status = 'sending'
            self.db.session.commit()
            
            # Get pending messages
            messages = Message.query.filter_by(
                campaign_id=campaign_id,
                status='pending'
            ).all()
            
            success_count = 0
            error_count = 0
            
            # ULTRA HIGH-SPEED SEQUENTIAL PROCESSING - MAXIMUM VELOCITY
            logging.info(f"Starting ULTRA HIGH-SPEED sequential processing for {len(messages)} messages...")
            
            # Process messages sequentially at maximum speed (no delays)
            for idx, message in enumerate(messages):
                try:
                    # Extract customer name and CPF for template parameters
                    customer_name = message.lead_name or 'Cliente'
                    customer_cpf = message.lead_cpf or 'N/A'
                    template_name = message.message_text  # Template name is stored in message_text
                    
                    # Send template message with correct parameters
                    if template_name == 'modelo_3':
                        # modelo_3 is in English with numbered parameters + button parameter
                        success, response = self.whatsapp_service.send_template_message_with_button(
                            message.phone_number,
                            template_name,
                            'en',
                            [customer_name, customer_cpf],  # {{1}} = Nome, {{2}} = CPF
                            customer_cpf  # Button parameter
                        )
                    elif template_name == 'modelo_4':
                        # modelo_4 - try English first like modelo_3
                        success, response = self.whatsapp_service.send_template_message_with_button(
                            message.phone_number,
                            template_name,
                            'en',  # Try English like modelo_3
                            [customer_name, customer_cpf],  # {{1}} = Nome, {{2}} = CPF
                            customer_cpf  # Button parameter
                        )
                    elif template_name == 'receita1':
                        # receita1 is in pt_BR with named parameters
                        success, response = self.whatsapp_service.send_template_message(
                            message.phone_number,
                            template_name,
                            'pt_BR',
                            [customer_name, customer_cpf]  # customer_name, cpf
                        )
                    else:
                        # Default: numbered parameters - template "elian_template_1753921883_6348f154" expects Nome first, CPF second
                        success, response = self.whatsapp_service.send_template_message(
                            message.phone_number,
                            template_name,
                            'en',  # Most templates are in English
                            [customer_name, customer_cpf]  # {{1}} = Nome, {{2}} = CPF
                        )
                    
                    if success:
                        message.status = 'sent'
                        message.sent_at = datetime.utcnow()
                        message.whatsapp_message_id = response.get('messageId')
                        success_count += 1
                    else:
                        message.status = 'failed'
                        message.error_message = response.get('error', 'Erro desconhecido')
                        error_count += 1
                    
                    # Update campaign progress every 50 messages for real-time feedback
                    if (idx + 1) % 50 == 0:
                        campaign.sent_count = success_count + error_count
                        campaign.success_count = success_count
                        campaign.error_count = error_count
                        self.db.session.commit()
                        logging.info(f"ULTRA SPEED: {idx + 1}/{len(messages)} messages processed")
                        
                except Exception as e:
                    message.status = 'failed'
                    message.error_message = str(e)
                    error_count += 1
                    logging.error(f"Exception processing message to {message.phone_number}: {str(e)}")
                
            logging.info(f"ULTRA HIGH-SPEED processing completed: {success_count} success, {error_count} errors")
            
            # Final update and completion
            campaign.sent_count = success_count + error_count
            campaign.success_count = success_count
            campaign.error_count = error_count
            campaign.status = 'completed'
            campaign.completed_at = datetime.utcnow()
            self.db.session.commit()
            
            logging.info(f"Campaign {campaign_id} completed: {success_count} success, {error_count} errors out of {len(messages)} total messages")
        
        except Exception as e:
            try:
                # Mark campaign as failed
                campaign = Campaign.query.get(campaign_id)
                if campaign:
                    campaign.status = 'failed'
                    self.db.session.commit()
            except Exception as db_error:
                logging.error(f"Error updating campaign status: {str(db_error)}")
            
            logging.error(f"Error processing campaign {campaign_id}: {str(e)}")
    
    def _send_message_parallel(self, message):
        """Helper method to send a single message in parallel with Flask context"""
        if not self.app:
            # Fallback: send without Flask context (won't update database in parallel)
            return self._send_message_without_context(message)
            
        # Use Flask application context for database operations
        with self.app.app_context():
            try:
                # Extract customer name and CPF for template parameters
                customer_name = message.lead_name or 'Cliente'
                customer_cpf = message.lead_cpf or 'N/A'
                template_name = message.message_text  # Template name is stored in message_text
                
                # Send template message with correct parameters
                # Configure language and parameters based on template
                if template_name == 'receita1':
                    # receita1 is in pt_BR with named parameters
                    success, response = self.whatsapp_service.send_template_message(
                        message.phone_number,
                        template_name,
                        'pt_BR',
                        [customer_name, customer_cpf]  # customer_name, cpf
                    )
                elif template_name == 'modelo_3':
                    # modelo_3 is in English with numbered parameters + button parameter
                    success, response = self.whatsapp_service.send_template_message_with_button(
                        message.phone_number,
                        template_name,
                        'en',
                        [customer_name, customer_cpf],  # {{1}} = Nome, {{2}} = CPF
                        customer_cpf  # Button parameter
                    )
                else:
                    # Default: numbered parameters - template "elian_template_1753921883_6348f154" expects Nome first, CPF second
                    success, response = self.whatsapp_service.send_template_message(
                        message.phone_number,
                        template_name,
                        'en',  # Most templates are in English
                        [customer_name, customer_cpf]  # {{1}} = Nome, {{2}} = CPF
                    )
                
                # Fallback to text message if template still fails
                if not success:
                    logging.info(f"Template failed for {message.phone_number}, using text fallback: {response}")
                    text_message = f"Olá {customer_name}, me chamo Sayonara Palloma e sou tabeliã do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF *{customer_cpf}.*\n\nPara evitar restrições ou bloqueios futuros, orientamos que verifique sua situação e regularize imediatamente.\n\nAtenciosamente,\nCartório 5º Ofício de Notas"
                    success, response = self.whatsapp_service.send_text_message(
                        message.phone_number,
                        text_message
                    )
                
                return success, response
                
            except Exception as e:
                logging.error(f"Error in parallel message sending for {message.phone_number}: {str(e)}")
                return False, {'error': str(e)}
    
    def _send_message_without_context(self, message):
        """Send message without Flask context (fallback method)"""
        try:
            # Extract customer name and CPF for template parameters
            customer_name = message.lead_name or 'Cliente'
            customer_cpf = message.lead_cpf or 'N/A'
            template_name = message.message_text  # Template name is stored in message_text
            
            # Send only via WhatsApp API (no database operations)
            if template_name == 'modelo_3':
                success, response = self.whatsapp_service.send_template_message_with_button(
                    message.phone_number,
                    template_name,
                    'en',
                    [customer_name, customer_cpf],  # {{1}} = Nome, {{2}} = CPF
                    customer_cpf  # Button parameter
                )
            else:
                success, response = self.whatsapp_service.send_template_message(
                    message.phone_number,
                    template_name,
                    'en',  # Most templates are in English
                    [customer_name, customer_cpf]  # {{1}} = Nome, {{2}} = CPF
                )
            
            return success, response
            
        except Exception as e:
            logging.error(f"Error sending message without context for {message.phone_number}: {str(e)}")
            return False, {'error': str(e)}
    
    def get_campaign_status(self, campaign_id: int) -> Optional[Dict]:
        """Get campaign status and progress"""
        try:
            campaign = Campaign.query.get(campaign_id)
            if not campaign:
                return None
            
            # Get message status breakdown
            message_stats = self.db.session.query(
                Message.status,
                self.db.func.count(Message.id)
            ).filter_by(campaign_id=campaign_id).group_by(Message.status).all()
            
            status_counts = {status: count for status, count in message_stats}
            
            # Calculate progress percentage
            progress = 0
            if campaign.total_leads > 0:
                progress = int((campaign.sent_count / campaign.total_leads) * 100)
            
            return {
                'id': campaign.id,
                'status': campaign.status,
                'total_leads': campaign.total_leads,
                'sent_count': campaign.sent_count,
                'success_count': campaign.success_count,
                'error_count': campaign.error_count,
                'progress': progress,
                'created_at': campaign.created_at.isoformat() if campaign.created_at else None,
                'completed_at': campaign.completed_at.isoformat() if campaign.completed_at else None,
                'message_status': status_counts
            }
        
        except Exception as e:
            logging.error(f"Error getting campaign status: {str(e)}")
            return None
    
    def get_campaign_messages(self, campaign_id: int, status: Optional[str] = None) -> List[Dict]:
        """Get messages from a campaign"""
        try:
            query = Message.query.filter_by(campaign_id=campaign_id)
            
            if status:
                query = query.filter_by(status=status)
            
            messages = query.all()
            
            return [{
                'id': msg.id,
                'phone_number': msg.phone_number,
                'lead_name': msg.lead_name,
                'status': msg.status,
                'error_message': msg.error_message,
                'sent_at': msg.sent_at.isoformat() if msg.sent_at else None,
                'delivered_at': msg.delivered_at.isoformat() if msg.delivered_at else None
            } for msg in messages]
        
        except Exception as e:
            logging.error(f"Error getting campaign messages: {str(e)}")
            return []
