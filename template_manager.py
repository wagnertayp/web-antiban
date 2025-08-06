"""
WhatsApp Business API Template Manager
This module helps create and manage message templates for WhatsApp Business API
"""

import os
import requests
import logging
from typing import Dict, List, Optional

class TemplateManager:
    """Manage WhatsApp Business API message templates"""
    
    def __init__(self):
        self.access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
        self.business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')  # Need this for template creation
        self.api_version = 'v18.0'
        self.base_url = f'https://graph.facebook.com/{self.api_version}'
        
        if self.access_token:
            self.headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
        else:
            self.headers = {}
    
    def create_template(self, name: str, category: str, language: str, body_text: str, 
                       parameters: List[str] = None) -> Dict:
        """
        Create a new message template
        
        Args:
            name: Template name (lowercase, underscores only)
            category: MARKETING, UTILITY, or AUTHENTICATION
            language: Language code (e.g., 'pt_BR', 'en_US')
            body_text: Template text with {{1}}, {{2}} placeholders
            parameters: List of parameter names for documentation
        """
        if not self.business_account_id:
            return {
                'success': False,
                'error': 'WHATSAPP_BUSINESS_ACCOUNT_ID não configurado'
            }
        
        try:
            # Build components for the template
            components = [
                {
                    "type": "BODY",
                    "text": body_text
                }
            ]
            
            # Add parameter format if parameters provided
            parameter_format = "TEXT" if parameters else None
            
            template_data = {
                "name": name,
                "category": category,
                "language": language,
                "components": components
            }
            
            if parameter_format:
                template_data["parameter_format"] = parameter_format
            
            url = f"{self.base_url}/{self.business_account_id}/message_templates"
            response = requests.post(url, json=template_data, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'template_id': data.get('id'),
                    'status': data.get('status', 'PENDING'),
                    'message': 'Template criado com sucesso. Aguarde aprovação do Facebook.'
                }
            else:
                error_data = response.json() if response.content else {}
                return {
                    'success': False,
                    'error': f'Erro HTTP {response.status_code}',
                    'details': error_data.get('error', {}).get('message', response.text)
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error creating template: {str(e)}")
            return {
                'success': False,
                'error': f'Erro de conexão: {str(e)}'
            }
    
    def list_templates(self) -> Dict:
        """List all message templates"""
        if not self.business_account_id:
            return {
                'success': False,
                'error': 'WHATSAPP_BUSINESS_ACCOUNT_ID não configurado'
            }
        
        try:
            url = f"{self.base_url}/{self.business_account_id}/message_templates"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'templates': data.get('data', [])
                }
            else:
                return {
                    'success': False,
                    'error': f'Erro HTTP {response.status_code}: {response.text}'
                }
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error listing templates: {str(e)}")
            return {
                'success': False,
                'error': f'Erro de conexão: {str(e)}'
            }
    
    def get_template_guide(self) -> Dict:
        """Get guide for creating templates based on user's message"""
        return {
            'template_name': 'cartorio_receita_inconsistencia',
            'category': 'UTILITY',
            'language': 'pt_BR',
            'body_text': 'Olá {{1}}, me chamo Sayonara Palloma e sou tabeliã do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF *{{2}}.* Para evitar restrições ou bloqueios futuros, orientamos que verifique sua situação e regularize imediatamente. Atenciosamente, Cartório 5º Ofício de Notas',
            'parameters': [
                'customer_name',  # {{1}}
                'cpf'            # {{2}}
            ],
            'example_values': [
                'João Silva',
                '123.456.789-01'
            ],
            'instructions': [
                '1. Acesse Facebook Business Manager',
                '2. Vá para WhatsApp Manager > Message Templates',
                '3. Clique em "Create Template"',
                '4. Use os dados fornecidos acima',
                '5. Aguarde aprovação (24-48h)',
                '6. Template aprovado pode ser usado para envio em massa'
            ]
        }

# Template creation helper for the user's specific message
def get_cartorio_template_config():
    """Get the exact template configuration for the user's Cartório message"""
    return {
        "name": "cartorio_receita_inconsistencia",
        "category": "UTILITY",
        "language": "pt_BR",
        "components": [
            {
                "type": "BODY",
                "text": "Olá {{1}}, me chamo Sayonara Palloma e sou tabeliã do Cartório 5º Ofício de Notas. Consta em nossos registros uma inconsistência relacionada à sua declaração de Imposto de Renda, vinculada ao CPF *{{2}}.* Para evitar restrições ou bloqueios futuros, orientamos que verifique sua situação e regularize imediatamente. Atenciosamente, Cartório 5º Ofício de Notas",
                "example": {
                    "body_text": [
                        [
                            {
                                "text": "João Silva"
                            },
                            {
                                "text": "123.456.789-01"
                            }
                        ]
                    ]
                }
            }
        ]
    }