import os
import requests
import logging
from typing import Dict, List, Optional, Tuple

class ZAPIService:
    """Service for Z-API WhatsApp integration"""
    
    def __init__(self):
        self.instance_id = os.getenv('ZAPI_INSTANCE_ID')
        self.token = os.getenv('ZAPI_TOKEN')
        self.client_token = os.getenv('ZAPI_CLIENT_TOKEN')
        self.base_url = f'https://api.z-api.io/instances/{self.instance_id}/token/{self.token}'
        
        if self.instance_id and self.token and self.client_token:
            self.headers = {
                'Client-Token': self.client_token,
                'Content-Type': 'application/json'
            }
            logging.info("Z-API service initialized successfully")
        else:
            logging.warning("Z-API credentials not found in environment variables")
    
    def is_configured(self) -> bool:
        """Check if Z-API is properly configured"""
        return bool(self.instance_id and self.token and self.client_token)
    
    def test_connection(self) -> Dict:
        """Test Z-API connection and status"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Z-API não configurada. Configure ZAPI_INSTANCE_ID e ZAPI_TOKEN'
            }
        
        try:
            url = f"{self.base_url}/status"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'status': data.get('connected', False),
                    'message': 'Conexão com Z-API estabelecida com sucesso'
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro na API: {response.status_code} - {response.text}'
                }
        
        except requests.RequestException as e:
            logging.error(f"Z-API connection test failed: {str(e)}")
            return {
                'success': False,
                'error': f'Erro de conexão: {str(e)}'
            }
    
    def send_text_message(self, phone: str, message: str) -> Tuple[bool, Dict]:
        """Send simple text message"""
        if not self.is_configured():
            return False, {'error': 'Z-API não configurada'}
        
        try:
            url = f"{self.base_url}/send-text"
            payload = {
                'phone': phone,
                'message': message
            }
            
            logging.info(f"Sending text message to {phone}: {message[:50]}...")
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            logging.info(f"Z-API Text Response Status: {response.status_code}")
            logging.info(f"Z-API Text Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                # Check if the response indicates success
                if data.get('success', True):  # Some APIs return success field
                    return True, data
                else:
                    logging.warning(f"Z-API text returned success=false: {data}")
                    return False, {'error': f'Z-API error: {data.get("message", "Unknown error")}'}
            else:
                return False, {
                    'error': f'Erro HTTP {response.status_code}',
                    'details': response.text
                }
        
        except requests.RequestException as e:
            logging.error(f"Error sending text message: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}
    
    def send_button_message(self, phone: str, message: str, buttons: List[Dict]) -> Tuple[bool, Dict]:
        """Send message with action buttons using Z-API format"""
        if not self.is_configured():
            return False, {'error': 'Z-API não configurada'}
        
        if not buttons:
            # If no buttons, send as simple text
            return self.send_text_message(phone, message)
        
        try:
            url = f"{self.base_url}/send-button-actions"
            
            # Format buttons for Z-API using the correct buttonActions format
            button_actions = []
            for i, button in enumerate(buttons):
                if button.get('type') == 'url' and button.get('url'):
                    button_actions.append({
                        'id': str(i + 1),
                        'type': 'URL',
                        'url': button.get('url'),
                        'label': button.get('text', 'Link')[:25]  # Max 25 chars
                    })
                elif button.get('type') == 'call' and button.get('phone'):
                    button_actions.append({
                        'id': str(i + 1),
                        'type': 'CALL',
                        'phone': button.get('phone'),
                        'label': button.get('text', 'Ligar')[:25]  # Max 25 chars
                    })
                elif button.get('type') == 'reply':
                    button_actions.append({
                        'id': button.get('id', str(i + 1)),
                        'type': 'REPLY',
                        'label': button.get('text', 'Responder')[:25]  # Max 25 chars
                    })
            
            payload = {
                'phone': phone,
                'message': message,
                'buttonActions': button_actions
            }
            
            # Add optional title and footer if specified
            # These can be added later as configurable options
            
            logging.info(f"Sending button message to {phone} with payload: {payload}")
            response = requests.post(url, json=payload, headers=self.headers, timeout=30)
            
            logging.info(f"Z-API Response Status: {response.status_code}")
            logging.info(f"Z-API Response Body: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                # Check if the response indicates success
                if data.get('success', True):  # Some APIs return success field
                    return True, data
                else:
                    logging.warning(f"Z-API returned success=false: {data}")
                    return False, {'error': f'Z-API error: {data.get("message", "Unknown error")}'}
            else:
                # Log the error and fallback to simple text if buttons fail
                logging.warning(f"Button message failed (HTTP {response.status_code}), sending as text: {response.text}")
                return self.send_text_message(phone, message)
        
        except requests.RequestException as e:
            logging.error(f"Error sending button message: {str(e)}")
            # Fallback to simple text
            return self.send_text_message(phone, message)
    
    def get_message_status(self, message_id: str) -> Tuple[bool, Dict]:
        """Get message delivery status"""
        if not self.is_configured():
            return False, {'error': 'Z-API não configurada'}
        
        try:
            url = f"{self.base_url}/message-status/{message_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, {
                    'error': f'Erro HTTP {response.status_code}',
                    'details': response.text
                }
        
        except requests.RequestException as e:
            logging.error(f"Error getting message status: {str(e)}")
            return False, {'error': f'Erro de conexão: {str(e)}'}
